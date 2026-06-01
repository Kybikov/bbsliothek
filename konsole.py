# BBSliothek - Konsolen-Anwendung
# Textbasierte Bedienoberfläche für die Lernmaterialverwaltung
# Nutzt datenbank.py für alle Datenbankoperationen

import os
import sys
import datenbank as db
from dotenv import load_dotenv

load_dotenv()

# Aktuell eingeloggter Benutzer
benutzer = None


def trennlinie():
    print("-" * 50)


def tabelle_ausgeben(zeilen):
    if not zeilen:
        print("(keine Ergebnisse)")
        return

    for zeile in zeilen:
        for key, value in zeile.items():
            # blob_inhalt nicht ausgeben - das sind Binärdaten
            if key == "blob_inhalt":
                continue
            print(str(key) + ": " + str(value))
        print("---")

    print(str(len(zeilen)) + " Ergebnis(se)")


# -----------------------------------------------------------------------
# Login
# -----------------------------------------------------------------------

def login():
    global benutzer
    trennlinie()
    print("BBSliothek - Anmelden")
    trennlinie()

    name = input("Benutzername: ").strip()
    passwort = input("Passwort: ").strip()

    if not name or not passwort:
        print("Fehler: Bitte Name und Passwort eingeben!")
        return False

    try:
        ergebnis = db.einloggen(name, passwort)
    except Exception as e:
        print("Fehler bei der Datenbankverbindung: " + str(e))
        return False

    if ergebnis is None:
        print("Falscher Benutzername oder Passwort!")
        return False

    benutzer = ergebnis
    print("Angemeldet als: " + benutzer["anzeigename"] + " (" + benutzer["rolle"] + ")")
    return True


# -----------------------------------------------------------------------
# Material hochladen
# -----------------------------------------------------------------------

def material_hochladen():
    trennlinie()
    print("MATERIAL HOCHLADEN")
    trennlinie()

    pfad = input("Pfad zur Datei: ").strip()
    if not pfad:
        print("Fehler: Kein Pfad angegeben!")
        return

    if not os.path.exists(pfad):
        print("Fehler: Datei nicht gefunden!")
        return

    # Prüfen ob neue Version oder neues Material
    mat_id_eingabe = input("Material-ID für neue Version (leer = neues Material anlegen): ").strip()

    if mat_id_eingabe:
        # Neue Version
        try:
            material_id = int(mat_id_eingabe)
        except ValueError:
            print("Fehler: Keine gültige ID!")
            return

        ergebnis = db.material_hochladen(pfad, benutzer["benutzer_id"], material_id=material_id)
        print("Neue Version gespeichert!")
        print("Material-ID: " + str(ergebnis["material_id"]))
        print("Version: " + str(ergebnis["version"]))
        print("Gespeichert als: " + ergebnis["strategie"])

    else:
        # Neues Material
        titel = input("Titel: ").strip()
        if not titel:
            print("Fehler: Titel darf nicht leer sein!")
            return

        # Themengebiete anzeigen
        themen = db.themen_laden()
        print("\nVerfügbare Themengebiete:")
        for t in themen:
            print(str(t["themengebiet_id"]) + " - " + t["name"])

        thema_eingabe = input("Themengebiet-ID: ").strip()
        try:
            thema_id = int(thema_eingabe)
        except ValueError:
            print("Fehler: Keine gültige Themen-ID!")
            return

        ergebnis = db.material_hochladen(pfad, benutzer["benutzer_id"], titel=titel, thema_id=thema_id)
        print("Material erfolgreich gespeichert!")
        print("Material-ID: " + str(ergebnis["material_id"]))
        print("Version: " + str(ergebnis["version"]))
        print("Gespeichert als: " + ergebnis["strategie"])
        if ergebnis["pfad"]:
            print("Pfad: " + ergebnis["pfad"])


# -----------------------------------------------------------------------
# Materialien suchen
# -----------------------------------------------------------------------

