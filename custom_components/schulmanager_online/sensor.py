"""Sensor platform for Schulmanager Online."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SchulmanagerOnlineDataUpdateCoordinator
from .const import (
    ATTR_APPOINTMENTS,
    ATTR_EXAMS,
    ATTR_HOMEWORK,
    ATTR_LAST_UPDATE,
    ATTR_LETTERS,
    ATTR_TIMETABLE,
    ATTR_TOTAL_COUNT,
    ATTR_UNREAD_COUNT,
    CONF_ENABLE_SCRAPING,
    DOMAIN,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    scraping_enabled = config_entry.data.get(CONF_ENABLE_SCRAPING, False)

    entities = []
    
    # Always add basic sensors
    entities.extend([
        SchulmanagerOnlineSensor(coordinator, "letters"),
        SchulmanagerOnlineSensor(coordinator, "unread_letters"),
    ])
    
    # Add scraping sensors if enabled
    if scraping_enabled:
        entities.extend([
            SchulmanagerOnlineSensor(coordinator, "homework"),
            SchulmanagerOnlineSensor(coordinator, "exams"),
            SchulmanagerOnlineSensor(coordinator, "appointments"),
            SchulmanagerOnlineSensor(coordinator, "timetable"),
        ])

    async_add_entities(entities)


class SchulmanagerOnlineSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Schulmanager Online sensor."""

    def __init__(
        self,
        coordinator: SchulmanagerOnlineDataUpdateCoordinator,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"Schulmanager Online {SENSOR_TYPES[sensor_type]['name']}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_icon = SENSOR_TYPES[sensor_type]["icon"]
        self._attr_unit_of_measurement = SENSOR_TYPES[sensor_type]["unit"]
        self._attr_device_class = SENSOR_TYPES[sensor_type]["device_class"]

    @property
    def native_value(self) -> Optional[int]:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        if self._sensor_type == "letters":
            return self.coordinator.data.get(ATTR_TOTAL_COUNT, 0)
        elif self._sensor_type == "unread_letters":
            return self.coordinator.data.get(ATTR_UNREAD_COUNT, 0)
        elif self._sensor_type == "homework":
            homework_list = self.coordinator.data.get("homework", [])
            return len(homework_list)
        elif self._sensor_type == "exams":
            exams_list = self.coordinator.data.get("exams", [])
            return len(exams_list)
        elif self._sensor_type == "appointments":
            appointments_list = self.coordinator.data.get("appointments", [])
            return len(appointments_list)
        elif self._sensor_type == "timetable":
            timetable_data = self.coordinator.data.get("timetable", [])
            # Return number of days with lessons
            return len([day for day in timetable_data if day])

        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        attributes = {
            ATTR_LAST_UPDATE: self.coordinator.last_update_success_time,
        }

        if self._sensor_type == "letters":
            attributes[ATTR_LETTERS] = self.coordinator.data.get("letters", [])
            attributes[ATTR_TOTAL_COUNT] = self.coordinator.data.get(ATTR_TOTAL_COUNT, 0)
            attributes[ATTR_UNREAD_COUNT] = self.coordinator.data.get(ATTR_UNREAD_COUNT, 0)
        elif self._sensor_type == "homework":
            homework_list = self.coordinator.data.get("homework", [])
            attributes[ATTR_HOMEWORK] = homework_list
            attributes["upcoming_homework"] = [
                hw for hw in homework_list 
                if hw.get("date", "") >= self._get_today_string()
            ]
        elif self._sensor_type == "exams":
            exams_list = self.coordinator.data.get("exams", [])
            attributes[ATTR_EXAMS] = exams_list
            attributes["upcoming_exams"] = [
                exam for exam in exams_list 
                if exam.get("date", "") >= self._get_today_string()
            ]
        elif self._sensor_type == "appointments":
            attributes[ATTR_APPOINTMENTS] = self.coordinator.data.get("appointments", [])
        elif self._sensor_type == "timetable":
            timetable_data = self.coordinator.data.get("timetable", [])
            attributes[ATTR_TIMETABLE] = timetable_data
            if timetable_data:
                day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                for i, day_schedule in enumerate(timetable_data):
                    if i < len(day_names):
                        attributes[day_names[i]] = day_schedule

        return attributes

    def _get_today_string(self) -> str:
        """Get today's date as YYYY-MM-DD string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

