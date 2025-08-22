# Installationsanleitung - Schulmanager Online Integration

Diese Anleitung führt Sie Schritt für Schritt durch die Installation und Konfiguration der Schulmanager Online Integration für Home Assistant, einschließlich der neuen erweiterten Funktionen.

## Systemanforderungen

Bevor Sie mit der Installation beginnen, stellen Sie sicher, dass Ihr System die folgenden Anforderungen erfüllt:

- **Home Assistant**: Version 2023.1 oder höher
- **Python**: Version 3.9 oder höher (wird normalerweise mit Home Assistant geliefert)
- **Internetverbindung**: Für den Zugriff auf die Schulmanager Online API
- **Schulmanager Online Account**: Gültiger Zugang zu Schulmanager Online
- **Chrome/Chromium**: Für Web-Scraping-Funktionen (wird automatisch installiert)

## Schritt 1: Integration herunterladen

### Option A: HACS Installation (Empfohlen)

HACS (Home Assistant Community Store) ist die einfachste Methode zur Installation benutzerdefinierter Integrationen.

1. **HACS installieren** (falls noch nicht geschehen):
   - Folgen Sie der offiziellen HACS-Installationsanleitung: https://hacs.xyz/docs/setup/download
   - Starten Sie Home Assistant nach der HACS-Installation neu

2. **Repository hinzufügen**:
   - Öffnen Sie HACS in der Home Assistant Seitenleiste
   - Klicken Sie auf "Integrationen"
   - Klicken Sie auf die drei Punkte (⋮) oben rechts
   - Wählen Sie "Benutzerdefinierte Repositories"
   - Geben Sie die Repository-URL ein: `https://github.com/your-username/schulmanager-online-hass`
   - Wählen Sie "Integration" als Kategorie
   - Klicken Sie auf "Hinzufügen"

3. **Integration installieren**:
   - Suchen Sie nach "Schulmanager Online" in HACS
   - Klicken Sie auf die Integration
   - Klicken Sie auf "Herunterladen"
   - Starten Sie Home Assistant neu

### Option B: Manuelle Installation

Falls Sie HACS nicht verwenden möchten, können Sie die Integration manuell installieren.