def materialien_suchen():
    while True:
        trennlinie()
        print("SUCHE")
        trennlinie()
        print("1. Freie Suche (Titel, Typ, Thema, Autor)")
        print("2. Standardabfrage 1: Materialien pro Themengebiet")
        print("3. Standardabfrage 2: Durchschnittliche Dateigröße je Thema")
        print("4. Standardabfrage 3: Materialien mit Autoren")
        print("5. Standardabfrage 4: Kommentare mit Material und Autor")
        print("6. Standardabfrage 5: Materialien pro Autor mit Rolle")
        print("7. Standardabfrage 6: Materialien mit Thema und Version")
        print("8. Standardabfrage 7: Vollständige Übersicht")
        print("9. Zurück")
        trennlinie()

        auswahl = input("Auswahl: ").strip()

        if auswahl == "1":
            freie_suche()
        elif auswahl in ["2", "3", "4", "5", "6", "7", "8"]:
            # Index ist auswahl - 2 weil die Liste ab 0 geht
            index = int(auswahl) - 2
            try:
                titel, beschreibung, zeilen = db.standardabfrage_ausfuehren(index)
                print("\n" + titel)
                print(beschreibung)
                trennlinie()
                tabelle_ausgeben(zeilen)
            except Exception as e:
                print("Fehler: " + str(e))
        elif auswahl == "9":
            break
        else:
            print("Ungültige Auswahl!")

        input("\nWeiter mit Enter...")


def freie_suche():
    print("\nFreie Suche (leer lassen = egal):")
    titel = input("Titel enthält: ").strip() or None
    dateityp = input("Dateityp (z.B. pdf): ").strip() or None

    themen = db.themen_laden()
    print("\nThemengebiete:")
    for t in themen:
        print(str(t["themengebiet_id"]) + " - " + t["name"])
    thema_eingabe = input("Themengebiet-ID (leer = alle): ").strip()
    thema_id = int(thema_eingabe) if thema_eingabe.isdigit() else None

    benutzer_liste = db.benutzer_laden()
    print("\nBenutzer:")
    for b in benutzer_liste:
        print(str(b["benutzer_id"]) + " - " + b["anzeigename"])
    autor_eingabe = input("Autor-ID (leer = alle): ").strip()
    autor_id = int(autor_eingabe) if autor_eingabe.isdigit() else None

    zeilen = db.materialien_laden(titel=titel, dateityp=dateityp, thema_id=thema_id, autor_id=autor_id)
    trennlinie()
    tabelle_ausgeben(zeilen)


# -----------------------------------------------------------------------
# Material herunterladen
# -----------------------------------------------------------------------

def material_herunterladen():
    trennlinie()
    print("MATERIAL HERUNTERLADEN")
    trennlinie()

    # Alle Materialien anzeigen
    zeilen = db.materialien_laden()
    if not zeilen:
        print("Keine Materialien vorhanden.")
        return
    tabelle_ausgeben(zeilen)

    mat_id_eingabe = input("\nMaterial-ID: ").strip()
    try:
        material_id = int(mat_id_eingabe)
    except ValueError:
        print("Fehler: Keine gültige ID!")
        return

    ziel = input("Zielordner (leer = downloads/): ").strip() or None

    try:
        ziel_datei = db.material_herunterladen(material_id, ziel)
        print("Datei gespeichert unter: " + ziel_datei)

        oeffnen = input("Datei jetzt öffnen? (j/n): ").strip().lower()
        if oeffnen == "j":
            if sys.platform == "win32":
                os.startfile(ziel_datei)
            else:
                os.system("xdg-open " + ziel_datei)
    except Exception as e:
        print("Fehler: " + str(e))


# -----------------------------------------------------------------------
# Kommentare
# -----------------------------------------------------------------------

def kommentare_anzeigen():
    trennlinie()
    print("KOMMENTARE")
    trennlinie()

    zeilen = db.materialien_laden()
    if not zeilen:
        print("Keine Materialien vorhanden.")
        return
    tabelle_ausgeben(zeilen)

    mat_id_eingabe = input("\nMaterial-ID: ").strip()
    try:
        material_id = int(mat_id_eingabe)
    except ValueError:
        print("Fehler: Keine gültige ID!")
        return

    kommentare = db.kommentare_laden(material_id)
    trennlinie()
    tabelle_ausgeben(kommentare)


