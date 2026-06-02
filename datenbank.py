import mysql.connector
import os
import shutil
import re
from dotenv import load_dotenv

load_dotenv()

DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = int(os.getenv("DB_PORT"))
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

STORAGE_ORDNER  = os.getenv("STORAGE_ROOT")
DOWNLOAD_ORDNER = os.getenv("DOWNLOAD_ROOT")


#https://stackoverflow.com/questions/372885
def verbinden():
    db = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return db



#def anfrage(sql, frage):
#    db = verbinden()
#    cur = db.cursor(dictionary=True)
#    cur.execute(frage)
#    result = cur.fetchall()
#    db.close()
#    return result



# fetchall() - print all the first cell of all the rows
# fetchone() - print first cell of all the rows


#login
def einloggen(benutzername, passwort):
    db = verbinden()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT b.benutzer_id, b.benutzername, b.vorname, b.nachname,
               CONCAT(b.vorname, ' ', b.nachname) AS anzeigename,
               b.email, r.name AS rolle
        FROM benutzer b
        INNER JOIN rollen r ON r.rollen_id = b.rollen_id
        WHERE b.benutzername = %s AND b.passwort = %s
    """, (benutzername, passwort))
    row = cur.fetchone()
    db.close()
    return row  #none wenn gibt es kein


#benutzer
def benutzer_mit_anzahl():
    # Join + Aggregation: Benutzer mit Anzahl hochgeladener Materialien
    db = verbinden()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT CONCAT(b.vorname, ' ', b.nachname) AS name,
               r.name AS rolle,
               COUNT(m.material_id) AS anzahl_materialien
        FROM benutzer b
        INNER JOIN rollen r ON r.rollen_id = b.rollen_id
        LEFT JOIN materialien m ON m.erstellt_von = b.benutzer_id
        GROUP BY b.benutzer_id, b.vorname, b.nachname, r.name
        ORDER BY b.nachname
    """)
    result = cur.fetchall()
    db.close()
    return result


def benutzer_laden():
    db = verbinden()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT b.benutzer_id, b.vorname, b.nachname,
               CONCAT(b.vorname, ' ', b.nachname) AS anzeigename,
               b.email, r.name AS rolle, b.erstellt_am
        FROM benutzer b
        INNER JOIN rollen r ON r.rollen_id = b.rollen_id
        ORDER BY b.nachname
    """)
    result = cur.fetchall()
    db.close()
    return result


def benutzer_anlegen(vorname, nachname, email, passwort, rollen_id):
    # Benutzername automatisch generieren: erster Buchstabe Vorname + "." + Nachname
    benutzername = vorname[0].lower() + "." + nachname.lower()
    db = verbinden()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO benutzer (rollen_id, benutzername, vorname, nachname, email, passwort)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (rollen_id, benutzername, vorname, nachname, email, passwort))
    db.commit()
    neue_id = cur.lastrowid
    db.close()
    return neue_id


def email_gueltig(email):
    # Einfache E-Mail-Validierung
    # Quelle: https://stackoverflow.com/questions/8022530
    muster = r"^[^@]+@[^@]+\.[^@]+$"
    return bool(re.match(muster, email))


def rollen_laden():
    db = verbinden()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT rollen_id, name FROM rollen ORDER BY rollen_id")
    result = cur.fetchall()
    db.close()
    return result


#themengebiete
def themen_mit_anzahl():
    # Aggregation: Themen mit Anzahl der Materialien
    db = verbinden()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT tg.themengebiet_id, tg.name,
               COUNT(m.material_id) AS anzahl_materialien
        FROM themengebiete tg
        LEFT JOIN materialien m ON m.themengebiet_id = tg.themengebiet_id
        GROUP BY tg.themengebiet_id, tg.name
        ORDER BY tg.name
    """)
    result = cur.fetchall()
    db.close()
    return result


