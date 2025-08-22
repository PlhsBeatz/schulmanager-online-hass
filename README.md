# Schulmanager Online Integration für Home Assistant

Diese benutzerdefinierte Integration ermöglicht es, Daten von Schulmanager Online in Home Assistant zu integrieren. Die Integration stellt Sensoren bereit, die Informationen über Briefe, Hausaufgaben, Klausuren, Termine und Stundenpläne anzeigen.

## Funktionen

### Basis-Funktionen (API-basiert)
- **Briefe-Sensor**: Zeigt die Gesamtanzahl der Briefe an
- **Ungelesene Briefe-Sensor**: Zeigt die Anzahl der ungelesenen Briefe an

### Erweiterte Funktionen (Web-Scraping-basiert)
- **Hausaufgaben-Sensor**: Aktuelle und anstehende Hausaufgaben
- **Klausuren-Sensor**: Geplante Klausuren und Prüfungen
- **Termine-Sensor**: Schultermine und Veranstaltungen
- **Stundenplan-Sensor**: Wöchentlicher Stundenplan mit Änderungen

### Allgemeine Funktionen
- **Automatische Updates**: Regelmäßige Aktualisierung der Daten (5-15 Minuten)
- **Benutzerfreundliche Konfiguration**: Einfache Einrichtung über die Home Assistant UI
- **Deutsche Lokalisierung**: Vollständige deutsche Übersetzung
- **HACS-Kompatibilität**: Installation über HACS möglich

## Voraussetzungen

- Home Assistant 2023.1 oder höher
- Gültiger Schulmanager Online Account
- JWS Token von Schulmanager Online (für Basis-Funktionen)
- Benutzername und Passwort (für erweiterte Funktionen)

## Installation

### HACS (Empfohlen)

1. Öffnen Sie HACS in Home Assistant
2. Gehen Sie zu "Integrationen"
3. Klicken Sie auf die drei Punkte oben rechts und wählen Sie "Benutzerdefinierte Repositories"
4. Fügen Sie die Repository-URL hinzu: `https://github.com/your-username/schulmanager-online-hass`
5. Wählen Sie "Integration" als Kategorie
6. Klicken Sie auf "Hinzufügen"
7. Suchen Sie nach "Schulmanager Online" und installieren Sie die Integration
8. Starten Sie Home Assistant neu

### Manuelle Installation

