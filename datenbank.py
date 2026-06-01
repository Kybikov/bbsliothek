# Datenbank-Modul für BBSliothek
# Quelle MySQL Connector: https://dev.mysql.com/doc/connector-python/en/

import mysql.connector
from mysql.connector import Error
import os
import hashlib
import shutil


# Verbindungsdaten aus Umgebungsvariablen lesen
# (damit das Passwort nicht im Code steht)
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "bbsliothek")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Ordner für Dateien und Downloads
STORAGE_ORDNER = os.getenv("STORAGE_ROOT", "storage/materials")
DOWNLOAD_ORDNER = os.getenv("DOWNLOAD_ROOT", "downloads")

# Dateien unter 1 MB werden als BLOB in die DB gespeichert
# Dateien über 1 MB werden nur als Pfad gespeichert (Performance)
MAX_BLOB_GROESSE = 1_000_000


def verbinden():
    # Verbindung zur MySQL-Datenbank herstellen
    # Quelle: https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        if conn.is_connected():
            # print("Datenbankverbindung erfolgreich")  # debug
            return conn
    except Error as e:
        raise Exception(f"Verbindung zur Datenbank fehlgeschlagen: {e}")


def materialien_laden(titel=None, dateityp=None, thema_id=None):
    # Alle Materialien aus der View laden, optional gefiltert
    conn = verbinden()
    cursor = conn.cursor(dictionary=True)

    # Basisabfrage - WHERE 1=1 damit man einfach AND anhängen kann
    # Tipp von Stack Overflow: https://stackoverflow.com/questions/1149545
    sql = """
        SELECT material_id, titel, dateiname, dateityp,
               themengebiet_name AS themengebiet,
               material_autor_name AS autor,
               versionsnummer AS version,
               dateigroesse_bytes,
               speicherstrategie,
               material_erstellt_am AS erstellt_am
        FROM vw_material_aktuell
        WHERE 1=1
    """
    params = []

    # Filter nur hinzufügen wenn ein Wert eingegeben wurde
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

    sql += " ORDER BY titel"

    cursor.execute(sql, params)
    result = cursor.fetchall()

    # Verbindung schließen
    cursor.close()
    conn.close()

    return result


def material_hochladen(quelldatei, autor_id, titel=None, thema_id=None, material_id=None):
    # Prüfen ob die Datei überhaupt existiert
    if not os.path.exists(quelldatei):
        raise Exception("Datei nicht gefunden: " + quelldatei)

    # Dateiinformationen ermitteln
    dateiname = os.path.basename(quelldatei)
    name, ext = os.path.splitext(dateiname)
    dateityp = ext.lower()
    groesse = os.path.getsize(quelldatei)

    # Dateiinhalt lesen
    with open(quelldatei, "rb") as f:
        datei_inhalt = f.read()

    # SHA256 Prüfsumme berechnen (für spätere Integritätsprüfung)
    checksumme = hashlib.sha256(datei_inhalt).hexdigest()
    # print("SHA256:", checksumme)  # debug

    # Speicherstrategie bestimmen je nach Dateigröße
    if groesse < MAX_BLOB_GROESSE:
        # Kleine Datei -> direkt als BLOB in die Datenbank
        strategie = "DB_BLOB"
        blob_inhalt = datei_inhalt
        dateipfad = None
    else:
        # Große Datei -> ins Dateisystem kopieren, nur Pfad speichern
        strategie = "DATEISYSTEM"
        blob_inhalt = None
        if not os.path.exists(STORAGE_ORDNER):
            os.makedirs(STORAGE_ORDNER)
        dateipfad = os.path.join(STORAGE_ORDNER, dateiname)
        shutil.copy2(quelldatei, dateipfad)

    conn = verbinden()
    cursor = conn.cursor(dictionary=True)

    try:
        # Transaktion starten damit bei Fehler alles rückgängig gemacht wird
        conn.start_transaction()

        if material_id is None:
            # Neues Material in die Datenbank einfügen
            cursor.execute(
                "INSERT INTO materialien (titel, themengebiet_id, erstellt_von, erstellt_am, geaendert_am) "
                "VALUES (%s, %s, %s, NOW(), NOW())",
                (titel, thema_id, autor_id)
            )
            material_id = cursor.lastrowid
            # print("Neues Material angelegt, ID:", material_id)  # debug

        # Nächste Versionsnummer berechnen
        # COALESCE gibt 0 zurück wenn noch keine Version existiert
        cursor.execute(
            "SELECT COALESCE(MAX(versionsnummer), 0) + 1 AS naechste "
            "FROM material_versionen WHERE material_id = %s",
            (material_id,)
        )
        row = cursor.fetchone()
        naechste_version = row["naechste"]

        # Version speichern
        cursor.execute(
            "INSERT INTO material_versionen "
            "(material_id, versionsnummer, dateiname, dateityp, dateigroesse_bytes, "
            "speicherstrategie, blob_inhalt, dateipfad, checksumme_sha256, erstellt_von, erstellt_am) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())",
            (material_id, naechste_version, dateiname, dateityp, groesse,
             strategie, blob_inhalt, dateipfad, checksumme, autor_id)
        )
        version_id = cursor.lastrowid

        # aktuelle_version_id in materialien aktualisieren
        cursor.execute(
            "UPDATE materialien SET aktuelle_version_id = %s, geaendert_am = NOW() "
            "WHERE material_id = %s",
            (version_id, material_id)
        )

        conn.commit()
        return {
            "material_id": material_id,
            "version": naechste_version,
            "strategie": strategie
        }

    except Exception as e:
        # Bei Fehler: alle Änderungen rückgängig machen
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def material_herunterladen(material_id, ziel_ordner=None):
    if ziel_ordner is None:
        ziel_ordner = DOWNLOAD_ORDNER

    # Ordner anlegen falls nicht vorhanden
    if not os.path.exists(ziel_ordner):
        os.makedirs(ziel_ordner)

    conn = verbinden()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT dateiname, speicherstrategie, blob_inhalt, dateipfad "
        "FROM vw_material_aktuell WHERE material_id = %s",
        (material_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        raise Exception("Material nicht gefunden (ID: " + str(material_id) + ")")

    ziel_datei = os.path.join(ziel_ordner, row["dateiname"])

    if row["speicherstrategie"] == "DB_BLOB":
        # BLOB aus der DB als Datei schreiben
        # bytes() nötig weil MySQL Connector bytearray zurückgibt
        with open(ziel_datei, "wb") as f:
            f.write(bytes(row["blob_inhalt"]))
    else:
        # Datei aus dem Dateisystem kopieren
        shutil.copy2(row["dateipfad"], ziel_datei)

    return ziel_datei


def kommentare_laden(material_id):
    conn = verbinden()
    cursor = conn.cursor(dictionary=True)

    # JOIN mit benutzer um den Namen des Autors zu bekommen
    cursor.execute(
        "SELECT k.kommentar_id, b.anzeigename AS autor, "
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


def benutzer_laden():
    conn = verbinden()
    cursor = conn.cursor(dictionary=True)

    # JOIN mit rollen Tabelle um den Rollennamen zu bekommen
    cursor.execute(
        "SELECT b.benutzer_id, b.anzeigename, b.email, r.name AS rolle "
        "FROM benutzer b "
        "INNER JOIN rollen r ON r.rollen_id = b.rollen_id "
        "ORDER BY b.anzeigename"
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


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
