"""Constants for the Schulmanager Online integration."""

DOMAIN = "schulmanager_online"

# Configuration keys
CONF_TOKEN = "token"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_ENABLE_SCRAPING = "enable_scraping"

# API constants
API_BASE_URL = "https://login.schulmanager-online.de/api/calls"
BUNDLE_VERSION = "c2a60433dcd7c3fc6ee1"

# Web scraping URLs
LOGIN_URL = "https://login.schulmanager-online.de/#/login"
HOMEWORK_URL = "https://login.schulmanager-online.de/#/modules/classbook/homework/"
SCHEDULES_URL = "https://login.schulmanager-online.de/#/modules/schedules/view/"

# Update intervals
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
SCRAPING_SCAN_INTERVAL = 900  # 15 minutes (less frequent for web scraping)

# Sensor types
SENSOR_TYPES = {
    "letters": {
        "name": "Letters",
        "icon": "mdi:email",
        "unit": None,
        "device_class": None,
    },
    "unread_letters": {
        "name": "Unread Letters",
        "icon": "mdi:email-outline",
        "unit": None,
        "device_class": None,
    },
    "homework": {
        "name": "Homework",
        "icon": "mdi:book-open-page-variant",
        "unit": None,
        "device_class": None,
    },
    "exams": {
        "name": "Exams",
        "icon": "mdi:clipboard-text",
        "unit": None,
        "device_class": None,
    },
    "appointments": {
        "name": "Appointments",
        "icon": "mdi:calendar",
        "unit": None,
        "device_class": None,
    },
    "timetable": {
        "name": "Timetable",
        "icon": "mdi:timetable",
        "unit": None,
        "device_class": None,
    },
}

# Attributes
ATTR_LETTERS = "letters"
ATTR_HOMEWORK = "homework"
ATTR_EXAMS = "exams"
ATTR_APPOINTMENTS = "appointments"
ATTR_TIMETABLE = "timetable"
ATTR_LAST_UPDATE = "last_update"
ATTR_TOTAL_COUNT = "total_count"
ATTR_UNREAD_COUNT = "unread_count"