1. Laden Sie die neueste Version von der [Releases-Seite](https://github.com/your-username/schulmanager-online-hass/releases) herunter
2. Extrahieren Sie die ZIP-Datei
3. Kopieren Sie den Ordner `custom_components/schulmanager_online` in Ihr Home Assistant `custom_components` Verzeichnis
4. Starten Sie Home Assistant neu

## Konfiguration

### Schritt 1: JWS Token erhalten

Um den erforderlichen JWS Token zu erhalten:

1. Melden Sie sich bei Schulmanager Online an
2. Öffnen Sie die Entwicklertools Ihres Browsers (F12)
3. Gehen Sie zum "Network" Tab
4. Führen Sie eine Aktion in Schulmanager Online aus (z.B. Briefe öffnen)
5. Suchen Sie nach einem Request zu `/api/calls`
6. Kopieren Sie den `Authorization` Header-Wert (ohne "Bearer ")

### Schritt 2: Integration einrichten

1. Gehen Sie zu "Einstellungen" > "Geräte & Dienste" in Home Assistant
2. Klicken Sie auf "Integration hinzufügen"
3. Suchen Sie nach "Schulmanager Online"
4. Geben Sie Ihren JWS Token ein
5. **Optional**: Aktivieren Sie "Erweiterte Daten aktivieren" für Hausaufgaben, Klausuren, etc.
6. Falls erweiterte Daten aktiviert wurden, geben Sie Benutzername und Passwort ein
7. Klicken Sie auf "Absenden"

## Verfügbare Entitäten

### Basis-Sensoren (immer verfügbar)
- `sensor.schulmanager_online_letters`: Gesamtanzahl der Briefe
- `sensor.schulmanager_online_unread_letters`: Anzahl der ungelesenen Briefe

### Erweiterte Sensoren (nur bei aktiviertem Web-Scraping)
- `sensor.schulmanager_online_homework`: Anzahl der Hausaufgaben
- `sensor.schulmanager_online_exams`: Anzahl der geplanten Klausuren
- `sensor.schulmanager_online_appointments`: Anzahl der Termine
- `sensor.schulmanager_online_timetable`: Stundenplan-Informationen

### Attribute

Jeder Sensor stellt zusätzliche Attribute bereit:

**Briefe-Sensor:**
- `letters`: Liste aller Briefe mit Details
- `total_count`: Gesamtanzahl der Briefe
- `unread_count`: Anzahl der ungelesenen Briefe

**Hausaufgaben-Sensor:**
- `homework`: Liste aller Hausaufgaben
- `upcoming_homework`: Nur anstehende Hausaufgaben

**Klausuren-Sensor:**
- `exams`: Liste aller Klausuren
- `upcoming_exams`: Nur anstehende Klausuren

**Stundenplan-Sensor:**
- `timetable`: Vollständiger Wochenplan
- `monday`, `tuesday`, etc.: Stundenplan pro Wochentag

## Verwendung in Automationen

### Benachrichtigung bei neuen Briefen
```yaml
automation:
  - alias: "Benachrichtigung bei neuen Briefen"
    trigger:
      - platform: state
        entity_id: sensor.schulmanager_online_unread_letters
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Neue Nachricht von der Schule"
          message: "Sie haben {{ states('sensor.schulmanager_online_unread_letters') }} ungelesene Briefe."
```

### Erinnerung an Hausaufgaben
```yaml
automation:
  - alias: "Hausaufgaben-Erinnerung"
    trigger:
      - platform: time
        at: "18:00:00"
    condition:
      - condition: template
        value_template: "{{ states('sensor.schulmanager_online_homework') | int > 0 }}"
    action:
      - service: notify.family
        data:
          title: "Hausaufgaben-Erinnerung"
          message: "Es sind noch {{ states('sensor.schulmanager_online_homework') }} Hausaufgaben zu erledigen."
```

### Klausur-Vorbereitung
```yaml
automation:
  - alias: "Klausur-Vorbereitung"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: template
        value_template: "{{ state_attr('sensor.schulmanager_online_exams', 'upcoming_exams') | length > 0 }}"
    action:
      - service: notify.student
        data:
          title: "Klausur heute"
          message: "Heute stehen Klausuren an. Viel Erfolg!"
```

## Fehlerbehebung

### Häufige Probleme

**"Ungültige Anmeldedaten" Fehler**
- Überprüfen Sie, ob der JWS Token korrekt kopiert wurde
- Bei Web-Scraping: Überprüfen Sie Benutzername und Passwort
- Stellen Sie sicher, dass die Anmeldedaten noch gültig sind

**"Verbindung zur API fehlgeschlagen"**
- Überprüfen Sie Ihre Internetverbindung
- Stellen Sie sicher, dass Schulmanager Online erreichbar ist
- Prüfen Sie die Home Assistant Logs auf detaillierte Fehlermeldungen

**Web-Scraping funktioniert nicht**
- Stellen Sie sicher, dass Chrome/Chromium installiert ist
- Überprüfen Sie die Logs auf Selenium-Fehler
- Bei wiederholten Problemen: Deaktivieren Sie Web-Scraping temporär

### Logs aktivieren

Um detaillierte Logs zu aktivieren, fügen Sie folgendes zu Ihrer `configuration.yaml` hinzu:

```yaml
logger:
  default: warning
  logs:
    custom_components.schulmanager_online: debug
```

## Performance-Hinweise

- **Web-Scraping**: Verwendet mehr Ressourcen als die API-Integration
- **Update-Intervalle**: Web-Scraping erfolgt alle 15 Minuten, API-Aufrufe alle 5 Minuten
- **Browser-Ressourcen**: Jeder Scraping-Vorgang startet einen temporären Browser

## Sicherheit

- **Token-Speicherung**: Alle Anmeldedaten werden sicher in Home Assistant gespeichert
- **Verschlüsselung**: Alle Verbindungen erfolgen über HTTPS
- **Lokale Verarbeitung**: Web-Scraping erfolgt lokal, keine Daten werden an Dritte weitergegeben

## Beitragen

Beiträge sind willkommen! Bitte lesen Sie die [Beitragsrichtlinien](CONTRIBUTING.md) bevor Sie einen Pull Request erstellen.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

## Haftungsausschluss

Diese Integration ist nicht offiziell von Schulmanager Online unterstützt oder entwickelt. Verwenden Sie sie auf eigene Verantwortung. Web-Scraping kann bei Änderungen der Schulmanager Online Website beeinträchtigt werden.

