import os
import datenbank as db
from dotenv import load_dotenv
load_dotenv()

# aktuell eingeloggter Benutzer
benutzer = None


def divider():
    print("-" * 50)


def tabelle_ausgeben(zeilen):
    if len(zeilen) == 0:
        print("(keine Ergebnisse)")
        return
    for zeile in zeilen:
        for key, value in zeile.items():
            if key == "blob_inhalt":
                continue
            print(str(key) + ": " + str(value))
        print("---")
    print(str(len(zeilen)) + " Ergebnis(se)")


#login
def login():
    print("BBSliothek - Anmelden")
    divider()

    global benutzer
    name = input("Benutzername: ")
    passwort = input("Passwort: ")

    ergebnis = db.einloggen(name, passwort)

    # zuerst so probiert - hat nicht funktioniert
    # if ergebnis == "":
    #     return False

    # einloggen() gibt None zurück wenn nichts gefunden wurde
    if ergebnis == None:
        print("Falscher Benutzername oder Passwort")
        return False

    benutzer = ergebnis
    print("Angemeldet als: " + benutzer["anzeigename"] + " (" + benutzer["rolle"] + ")")
    return True


#materialien
def materialien_menu():
    divider()
    print("MATERIALIEN")
    divider()

    # Inner Join: Material + Thema + Autor + Version (über View)
    zeilen = db.materialien_laden()
    if len(zeilen) == 0:
        print("Keine Materialien vorhanden.")
        eingabe = input("\n1. Neues Material hochladen  2. Zurück: ").strip()
        if eingabe == "1":
            material_hochladen()
        return

    tabelle_ausgeben(zeilen)

    divider()
    print("1. Neues Material hochladen")
    print("2. Material auswählen (herunterladen / neue Version / löschen)")
    print("3. Suchen / Filtern")
    print("4. Zurück")
    wahl = input("Auswahl: ").strip()

    if wahl == "1":
        material_hochladen()
    elif wahl == "2":
        mat_id = input("Material-ID: ").strip()
        try:
            material_id = int(mat_id)
        except ValueError:
            print("Keine gültige ID!")
            return

        print("1. Herunterladen  2. Neue Version  3. Löschen")
        aktion = input("Auswahl: ").strip()

        if aktion == "1":
            ziel_eingabe = input("Zielordner (leer = downloads/): ").strip()
            ziel = None
            if ziel_eingabe != "":
                ziel = ziel_eingabe
            ziel_datei = db.material_herunterladen(material_id, ziel)
            print("Gespeichert unter: " + ziel_datei)

        elif aktion == "2":
            file_pfad = input("Pfad zur neuen Datei: ").strip()
            if os.path.exists(file_pfad) == False:
                print("Datei nicht gefunden!")
                return
            ergebnis = db.material_hochladen(file_pfad, benutzer["benutzer_id"], material_id=material_id)
            print("Version " + str(ergebnis["version"]) + " gespeichert!")

        elif aktion == "3":
            bestaetigung = input("Wirklich löschen? (j/n): ").strip().lower()
            if bestaetigung == "j":
                db.material_loeschen(material_id)
                print("Material gelöscht.")

    elif wahl == "3":
        print("\nSuchen (leer lassen = egal):")
        titel_eingabe = input("Titel enthält: ").strip()
        titel = None
        if titel_eingabe != "":
            titel = titel_eingabe

        typ_eingabe = input("Dateityp (z.B. .pdf): ").strip()
        dateityp = None
        if typ_eingabe != "":
            dateityp = typ_eingabe

        zeilen = db.materialien_laden(titel=titel, dateityp=dateityp)
        tabelle_ausgeben(zeilen)


def material_hochladen():
    divider()
    print("NEUES MATERIAL HOCHLADEN")
    divider()

    file_pfad = input("Pfad zur Datei: ").strip()
    if os.path.exists(file_pfad) == False:
        print("Datei nicht gefunden!")
        return

    # Dateiname als Titel verwenden
    titel = os.path.basename(file_pfad)

    # Themen mit Anzahl der Materialien anzeigen (Aggregation)
    themen = db.themen_mit_anzahl()
    print("\nThemengebiete:")
    for t in themen:
        print(str(t["themengebiet_id"]) + " - " + t["name"] + " (" + str(t["anzahl_materialien"]) + " Materialien)")

    thema_eingabe = input("Themengebiet-ID: ").strip()
    try:
        thema_id = int(thema_eingabe)
    except ValueError:
        print("Keine gültige ID!")
        return

    ergebnis = db.material_hochladen(file_pfad, benutzer["benutzer_id"], titel=titel, thema_id=thema_id)
    print("Gespeichert! Material-ID: " + str(ergebnis["material_id"]) + ", Strategie: " + ergebnis["strategie"])