1. **Dateien herunterladen**:
   - Gehen Sie zur [Releases-Seite](https://github.com/your-username/schulmanager-online-hass/releases)
   - Laden Sie die neueste Version herunter (ZIP-Datei)
   - Extrahieren Sie die ZIP-Datei

2. **Dateien kopieren**:
   - Navigieren Sie zu Ihrem Home Assistant Konfigurationsverzeichnis
   - Erstellen Sie den Ordner `custom_components` falls er nicht existiert
   - Kopieren Sie den gesamten Ordner `schulmanager_online` in `custom_components/`
   - Die finale Struktur sollte so aussehen:
     ```
     config/
     └── custom_components/
         └── schulmanager_online/
             ├── __init__.py
             ├── api.py
             ├── config_flow.py
             ├── const.py
             ├── manifest.json
             ├── scraper.py
             ├── sensor.py
             ├── strings.json
             └── translations/
                 └── de.json
     ```

3. **Home Assistant neu starten**:
   - Starten Sie Home Assistant über "Einstellungen" > "System" > "Neu starten"

## Schritt 2: JWS Token beschaffen

Der JWS (JSON Web Signature) Token ist für die Basis-Funktionen (Briefe) erforderlich.

### Detaillierte Anleitung:

1. **Browser öffnen**:
   - Öffnen Sie einen modernen Webbrowser (Chrome, Firefox, Safari, Edge)
   - Navigieren Sie zu https://login.schulmanager-online.de

2. **Entwicklertools öffnen**:
   - **Chrome/Edge**: Drücken Sie F12 oder Rechtsklick → "Untersuchen"
   - **Firefox**: Drücken Sie F12 oder Rechtsklick → "Element untersuchen"
   - **Safari**: Aktivieren Sie zuerst das Entwicklermenü in den Einstellungen

3. **Network Tab aktivieren**:
   - Klicken Sie auf den "Network" oder "Netzwerk" Tab in den Entwicklertools
   - Stellen Sie sicher, dass die Aufzeichnung aktiviert ist (roter Punkt oder "Record" Button)

4. **Bei Schulmanager Online anmelden**:
   - Geben Sie Ihre Anmeldedaten ein
   - Melden Sie sich erfolgreich an

5. **API-Aufruf auslösen**:
   - Navigieren Sie zu einem Bereich mit Daten (z.B. "Briefe" oder "Nachrichten")
   - Führen Sie eine Aktion aus, die Daten lädt

6. **Token extrahieren**:
   - Suchen Sie in der Network-Liste nach einem Request zu `/api/calls`
   - Klicken Sie auf diesen Request
   - Gehen Sie zum "Headers" Tab
   - Suchen Sie nach dem "Authorization" Header
   - Kopieren Sie den Wert OHNE das Wort "Bearer " (nur den Token-Teil)

### Beispiel:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
Kopieren Sie nur: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Schritt 3: Integration konfigurieren

### Basis-Konfiguration

1. **Integration hinzufügen**:
   - Öffnen Sie Home Assistant
   - Gehen Sie zu "Einstellungen" > "Geräte & Dienste"
   - Klicken Sie auf "+ Integration hinzufügen"
   - Suchen Sie nach "Schulmanager Online"
   - Klicken Sie auf die Integration

2. **Token eingeben**:
   - Fügen Sie den kopierten JWS Token in das Textfeld ein
   - **Optional**: Aktivieren Sie "Erweiterte Daten aktivieren" für zusätzliche Funktionen
   - Klicken Sie auf "Absenden"

### Erweiterte Konfiguration (Optional)

Falls Sie "Erweiterte Daten aktivieren" ausgewählt haben:

3. **Anmeldedaten eingeben**:
   - Geben Sie Ihren Schulmanager Online Benutzernamen ein
   - Geben Sie Ihr Schulmanager Online Passwort ein
   - Klicken Sie auf "Absenden"

4. **Konfiguration abschließen**:
   - Die Integration sollte erfolgreich hinzugefügt werden
   - Sie sehen eine Bestätigung mit den verfügbaren Entitäten

## Schritt 4: Entitäten überprüfen

Nach der erfolgreichen Konfiguration sollten folgende Entitäten verfügbar sein:

### Basis-Entitäten (immer verfügbar):
- `sensor.schulmanager_online_letters`
- `sensor.schulmanager_online_unread_letters`

### Erweiterte Entitäten (nur bei aktiviertem Web-Scraping):
- `sensor.schulmanager_online_homework`
- `sensor.schulmanager_online_exams`
- `sensor.schulmanager_online_appointments`
- `sensor.schulmanager_online_timetable`

### Entitäten finden:
1. Gehen Sie zu "Einstellungen" > "Geräte & Dienste"
2. Suchen Sie nach "Schulmanager Online"
3. Klicken Sie darauf, um alle Entitäten zu sehen

## Schritt 5: Dashboard einrichten (Optional)

Sie können die Sensoren zu Ihrem Dashboard hinzufügen:

1. **Dashboard bearbeiten**:
   - Gehen Sie zu Ihrem Dashboard
   - Klicken Sie auf die drei Punkte oben rechts
   - Wählen Sie "Dashboard bearbeiten"

2. **Karte hinzufügen**:
   - Klicken Sie auf "+ Karte hinzufügen"
   - Wählen Sie "Entitäten" oder "Sensor"
   - Fügen Sie die Schulmanager Online Sensoren hinzu

3. **Karte anpassen**:
   - Passen Sie Titel und Darstellung nach Ihren Wünschen an
   - Speichern Sie die Änderungen

## Fehlerbehebung

### Problem: "Integration nicht gefunden"
**Lösung**: 
- Stellen Sie sicher, dass Home Assistant nach der Installation neu gestartet wurde
- Überprüfen Sie, ob die Dateien im korrekten Verzeichnis liegen
- Prüfen Sie die Home Assistant Logs auf Fehlermeldungen

### Problem: "Ungültige Anmeldedaten"
**Lösung**:
- **Für Token**: Überprüfen Sie, ob der Token vollständig kopiert wurde
- **Für Web-Scraping**: Überprüfen Sie Benutzername und Passwort
- Stellen Sie sicher, dass keine zusätzlichen Leerzeichen vorhanden sind
- Versuchen Sie, neue Anmeldedaten zu generieren

### Problem: "Verbindung fehlgeschlagen"
**Lösung**:
- Überprüfen Sie Ihre Internetverbindung
- Stellen Sie sicher, dass Home Assistant Zugriff auf externe APIs hat
- Prüfen Sie Firewall-Einstellungen
- Testen Sie den Zugriff auf https://login.schulmanager-online.de

### Problem: "Web-Scraping funktioniert nicht"
**Lösung**:
- Überprüfen Sie, ob Chrome/Chromium verfügbar ist
- Prüfen Sie die Logs auf Selenium-spezifische Fehler
- Stellen Sie sicher, dass genügend Systemressourcen verfügbar sind
- Bei wiederholten Problemen: Deaktivieren Sie Web-Scraping temporär

### Logs aktivieren

Für detaillierte Fehlermeldungen fügen Sie folgendes zu Ihrer `configuration.yaml` hinzu:

```yaml
logger:
  default: warning
  logs:
    custom_components.schulmanager_online: debug
    selenium: debug
```

Starten Sie Home Assistant neu und überprüfen Sie die Logs unter "Einstellungen" > "System" > "Logs".

## Performance-Optimierung

### Ressourcenverbrauch
- **Web-Scraping**: Benötigt mehr CPU und Speicher als API-Aufrufe
- **Update-Intervalle**: Automatisch angepasst (API: 5 Min, Scraping: 15 Min)
- **Browser-Instanzen**: Werden nach jedem Scraping-Vorgang geschlossen

### Empfehlungen
- Aktivieren Sie Web-Scraping nur wenn nötig
- Überwachen Sie die Systemlast bei aktiviertem Web-Scraping
- Bei Problemen: Deaktivieren Sie Web-Scraping und nutzen Sie nur die API-Funktionen

## Support

Bei Problemen oder Fragen:

1. Überprüfen Sie die [FAQ](FAQ.md)
2. Suchen Sie in den [GitHub Issues](https://github.com/your-username/schulmanager-online-hass/issues)
3. Erstellen Sie ein neues Issue mit detaillierten Informationen über Ihr Problem

## Nächste Schritte

Nach der erfolgreichen Installation können Sie:

- [Automationen erstellen](AUTOMATIONS.md) für Benachrichtigungen
- [Dashboard-Karten konfigurieren](DASHBOARD.md) für eine bessere Darstellung
- [Erweiterte Konfiguration](ADVANCED.md) für zusätzliche Funktionen