def themen_laden():
    db = verbinden()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT themengebiet_id, name, beschreibung FROM themengebiete ORDER BY name")
    result = cur.fetchall()
    db.close()
    return result


def thema_anlegen(name, beschreibung=""):
    db = verbinden()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO themengebiete (name, beschreibung)
        VALUES (%s, %s)
    """, (name, beschreibung))
    db.commit()
    neue_id = cur.lastrowid
    db.close()
    return neue_id


#materialien
def materialien_laden(titel=None, dateityp=None, thema_id=None, autor_id=None):
    db = verbinden()
    cur = db.cursor(dictionary=True)

    sql = """
        SELECT material_id, titel, dateiname, dateityp,
               themengebiet_name AS themengebiet,
               material_autor_name AS autor,
               material_autor_id,
               versionsnummer AS version,
               dateigroesse_bytes,
               speicherstrategie,
               material_erstellt_am AS erstellt_am,
               version_autor_name AS zuletzt_geaendert_von
        FROM vw_material_aktuell
        WHERE 1=1
    """
    params = []

    if titel:
        sql += " AND (titel LIKE %s OR dateiname LIKE %s)"
        params.append("%" + titel + "%")
        params.append("%" + titel + "%")

    if dateityp:
        sql += " AND dateityp LIKE %s"
        params.append("%" + dateityp + "%")

    if thema_id:
        sql += " AND themengebiet_id = %s"
        params.append(thema_id)

    if autor_id:
        sql += " AND material_autor_id = %s"
        params.append(autor_id)

    sql += " ORDER BY titel"

    cur.execute(sql, params)
    result = cur.fetchall()
    db.close()
    return result


def material_hochladen(quelldatei, autor_id, titel=None, thema_id=None, material_id=None):
    if os.path.exists(quelldatei) == False:
        raise Exception("Datei nicht gefunden: " + quelldatei)

    dateiname = os.path.basename(quelldatei)
    dateityp = os.path.splitext(dateiname)[1].lower()
    groesse = os.path.getsize(quelldatei)

    # Speicherstrategie: unter 1 MB -> BLOB, sonst -> Dateisystem
    if groesse < 1000000:
        strategie = "DB_BLOB"
        with open(quelldatei, "rb") as f:
            blob_inhalt = f.read()
        ziel_pfad = None
    else:
        strategie = "DATEISYSTEM"
        blob_inhalt = None
        if os.path.exists(STORAGE_ORDNER) == False:
            os.makedirs(STORAGE_ORDNER)
        ziel_pfad = os.path.join(STORAGE_ORDNER, dateiname)
        shutil.copy2(quelldatei, ziel_pfad)

    db = verbinden()
    cur = db.cursor(dictionary=True)

    if material_id == None:
        # Neues Material anlegen
        cur.execute("""
            INSERT INTO materialien (titel, themengebiet_id, erstellt_von, erstellt_am, geaendert_am)
            VALUES (%s, %s, %s, NOW(), NOW())
        """, (titel, thema_id, autor_id))
        material_id = cur.lastrowid

    # Nächste Versionsnummer ermitteln
    cur.execute("""
        SELECT MAX(versionsnummer) AS max_version
        FROM material_versionen
        WHERE material_id = %s
    """, (material_id,))
    row = cur.fetchone()
    if row["max_version"] == None:
        naechste_version = 1
    else:
        naechste_version = row["max_version"] + 1

    # Version speichern
    cur.execute("""
        INSERT INTO material_versionen
        (material_id, versionsnummer, dateiname, dateityp, dateigroesse_bytes,
         speicherstrategie, blob_inhalt, dateipfad, erstellt_von, erstellt_am)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """, (material_id, naechste_version, dateiname, dateityp, groesse,
          strategie, blob_inhalt, ziel_pfad, autor_id))
    version_id = cur.lastrowid

    # Zeiger auf aktuelle Version aktualisieren
    cur.execute("""
        UPDATE materialien SET aktuelle_version_id = %s, geaendert_am = NOW()
        WHERE material_id = %s
    """, (version_id, material_id))

    db.commit()
    db.close()
    return {
        "material_id": material_id,
        "version": naechste_version,
        "strategie": strategie,
        "pfad": ziel_pfad
    }


def material_loeschen(material_id):
    db = verbinden()
    cur = db.cursor()
    # Kommentare löschen
    cur.execute("DELETE FROM kommentare WHERE material_id = %s", (material_id,))
    # aktuelle_version_id auf NULL setzen - sonst Foreign Key Fehler
    cur.execute("UPDATE materialien SET aktuelle_version_id = NULL WHERE material_id = %s", (material_id,))
    # Versionen löschen
    cur.execute("DELETE FROM material_versionen WHERE material_id = %s", (material_id,))
    # Material löschen
    cur.execute("DELETE FROM materialien WHERE material_id = %s", (material_id,))
    db.commit()
    db.close()


def material_herunterladen(material_id, ziel_ordner=None):
    if ziel_ordner == None:
        ziel_ordner = DOWNLOAD_ORDNER

    if os.path.exists(ziel_ordner) == False:
        os.makedirs(ziel_ordner)

    db = verbinden()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT dateiname, speicherstrategie, blob_inhalt, dateipfad
        FROM vw_material_aktuell
        WHERE material_id = %s
    """, (material_id,))
    row = cur.fetchone()
    db.close()

    if row == None:
        raise Exception("Material nicht gefunden (ID: " + str(material_id) + ")")

    ziel_datei = os.path.join(ziel_ordner, row["dateiname"])

    if row["speicherstrategie"] == "DB_BLOB":
        # BLOB aus der Datenbank in eine Datei schreiben
        with open(ziel_datei, "wb") as f:
            f.write(row["blob_inhalt"])
    else:
        # Datei vom Dateisystem kopieren
        shutil.copy2(row["dateipfad"], ziel_datei)

    return ziel_datei


