# Datenbank-Modul für BBSliothek
# Quelle MySQL Connector: https://dev.mysql.com/doc/connector-python/en/

import mysql.connector
from mysql.connector import Error
import os
import shutil
import re
from dotenv import load_dotenv

# .env Datei laden (falls vorhanden)
# Quelle: https://pypi.org/project/python-dotenv/
load_dotenv()

# Verbindungsdaten aus Umgebungsvariablen lesen
# Frühere Version: Werte waren direkt im Code (hardcoded):
#   DB_HOST = "127.0.0.1"
#   DB_USER = "root"
#   DB_PASSWORD = ""
# Dann auf Umgebungsvariablen umgestellt damit der Code auf
# verschiedenen Systemen (lokal + Server) ohne Änderungen läuft
DB_HOST     = os.getenv("DB_HOST",     "127.0.0.1")
DB_PORT     = int(os.getenv("DB_PORT", "3306"))
DB_NAME     = os.getenv("DB_NAME",     "bbsliothek")
DB_USER     = os.getenv("DB_USER",     "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

STORAGE_ORDNER  = os.getenv("STORAGE_ROOT",  "storage/materials")
DOWNLOAD_ORDNER = os.getenv("DOWNLOAD_ROOT", "downloads")


def verbinden():
    # Verbindung zur MySQL-Datenbank herstellen
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        if conn.is_connected():
            return conn
    except Error as e:
        raise Exception("Verbindung zur Datenbank fehlgeschlagen: " + str(e))


# -----------------------------------------------------------------------
# Login
# -----------------------------------------------------------------------

def einloggen(benutzername, passwort):
    # Benutzer anhand von Name und Passwort suchen
    # Passwort wird als Klartext verglichen (vereinfacht für Schulprojekt)
    conn = verbinden()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT b.benutzer_id, b.anzeigename, b.email, r.name AS rolle "
        "FROM benutzer b "
        "INNER JOIN rollen r ON r.rollen_id = b.rollen_id "
        "WHERE b.anzeigename = %s AND b.passwort = %s",
        (benutzername, passwort)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result  # None wenn nicht gefunden


# -----------------------------------------------------------------------
# Benutzer
# -----------------------------------------------------------------------

def benutzer_laden():
    conn = verbinden()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT b.benutzer_id, b.anzeigename, b.email, r.name AS rolle, b.erstellt_am "
        "FROM benutzer b "
        "INNER JOIN rollen r ON r.rollen_id = b.rollen_id "
        "ORDER BY b.anzeigename"
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def benutzer_anlegen(anzeigename, email, passwort, rollen_id):
    conn = verbinden()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO benutzer (rollen_id, anzeigename, email, passwort) "
        "VALUES (%s, %s, %s, %s)",
        (rollen_id, anzeigename, email, passwort)
    )
    conn.commit()
    neue_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return neue_id


def email_gueltig(email):
    # Einfache E-Mail-Validierung mit regulärem Ausdruck
    # Quelle: https://stackoverflow.com/questions/8022530
    muster = r"^[^@]+@[^@]+\.[^@]+$"
    return bool(re.match(muster, email))


def rollen_laden():
    conn = verbinden()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT rollen_id, name FROM rollen ORDER BY rollen_id")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


# -----------------------------------------------------------------------
# Themengebiete
# -----------------------------------------------------------------------

def themen_laden():
    conn = verbinden()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT themengebiet_id, name, beschreibung FROM themengebiete ORDER BY name")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def thema_anlegen(name, beschreibung=""):
    conn = verbinden()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO themengebiete (name, beschreibung) VALUES (%s, %s)",
        (name, beschreibung)
    )
    conn.commit()
    neue_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return neue_id


# -----------------------------------------------------------------------
# Materialien
# -----------------------------------------------------------------------

