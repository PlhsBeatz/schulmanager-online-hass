# Changelog

## Version 2.0.0 - Erweiterte Funktionen

### Neue Funktionen
- **Web-Scraping-Unterstützung**: Optionale Aktivierung von Web-Scraping für erweiterte Daten
- **Hausaufgaben-Sensor**: Zeigt aktuelle und anstehende Hausaufgaben an
- **Klausuren-Sensor**: Übersicht über geplante Klausuren und Prüfungen
- **Termine-Sensor**: Anzeige von Schultermine und Veranstaltungen
- **Stundenplan-Sensor**: Wöchentlicher Stundenplan mit Änderungen und Ausfällen
- **Konfigurierbare Datenquellen**: Benutzer können wählen, welche Daten abgerufen werden sollen

### Technische Verbesserungen
- **Selenium-Integration**: Hinzufügung von Selenium WebDriver für Web-Scraping
- **Erweiterte Konfiguration**: Mehrstufiger Konfigurationsprozess für verschiedene Datenquellen
- **Robuste Fehlerbehandlung**: Graceful Degradation bei Scraping-Fehlern
- **Optimierte Update-Intervalle**: Unterschiedliche Aktualisierungsfrequenzen für API und Scraping

### Abhängigkeiten
- **Neue Requirements**: 
  - `selenium>=4.0.0`
  - `webdriver-manager>=3.8.0`
- **Bestehende Requirements**: 
  - `aiohttp>=3.8.0` (unverändert)

### Konfiguration
- **Erweiterte Konfiguration**: Optionale Aktivierung von Web-Scraping-Funktionen
- **Mehrstufiger Setup**: Separate Konfiguration für API-Token und Anmeldedaten
- **Rückwärtskompatibilität**: Bestehende Konfigurationen funktionieren weiterhin

### Sensoren
- `sensor.schulmanager_online_letters` (bestehend)
- `sensor.schulmanager_online_unread_letters` (bestehend)
- `sensor.schulmanager_online_homework` (neu)
- `sensor.schulmanager_online_exams` (neu)
- `sensor.schulmanager_online_appointments` (neu)
- `sensor.schulmanager_online_timetable` (neu)

### Attribute
Jeder neue Sensor bietet detaillierte Attribute:
- **Hausaufgaben**: Liste mit Fach, Aufgabe, Datum
- **Klausuren**: Termine mit Fach, Zeit, Datum
- **Stundenplan**: Wochenplan mit Fach, Lehrer, Raum pro Tag

---

## Version 1.0.0 - Erste Version

### Funktionen
- **Briefe-Sensor**: Anzeige der Gesamtanzahl von Briefen
- **Ungelesene Briefe-Sensor**: Anzahl ungelesener Nachrichten
- **API-Integration**: Direkte Verbindung zur Schulmanager Online API
- **Benutzerfreundliche Konfiguration**: Setup über Home Assistant UI
- **Deutsche Lokalisierung**: Vollständige Übersetzung der Benutzeroberfläche