#kommentare
def materialien_mit_kommentaranzahl():
    # Aggregation: Materialien mit Anzahl der Kommentare
    db = verbinden()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT m.material_id, m.titel,
               COUNT(k.kommentar_id) AS anzahl_kommentare
        FROM materialien m
        LEFT JOIN kommentare k ON k.material_id = m.material_id
        GROUP BY m.material_id, m.titel
        ORDER BY m.titel
    """)
    result = cur.fetchall()
    db.close()
    return result


def kommentare_laden(material_id):
    db = verbinden()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT k.kommentar_id, CONCAT(b.vorname, ' ', b.nachname) AS autor,
               b.benutzer_id AS autor_id, k.kommentartext, k.erstellt_am, k.geaendert_am
        FROM kommentare k
        INNER JOIN benutzer b ON b.benutzer_id = k.autor_id
        WHERE k.material_id = %s
        ORDER BY k.erstellt_am
    """, (material_id,))
    result = cur.fetchall()
    db.close()
    return result


def kommentar_speichern(material_id, autor_id, text):
    db = verbinden()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO kommentare (material_id, autor_id, kommentartext, erstellt_am, geaendert_am)
        VALUES (%s, %s, %s, NOW(), NOW())
    """, (material_id, autor_id, text))
    db.commit()
    neue_id = cur.lastrowid
    db.close()
    return neue_id


def kommentar_loeschen(kommentar_id):
    db = verbinden()
    cur = db.cursor()
    cur.execute("DELETE FROM kommentare WHERE kommentar_id = %s", (kommentar_id,))
    db.commit()
    db.close()


def kommentar_bearbeiten(kommentar_id, neuer_text):
    db = verbinden()
    cur = db.cursor()
    cur.execute("""
        UPDATE kommentare SET kommentartext = %s, geaendert_am = NOW()
        WHERE kommentar_id = %s
    """, (neuer_text, kommentar_id))
    db.commit()
    db.close()