def materialien_laden(titel=None, dateityp=None, thema_id=None, autor_id=None):
    conn = verbinden()
    cursor = conn.cursor(dictionary=True)

    # WHERE 1=1 damit man einfach AND anhängen kann
    sql = """
        SELECT material_id, titel, dateiname, dateityp,
               themengebiet_name  AS themengebiet,
               material_autor_name AS autor,
               material_autor_id,
               versionsnummer     AS version,
               dateigroesse_bytes,
               speicherstrategie,
               material_erstellt_am  AS erstellt_am,
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

    cursor.execute(sql, params)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def material_hochladen(quelldatei, autor_id, titel=None, thema_id=None, material_id=None):
    if not os.path.exists(quelldatei):
        raise Exception("Datei nicht gefunden: " + quelldatei)

    dateiname = os.path.basename(quelldatei)
    _, ext = os.path.splitext(dateiname)
    dateityp = ext.lower() if ext else "unbekannt"
    groesse = os.path.getsize(quelldatei)

    # Datei in den Storage-Ordner kopieren
    if not os.path.exists(STORAGE_ORDNER):
        os.makedirs(STORAGE_ORDNER)

    ziel_pfad = os.path.join(STORAGE_ORDNER, dateiname)
    shutil.copy2(quelldatei, ziel_pfad)

    conn = verbinden()
    cursor = conn.cursor(dictionary=True)

    try:
        conn.start_transaction()

        if material_id is None:
            # Neues Material anlegen
            cursor.execute(
                "INSERT INTO materialien (titel, themengebiet_id, erstellt_von, erstellt_am, geaendert_am) "
                "VALUES (%s, %s, %s, NOW(), NOW())",
                (titel, thema_id, autor_id)
            )
            material_id = cursor.lastrowid

        # Nächste Versionsnummer ermitteln
        cursor.execute(
            "SELECT COALESCE(MAX(versionsnummer), 0) + 1 AS naechste "
            "FROM material_versionen WHERE material_id = %s",
            (material_id,)
        )
        naechste_version = cursor.fetchone()["naechste"]

        # Version speichern - alle Dateien gehen ins Dateisystem
        cursor.execute(
            "INSERT INTO material_versionen "
            "(material_id, versionsnummer, dateiname, dateityp, dateigroesse_bytes, "
            "speicherstrategie, dateipfad, erstellt_von, erstellt_am) "
            "VALUES (%s, %s, %s, %s, %s, 'DATEISYSTEM', %s, %s, NOW())",
            (material_id, naechste_version, dateiname, dateityp, groesse, ziel_pfad, autor_id)
        )
        version_id = cursor.lastrowid

        # Zeiger auf aktuelle Version aktualisieren
        cursor.execute(
            "UPDATE materialien SET aktuelle_version_id = %s, geaendert_am = NOW() "
            "WHERE material_id = %s",
            (version_id, material_id)
        )

        conn.commit()
        return {
            "material_id": material_id,
            "version": naechste_version,
            "pfad": ziel_pfad
        }

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def material_herunterladen(material_id, ziel_ordner=None):
    if ziel_ordner is None:
        ziel_ordner = DOWNLOAD_ORDNER

    if not os.path.exists(ziel_ordner):
        os.makedirs(ziel_ordner)

    conn = verbinden()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT dateiname, dateipfad FROM vw_material_aktuell WHERE material_id = %s",
        (material_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        raise Exception("Material nicht gefunden (ID: " + str(material_id) + ")")

    ziel_datei = os.path.join(ziel_ordner, row["dateiname"])
    shutil.copy2(row["dateipfad"], ziel_datei)
    return ziel_datei


# -----------------------------------------------------------------------
# Kommentare
# -----------------------------------------------------------------------

def kommentare_laden(material_id):
    conn = verbinden()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT k.kommentar_id, b.anzeigename AS autor, b.benutzer_id AS autor_id, "
        "k.kommentartext, k.erstellt_am, k.geaendert_am "
        "FROM kommentare k "
        "INNER JOIN benutzer b ON b.benutzer_id = k.autor_id "
        "WHERE k.material_id = %s "
        "ORDER BY k.erstellt_am",
        (material_id,)
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def kommentar_speichern(material_id, autor_id, text):
    conn = verbinden()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO kommentare (material_id, autor_id, kommentartext, erstellt_am, geaendert_am) "
        "VALUES (%s, %s, %s, NOW(), NOW())",
        (material_id, autor_id, text)
    )
    conn.commit()
    neue_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return neue_id


def kommentar_loeschen(kommentar_id):
    conn = verbinden()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kommentare WHERE kommentar_id = %s", (kommentar_id,))
    conn.commit()
    cursor.close()
    conn.close()


def kommentar_bearbeiten(kommentar_id, neuer_text):
    conn = verbinden()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE kommentare SET kommentartext = %s, geaendert_am = NOW() "
        "WHERE kommentar_id = %s",
        (neuer_text, kommentar_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


# -----------------------------------------------------------------------
# 7 Standardabfragen laut Aufgabenstellung
# 2x Aggregation, 2x Inner Join, 1x Join+Aggregation, 2x mehrere Joins
# -----------------------------------------------------------------------
STANDARDABFRAGEN = [
    {
        "titel": "Materialien pro Themengebiet (Aggregation)",
        "beschreibung": "Zählt wie viele Materialien in jedem Themengebiet vorhanden sind",
        "sql": """
            SELECT tg.name AS Themengebiet, COUNT(m.material_id) AS Anzahl_Materialien
            FROM themengebiete tg
            LEFT JOIN materialien m ON m.themengebiet_id = tg.themengebiet_id
            GROUP BY tg.themengebiet_id, tg.name
            ORDER BY Anzahl_Materialien DESC
        """
    },
    {
        "titel": "Durchschnittliche Dateigröße je Thema (Aggregation)",
        "beschreibung": "Durchschnittsgröße aller Versionen pro Themengebiet in KB",
        "sql": """
            SELECT tg.name AS Themengebiet,
                   ROUND(AVG(mv.dateigroesse_bytes) / 1024, 2) AS Durchschnitt_KB,
                   COUNT(mv.version_id) AS Anzahl_Versionen
            FROM themengebiete tg
            INNER JOIN materialien m ON m.themengebiet_id = tg.themengebiet_id
            INNER JOIN material_versionen mv ON mv.material_id = m.material_id
            GROUP BY tg.themengebiet_id, tg.name
        """
    },
    {
        "titel": "Materialien mit Autoren (Inner Join)",
        "beschreibung": "Verknüpft Materialien mit den Benutzerdaten der Ersteller",
        "sql": """
            SELECT m.material_id, m.titel, b.anzeigename AS Autor, b.email
            FROM materialien m
            INNER JOIN benutzer b ON b.benutzer_id = m.erstellt_von
            ORDER BY m.titel
        """
    },
    {
        "titel": "Kommentare mit Material und Autor (Inner Join)",
        "beschreibung": "Zeigt alle Kommentare mit zugehörigem Material und Autor",
        "sql": """
            SELECT m.titel AS Material, b.anzeigename AS Kommentiert_von,
                   LEFT(k.kommentartext, 60) AS Kommentar, k.erstellt_am
            FROM kommentare k
            INNER JOIN materialien m ON m.material_id = k.material_id
            INNER JOIN benutzer b ON b.benutzer_id = k.autor_id
            ORDER BY k.erstellt_am DESC
        """
    },
    {
        "titel": "Materialien pro Autor mit Rolle (Join + Aggregation)",
        "beschreibung": "Zählt wie viele Materialien jeder Benutzer hochgeladen hat",
        "sql": """
            SELECT b.anzeigename AS Autor, r.name AS Rolle,
                   COUNT(m.material_id) AS Anzahl_Materialien
            FROM benutzer b
            INNER JOIN rollen r ON r.rollen_id = b.rollen_id
            INNER JOIN materialien m ON m.erstellt_von = b.benutzer_id
            GROUP BY b.benutzer_id, b.anzeigename, r.name
            ORDER BY Anzahl_Materialien DESC
        """
    },
    {
        "titel": "Materialien mit Thema und Version (2x Inner Join)",
        "beschreibung": "Verbindet Materialien mit Themengebiet und aktueller Version",
        "sql": """
            SELECT m.titel, tg.name AS Themengebiet,
                   mv.versionsnummer AS Version, mv.dateiname,
                   ROUND(mv.dateigroesse_bytes / 1024, 1) AS Groesse_KB,
                   mv.speicherstrategie
            FROM materialien m
            INNER JOIN themengebiete tg ON tg.themengebiet_id = m.themengebiet_id
            INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
            ORDER BY tg.name, m.titel
        """
    },
    {
        "titel": "Vollständige Übersicht (mehrere Joins)",
        "beschreibung": "Verbindet Material, Autor, Thema und Version in einer Abfrage",
        "sql": """
            SELECT m.titel, b.anzeigename AS Autor, tg.name AS Themengebiet,
                   mv.versionsnummer AS Version, mv.dateityp,
                   ROUND(mv.dateigroesse_bytes / 1024, 1) AS Groesse_KB,
                   m.erstellt_am
            FROM materialien m
            INNER JOIN benutzer b ON b.benutzer_id = m.erstellt_von
            INNER JOIN themengebiete tg ON tg.themengebiet_id = m.themengebiet_id
            INNER JOIN material_versionen mv ON mv.version_id = m.aktuelle_version_id
            ORDER BY m.erstellt_am DESC
        """
    }
]


def standardabfrage_ausfuehren(index):
    if index < 0 or index >= len(STANDARDABFRAGEN):
        raise Exception("Ungültige Abfragenummer")

    abfrage = STANDARDABFRAGEN[index]
    conn = verbinden()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(abfrage["sql"])
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return abfrage["titel"], abfrage["beschreibung"], result