#themengebiete
def themen_menu():
    divider()
    print("THEMENGEBIETE")
    divider()

    # Aggregation: Themen mit Anzahl der Materialien
    themen = db.themen_mit_anzahl()
    tabelle_ausgeben(themen)

    divider()
    print("1. Materialien eines Themas anzeigen")
    print("2. Neues Thema anlegen")
    print("3. Zurück")
    wahl = input("Auswahl: ").strip()

    if wahl == "1":
        thema_id = input("Themengebiet-ID: ").strip()
        try:
            thema_id = int(thema_id)
        except ValueError:
            print("Keine gültige ID!")
            return
        # Inner Join: Materialien mit Autor + Thema (über View gefiltert)
        zeilen = db.materialien_laden(thema_id=thema_id)
        tabelle_ausgeben(zeilen)

    elif wahl == "2":
        name = input("Name: ").strip()
        if name == "":
            print("Name darf nicht leer sein!")
            return
        beschreibung = input("Beschreibung (optional): ").strip()
        neue_id = db.thema_anlegen(name, beschreibung)
        print("Thema angelegt (ID: " + str(neue_id) + ")")


#benutzer
def benutzer_menu():
    divider()
    print("BENUTZER")
    divider()

    # Join + Aggregation: Benutzer mit Rolle + Anzahl Materialien
    zeilen = db.benutzer_mit_anzahl()
    tabelle_ausgeben(zeilen)

    divider()
    print("1. Neuen Benutzer anlegen")
    print("2. Zurück")
    wahl = input("Auswahl: ").strip()

    if wahl == "1":
        vorname = input("Vorname: ").strip()
        nachname = input("Nachname: ").strip()
        email = input("E-Mail: ").strip()
        passwort = input("Passwort: ").strip()

        rollen = db.rollen_laden()
        for r in rollen:
            print(str(r["rollen_id"]) + " - " + r["name"])
        rollen_eingabe = input("Rollen-ID: ").strip()
        try:
            rollen_id = int(rollen_eingabe)
        except ValueError:
            print("Keine gültige ID!")
            return

        neue_id = db.benutzer_anlegen(vorname, nachname, email, passwort, rollen_id)
        print("Benutzer angelegt (ID: " + str(neue_id) + ")")


#kommentare
def kommentare_menu():
    divider()
    print("KOMMENTARE")
    divider()

    # Aggregation: Materialien mit Anzahl der Kommentare
    zeilen = db.materialien_mit_kommentaranzahl()
    tabelle_ausgeben(zeilen)

    divider()
    print("1. Kommentare eines Materials anzeigen")
    print("2. Kommentar hinzufügen")
    print("3. Kommentar bearbeiten")
    print("4. Kommentar löschen")
    print("5. Zurück")
    wahl = input("Auswahl: ").strip()

    if wahl == "1":
        mat_id = input("Material-ID: ").strip()
        try:
            material_id = int(mat_id)
        except ValueError:
            print("Keine gültige ID!")
            return
        # Inner Join: Kommentare mit Autor
        kommentare = db.kommentare_laden(material_id)
        tabelle_ausgeben(kommentare)

    elif wahl == "2":
        mat_id = input("Material-ID: ").strip()
        try:
            material_id = int(mat_id)
        except ValueError:
            print("Keine gültige ID!")
            return
        text = input("Kommentartext: ").strip()
        if text == "":
            print("Kommentar darf nicht leer sein!")
            return
        neue_id = db.kommentar_speichern(material_id, benutzer["benutzer_id"], text)
        print("Kommentar gespeichert (ID: " + str(neue_id) + ")")

    elif wahl == "3":
        kid = input("Kommentar-ID: ").strip()
        try:
            kommentar_id = int(kid)
        except ValueError:
            print("Keine gültige ID!")
            return
        neuer_text = input("Neuer Text: ").strip()
        if neuer_text == "":
            print("Text darf nicht leer sein!")
            return
        db.kommentar_bearbeiten(kommentar_id, neuer_text)
        print("Kommentar gespeichert.")

    elif wahl == "4":
        kid = input("Kommentar-ID: ").strip()
        try:
            kommentar_id = int(kid)
        except ValueError:
            print("Keine gültige ID!")
            return
        db.kommentar_loeschen(kommentar_id)
        print("Kommentar gelöscht.")


#menu
def hauptmenue():
    while True:
        divider()
        print("BBSliothek - Hauptmenü")
        print("Hallo " + benutzer["vorname"] + "!")
        divider()
        print("1. Materialien")
        print("2. Themengebiete")
        print("3. Benutzer")
        print("4. Kommentare")
        print("5. Beenden")
        divider()

        wahl = input("Auswahl: ")

        if wahl == "1":
            materialien_menu()
        elif wahl == "2":
            themen_menu()
        elif wahl == "3":
            benutzer_menu()
        elif wahl == "4":
            kommentare_menu()
        elif wahl == "5":
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Auswahl!")

        input("\nWeiter mit Enter...")


if __name__ == "__main__":
    print("=" * 50)
    print("  BBSliothek - Lernmaterialverwaltung")
    print("=" * 50)

    versuche = 0
    eingeloggt = False

    while versuche < 3:
        if login():
            eingeloggt = True
            break
        versuche += 1
        if versuche < 3:
            print("Noch " + str(3 - versuche) + " Versuch(e).")

    if eingeloggt == False:
        print("Zu viele Fehlversuche.")
    else:
        hauptmenue()