def kommentar_hinzufuegen():
    trennlinie()
    print("KOMMENTAR HINZUFÜGEN")
    trennlinie()

    zeilen = db.materialien_laden()
    if not zeilen:
        print("Keine Materialien vorhanden.")
        return
    tabelle_ausgeben(zeilen)

    mat_id_eingabe = input("\nMaterial-ID: ").strip()
    try:
        material_id = int(mat_id_eingabe)
    except ValueError:
        print("Fehler: Keine gültige ID!")
        return

    text = input("Kommentartext: ").strip()
    if not text:
        print("Fehler: Kommentar darf nicht leer sein!")
        return

    try:
        neue_id = db.kommentar_speichern(material_id, benutzer["benutzer_id"], text)
        print("Kommentar gespeichert (ID: " + str(neue_id) + ")")
    except Exception as e:
        print("Fehler: " + str(e))


# -----------------------------------------------------------------------
# Themengebiete
# -----------------------------------------------------------------------

def themen_verwalten():
    while True:
        trennlinie()
        print("THEMENGEBIETE")
        trennlinie()
        print("1. Alle Themengebiete anzeigen")
        print("2. Neues Themengebiet anlegen")
        print("3. Zurück")
        trennlinie()

        auswahl = input("Auswahl: ").strip()

        if auswahl == "1":
            zeilen = db.themen_laden()
            tabelle_ausgeben(zeilen)
        elif auswahl == "2":
            name = input("Name: ").strip()
            if not name:
                print("Fehler: Name darf nicht leer sein!")
                continue
            beschreibung = input("Beschreibung (optional): ").strip()
            neue_id = db.thema_anlegen(name, beschreibung)
            print("Themengebiet angelegt (ID: " + str(neue_id) + ")")
        elif auswahl == "3":
            break
        else:
            print("Ungültige Auswahl!")

        input("\nWeiter mit Enter...")


# -----------------------------------------------------------------------
# Hauptmenü
# -----------------------------------------------------------------------

def hauptmenue():
    while True:
        trennlinie()
        print("BBSliothek - Hauptmenü")
        print("Angemeldet als: " + benutzer["anzeigename"])
        trennlinie()
        print("1. Material hochladen")
        print("2. Materialien suchen / Standardabfragen")
        print("3. Material herunterladen")
        print("4. Kommentare anzeigen")
        print("5. Kommentar hinzufügen")
        print("6. Themengebiete verwalten")
        print("7. Benutzer anzeigen")
        print("8. Beenden")
        trennlinie()

        auswahl = input("Auswahl: ").strip()

        if auswahl == "1":
            material_hochladen()
        elif auswahl == "2":
            materialien_suchen()
        elif auswahl == "3":
            material_herunterladen()
        elif auswahl == "4":
            kommentare_anzeigen()
        elif auswahl == "5":
            kommentar_hinzufuegen()
        elif auswahl == "6":
            themen_verwalten()
        elif auswahl == "7":
            trennlinie()
            tabelle_ausgeben(db.benutzer_laden())
            input("\nWeiter mit Enter...")
        elif auswahl == "8":
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Auswahl! Bitte 1-8 eingeben.")


# -----------------------------------------------------------------------
# Programmstart
# -----------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("  BBSliothek - Lernmaterialverwaltung")
    print("=" * 50)

    # Login-Schleife - max. 3 Versuche
    versuche = 0
    eingeloggt = False

    while versuche < 3:
        if login():
            eingeloggt = True
            break
        versuche += 1
        if versuche < 3:
            print(f"Noch {3 - versuche} Versuch(e) übrig.")

    if not eingeloggt:
        print("Zu viele Fehlversuche. Programm wird beendet.")
        sys.exit(1)

    hauptmenue()
