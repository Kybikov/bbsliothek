# BBSliothek - Lernmaterialverwaltung
# Flet Dokumentation: https://flet.dev/docs/
# Getting Started Guide: https://flet.dev/docs/getting-started/

import flet as ft
import datenbank as db
import os
import sys
import subprocess
from dotenv import load_dotenv

# .env Datei laden
load_dotenv()


def datei_oeffnen(pfad):
    # Datei plattformübergreifend öffnen
    # Quelle: https://stackoverflow.com/questions/434597
    # Zuerst nur os.startfile() verwendet (nur Windows) -> hat auf anderen Systemen nicht funktioniert
    # Dann sys.platform-Abfrage hinzugefügt um alle Plattformen zu unterstützen
    if sys.platform == "win32":
        os.startfile(pfad)
    elif sys.platform == "darwin":
        subprocess.run(["open", pfad])
    else:
        # Linux
        subprocess.run(["xdg-open", pfad])


def main(page: ft.Page):
    page.title = "BBSliothek – Lernmaterialverwaltung"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1200
    page.window.height = 800
    page.padding = 0
    page.bgcolor = "#f8f9fa"

    # Aktuell eingeloggter Benutzer (wird nach Login befüllt)
    aktueller_benutzer = {"id": None, "name": None, "rolle": None}

    # FilePicker wurde komplett entfernt - funktioniert nicht in Flet 0.80+
    # Weder dynamisch noch beim Start (Unknown control: FilePicker)
    # Lösung: Benutzer gibt den Dateipfad manuell ein

    # ==================================================================
    # Login-Seite
    # ==================================================================
    def zeige_login():
        page.clean()

        benutzername_feld = ft.TextField(label="Benutzername", width=320)
        passwort_feld = ft.TextField(
            label="Passwort",
            password=True,
            can_reveal_password=True,
            width=320,
        )
        fehler_text = ft.Text("", color="red", size=13)

        def anmelden(e):
            if not benutzername_feld.value or not passwort_feld.value:
                fehler_text.value = "Bitte alle Felder ausfüllen!"
                page.update()
                return

            benutzer = db.einloggen(benutzername_feld.value, passwort_feld.value)

            if benutzer is None:
                fehler_text.value = "Falscher Benutzername oder Passwort!"
                passwort_feld.value = ""
                page.update()
                return

            # Login erfolgreich - Daten speichern
            aktueller_benutzer["id"]    = benutzer["benutzer_id"]
            aktueller_benutzer["name"]  = benutzer["anzeigename"]
            aktueller_benutzer["rolle"] = benutzer["rolle"]

            zeige_hauptansicht()

        # Enter-Taste löst auch Login aus
        passwort_feld.on_submit = anmelden

        page.add(
            ft.Column(
                controls=[
                    ft.Text("BBSliothek", size=40, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_700),
                    ft.Text("Lernmaterialverwaltung", size=16, color="grey"),
                    ft.Divider(height=30, color="transparent"),
                    ft.Card(
                        elevation=3,
                        content=ft.Container(
                            padding=32,
                            width=380,
                            content=ft.Column([
                                ft.Text("Anmelden", size=20, weight=ft.FontWeight.W_600),
                                ft.Divider(height=10, color="transparent"),
                                benutzername_feld,
                                passwort_feld,
                                fehler_text,
                                ft.FilledButton(
                                    "Anmelden",
                                    icon=ft.Icons.LOGIN,
                                    on_click=anmelden,
                                    width=320,
                                ),
                            ], spacing=12),
                        ),
                    ),
                    ft.Text("Testbenutzer: Mia Hoffmann / lehrer123", size=11, color="grey"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
                spacing=8,
            )
        )
        page.update()

    # ==================================================================
    # Hauptansicht (nach Login)
    # ==================================================================
    def zeige_hauptansicht():
        page.clean()

        inhalt = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=10)

        def seite_laden(controls):
            inhalt.controls.clear()
            inhalt.controls.extend(controls)
            page.update()

        # --------------------------------------------------------------
        # Seite: Materialien
        # --------------------------------------------------------------
        def zeige_materialien(e=None):
            titel_feld  = ft.TextField(label="Titel / Dateiname", width=220, dense=True)
            typ_feld    = ft.TextField(label="Dateityp (.pdf …)", width=160, dense=True)
            status_text = ft.Text("", size=13)

            # Autor-Filter Dropdown
            benutzer_liste = db.benutzer_laden()
            autor_filter = ft.Dropdown(
                label="Autor",
                width=180,
                dense=True,
                options=[ft.dropdown.Option(key="", text="Alle")] + [
                    ft.dropdown.Option(key=str(b["benutzer_id"]), text=b["anzeigename"])
                    for b in benutzer_liste
                ],
                value="",
            )

            tabelle = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Titel")),
                    ft.DataColumn(ft.Text("Typ")),
                    ft.DataColumn(ft.Text("Thema")),
                    ft.DataColumn(ft.Text("Autor")),
                    ft.DataColumn(ft.Text("Ver.")),
                    ft.DataColumn(ft.Text("Geändert von")),
                    ft.DataColumn(ft.Text("Größe")),
                    ft.DataColumn(ft.Text("")),
                ],
                rows=[],
                border=ft.Border(
                    top=ft.BorderSide(1, "#dee2e6"),
                    bottom=ft.BorderSide(1, "#dee2e6"),
                    left=ft.BorderSide(1, "#dee2e6"),
                    right=ft.BorderSide(1, "#dee2e6"),
                ),
                border_radius=8,
                vertical_lines=ft.BorderSide(1, "#dee2e6"),
                heading_row_color="#e9ecef",
                column_spacing=16,
            )

            def tabelle_fuellen(titel=None, dateityp=None, autor_id=None):
                try:
                    materialien = db.materialien_laden(
                        titel=titel,
                        dateityp=dateityp,
                        autor_id=autor_id if autor_id else None
                    )
                    tabelle.rows.clear()

                    for m in materialien:
                        kb  = round(m["dateigroesse_bytes"] / 1024, 1)
                        mid = m["material_id"]
                        tabelle.rows.append(
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text(str(m["material_id"]))),
                                ft.DataCell(ft.Text(m["titel"][:30])),
                                ft.DataCell(ft.Text(m["dateityp"])),
                                ft.DataCell(ft.Text(m["themengebiet"][:18])),
                                ft.DataCell(ft.Text(m["autor"][:16])),
                                ft.DataCell(ft.Text(str(m["version"]))),
                                ft.DataCell(ft.Text(m["zuletzt_geaendert_von"][:16])),
                                ft.DataCell(ft.Text(str(kb) + " KB")),
                                ft.DataCell(
                                    ft.IconButton(
                                        icon=ft.Icons.DOWNLOAD_OUTLINED,
                                        tooltip="Herunterladen",
                                        icon_color=ft.Colors.BLUE_600,
                                        on_click=lambda e, x=mid: herunterladen(x),
                                    )
                                ),
                            ])
                        )

                    status_text.value = str(len(materialien)) + " Ergebnis(se)"
                    status_text.color = "grey"
                    page.update()
                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                    status_text.color = "red"
                    page.update()

            def herunterladen(material_id):
                try:
                    pfad = db.material_herunterladen(material_id)
                    status_text.value = "Gespeichert: " + pfad
                    status_text.color = "green"
                    page.update()
                    datei_oeffnen(pfad)
                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                    status_text.color = "red"
                    page.update()

            def suchen(e):
                autor_id = int(autor_filter.value) if autor_filter.value else None
                tabelle_fuellen(
                    titel=titel_feld.value or None,
                    dateityp=typ_feld.value or None,
                    autor_id=autor_id,
                )

            def zuruecksetzen(e):
                titel_feld.value  = ""
                typ_feld.value    = ""
                autor_filter.value = ""
                tabelle_fuellen()

            tabelle_fuellen()

            seite_laden([
                ft.Text("Lernmaterialien", size=26, weight=ft.FontWeight.BOLD),
                ft.Row([
                    titel_feld,
                    typ_feld,
                    autor_filter,
                    ft.FilledButton("Suchen", icon=ft.Icons.SEARCH, on_click=suchen),
                    ft.TextButton("Zurücksetzen", on_click=zuruecksetzen),
                ], spacing=8),
                status_text,
                ft.Container(content=tabelle, padding=ft.Padding(top=8, left=0, right=0, bottom=0)),
            ])

        # --------------------------------------------------------------
        # Seite: Upload
        # --------------------------------------------------------------
        def zeige_upload(e=None):
            dateiname_text = ft.Text("Keine Datei ausgewählt", italic=True, color="grey")

            pfad_feld = ft.TextField(
                label="Oder Pfad manuell eingeben",
                width=500,
                hint_text=r"z.B. C:\Users\...\datei.pdf",
            )

            titel_feld = ft.TextField(label="Titel des Materials", width=420)

            themen = db.themen_laden()
            thema_dropdown = ft.Dropdown(
                label="Themengebiet",
                width=280,
                options=[
                    ft.dropdown.Option(key=str(t["themengebiet_id"]), text=t["name"])
                    for t in themen
                ],
            )

            version_feld = ft.TextField(
                label="Material-ID für neue Version (leer = neues Material)",
                width=420,
                hint_text="z.B. 3",
            )
            status_text = ft.Text("", size=13)

            # Neue FilePicker API in Flet 0.80: async, kein page.overlay nötig
            # Quelle: https://flet.app/gallery/utility/filepicker
            # Kein FLET_SECRET_KEY nötig - wir lesen nur den lokalen Pfad (files[0].path)
            async def datei_auswaehlen(e):
                picker = ft.FilePicker()
                files = await picker.pick_files(allow_multiple=False)
                if not files:
                    return
                f = files[0]
                if f.path:
                    # Desktop: lokaler Pfad direkt verfügbar
                    pfad_feld.value = f.path
                    dateiname_text.value = f.name
                    dateiname_text.color = ft.Colors.BLUE_700
                else:
                    # Web-Modus: Browser gibt keinen lokalen Pfad
                    # Benutzer muss den Server-Pfad manuell eingeben
                    dateiname_text.value = f.name + " (Pfad manuell eingeben)"
                    dateiname_text.color = "orange"
                page.update()

            def hochladen(e):
                quelldatei = pfad_feld.value.strip()
                if not quelldatei:
                    status_text.value = "Bitte eine Datei auswählen oder Pfad eingeben!"
                    status_text.color = "red"
                    page.update()
                    return

                try:
                    mat_id = int(version_feld.value.strip()) if version_feld.value.strip() else None

                    if mat_id is None:
                        if not titel_feld.value.strip():
                            status_text.value = "Bitte einen Titel eingeben!"
                            status_text.color = "red"
                            page.update()
                            return
                        if not thema_dropdown.value:
                            status_text.value = "Bitte ein Themengebiet auswählen!"
                            status_text.color = "red"
                            page.update()
                            return
                        result = db.material_hochladen(
                            quelldatei=quelldatei,
                            autor_id=aktueller_benutzer["id"],
                            titel=titel_feld.value.strip(),
                            thema_id=int(thema_dropdown.value),
                        )
                    else:
                        result = db.material_hochladen(
                            quelldatei=quelldatei,
                            autor_id=aktueller_benutzer["id"],
                            material_id=mat_id,
                        )

                    status_text.value = (
                        "Erfolgreich hochgeladen!  "
                        "Material-ID: " + str(result["material_id"]) +
                        "  |  Version: " + str(result["version"])
                    )
                    status_text.color = "green"
                    page.update()

                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                    status_text.color = "red"
                    page.update()

            seite_laden([
                ft.Text("Material hochladen", size=26, weight=ft.FontWeight.BOLD),
                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=24,
                        content=ft.Column([
                            ft.Text("1. Datei auswählen", size=15, weight=ft.FontWeight.W_600),
                            ft.Row([
                                ft.FilledButton(
                                    "Datei auswählen …",
                                    icon=ft.Icons.ATTACH_FILE,
                                    on_click=datei_auswaehlen,
                                ),
                                dateiname_text,
                            ]),
                            pfad_feld,
                            ft.Text(
                                "Windows: Shift + Rechtsklick auf Datei → 'Als Pfad kopieren'",
                                size=11, color="grey",
                            ),
                            ft.Divider(height=20),
                            ft.Text("2. Informationen", size=15, weight=ft.FontWeight.W_600),
                            titel_feld,
                            thema_dropdown,
                            version_feld,
                            ft.Text(
                                "Wenn eine Material-ID angegeben wird → neue Version.",
                                size=11, color="grey",
                            ),
                            ft.Divider(height=20),
                            ft.Text(
                                "Hochladen als: " + aktueller_benutzer["name"],
                                size=12, color="grey",
                            ),
                            ft.FilledButton(
                                "Hochladen",
                                icon=ft.Icons.CLOUD_UPLOAD,
                                on_click=hochladen,
                            ),
                            status_text,
                        ], spacing=12),
                    ),
                ),
            ])

        # --------------------------------------------------------------
        # Seite: Standardabfragen
        # --------------------------------------------------------------
        def zeige_abfragen(e=None):
            ergebnis = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True)

            def abfrage_starten(index):
                try:
                    titel, beschreibung, zeilen = db.standardabfrage_ausfuehren(index)

                    if not zeilen:
                        ergebnis.controls = [ft.Text("Keine Ergebnisse.", color="grey")]
                        page.update()
                        return

                    spalten = list(zeilen[0].keys())
                    tabelle = ft.DataTable(
                        columns=[ft.DataColumn(ft.Text(s)) for s in spalten],
                        rows=[
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text(str(z.get(s, "")))) for s in spalten
                            ])
                            for z in zeilen
                        ],
                        border=ft.Border(
                            top=ft.BorderSide(1, "#dee2e6"),
                            bottom=ft.BorderSide(1, "#dee2e6"),
                            left=ft.BorderSide(1, "#dee2e6"),
                            right=ft.BorderSide(1, "#dee2e6"),
                        ),
                        border_radius=8,
                        heading_row_color="#e9ecef",
                    )

                    ergebnis.controls = [
                        ft.Text(titel, size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(beschreibung, color="grey", size=13),
                        ft.Text(str(len(zeilen)) + " Zeile(n)", size=12, color="grey"),
                        ft.Divider(height=8),
                        ft.Container(content=tabelle, padding=ft.Padding(top=0, left=0, right=0, bottom=20)),
                    ]
                    page.update()
                except Exception as fehler:
                    ergebnis.controls = [ft.Text("Fehler: " + str(fehler), color="red")]
                    page.update()

            abfrage_liste = ft.Column(spacing=4)
            for i in range(len(db.STANDARDABFRAGEN)):
                a = db.STANDARDABFRAGEN[i]
                n = i
                abfrage_liste.controls.append(
                    ft.ListTile(
                        leading=ft.CircleAvatar(
                            content=ft.Text(str(i + 1), size=13),
                            radius=16,
                            bgcolor=ft.Colors.BLUE_100,
                        ),
                        title=ft.Text(a["titel"], size=13),
                        subtitle=ft.Text(a["beschreibung"], size=11),
                        on_click=lambda e, x=n: abfrage_starten(x),
                        hover_color="#e3f2fd",
                    )
                )

            seite_laden([
                ft.Text("Standardabfragen", size=26, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=abfrage_liste,
                            width=400,
                            padding=10,
                            border=ft.Border(
                                top=ft.BorderSide(1, "#dee2e6"),
                                bottom=ft.BorderSide(1, "#dee2e6"),
                                left=ft.BorderSide(1, "#dee2e6"),
                                right=ft.BorderSide(1, "#dee2e6"),
                            ),
                            border_radius=8,
                            bgcolor=ft.Colors.WHITE,
                        ),
                        ft.VerticalDivider(width=1),
                        ft.Container(
                            content=ergebnis,
                            expand=True,
                            padding=ft.Padding(top=0, left=16, right=0, bottom=0),
                        ),
                    ],
                    expand=True,
                    spacing=0,
                ),
            ])

        # --------------------------------------------------------------
        # Seite: Kommentare
        # --------------------------------------------------------------
        def zeige_kommentare(e=None):
            materialien = db.materialien_laden()
            if len(materialien) == 0:
                seite_laden([ft.Text("Noch keine Materialien vorhanden.", color="grey")])
                return

            material_dropdown = ft.Dropdown(
                label="Material auswählen",
                width=440,
                options=[
                    ft.dropdown.Option(
                        key=str(m["material_id"]),
                        text="[" + str(m["material_id"]) + "] " + m["titel"][:45]
                    )
                    for m in materialien
                ],
            )
            kommentar_feld = ft.TextField(
                label="Neuer Kommentar",
                multiline=True,
                min_lines=3,
                max_lines=5,
                width=520,
            )
            kommentar_liste = ft.Column([], spacing=8)
            status_text = ft.Text("", size=13)

            # Dialog zum Bearbeiten eines Kommentars
            # AlertDialog ist einfacher als inline-Bearbeitung
            edit_dialog_feld = ft.TextField(
                label="Kommentar bearbeiten",
                multiline=True,
                min_lines=3,
                width=420,
            )
            edit_dialog_kid = {"id": None}

            def dialog_speichern(e):
                try:
                    db.kommentar_bearbeiten(edit_dialog_kid["id"], edit_dialog_feld.value)
                    edit_dialog.open = False
                    status_text.value = "Kommentar gespeichert."
                    status_text.color = "green"
                    kommentare_anzeigen()
                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                page.update()

            def dialog_abbrechen(e):
                edit_dialog.open = False
                page.update()

            edit_dialog = ft.AlertDialog(
                title=ft.Text("Kommentar bearbeiten"),
                content=edit_dialog_feld,
                actions=[
                    ft.TextButton("Abbrechen", on_click=dialog_abbrechen),
                    ft.FilledButton("Speichern", on_click=dialog_speichern),
                ],
            )
            page.overlay.append(edit_dialog)

            def kommentare_anzeigen(e=None):
                if not material_dropdown.value:
                    return
                try:
                    kommentare = db.kommentare_laden(int(material_dropdown.value))
                    kommentar_liste.controls.clear()

                    if len(kommentare) == 0:
                        kommentar_liste.controls.append(
                            ft.Text("Noch keine Kommentare.", color="grey", italic=True)
                        )
                    else:
                        for k in kommentare:
                            kid   = k["kommentar_id"]
                            ktext = k["kommentartext"]

                            def bearbeiten(e, k_id=kid, k_text=ktext):
                                edit_dialog_kid["id"]  = k_id
                                edit_dialog_feld.value = k_text
                                edit_dialog.open = True
                                page.update()

                            def loeschen(e, k_id=kid):
                                try:
                                    db.kommentar_loeschen(k_id)
                                    status_text.value = "Kommentar gelöscht."
                                    status_text.color = "green"
                                    kommentare_anzeigen()
                                except Exception as fehler:
                                    status_text.value = "Fehler: " + str(fehler)
                                    page.update()

                            kommentar_liste.controls.append(
                                ft.Card(
                                    elevation=1,
                                    content=ft.Container(
                                        padding=12,
                                        content=ft.Column([
                                            ft.Row([
                                                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=18,
                                                        color=ft.Colors.BLUE_600),
                                                ft.Text(k["autor"],
                                                        weight=ft.FontWeight.BOLD, size=14),
                                                ft.Text(str(k["erstellt_am"])[:16],
                                                        size=11, color="grey"),
                                                ft.IconButton(
                                                    icon=ft.Icons.EDIT_OUTLINED,
                                                    icon_size=16,
                                                    tooltip="Bearbeiten",
                                                    on_click=bearbeiten,
                                                ),
                                                ft.IconButton(
                                                    icon=ft.Icons.DELETE_OUTLINE,
                                                    icon_size=16,
                                                    icon_color=ft.Colors.RED_400,
                                                    tooltip="Löschen",
                                                    on_click=loeschen,
                                                ),
                                            ], spacing=6),
                                            ft.Text(ktext, size=13),
                                        ], spacing=4),
                                    ),
                                )
                            )
                    page.update()
                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                    status_text.color = "red"
                    page.update()

            def kommentar_senden(e):
                if not material_dropdown.value:
                    status_text.value = "Bitte ein Material auswählen!"
                    status_text.color = "red"
                    page.update()
                    return
                if kommentar_feld.value.strip() == "":
                    status_text.value = "Kommentartext darf nicht leer sein!"
                    status_text.color = "red"
                    page.update()
                    return
                try:
                    db.kommentar_speichern(
                        int(material_dropdown.value),
                        aktueller_benutzer["id"],
                        kommentar_feld.value.strip(),
                    )
                    kommentar_feld.value = ""
                    status_text.value = "Kommentar gespeichert!"
                    status_text.color = "green"
                    kommentare_anzeigen()
                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                    status_text.color = "red"
                page.update()

            material_dropdown.on_change = kommentare_anzeigen

            seite_laden([
                ft.Text("Kommentare", size=26, weight=ft.FontWeight.BOLD),
                material_dropdown,
                ft.Container(
                    content=kommentar_liste,
                    padding=ft.Padding(top=8, left=0, right=0, bottom=8),
                ),
                ft.Divider(),
                ft.Text("Neuen Kommentar schreiben", size=15, weight=ft.FontWeight.W_600),
                ft.Text(
                    "Als: " + aktueller_benutzer["name"],
                    size=12, color="grey",
                ),
                kommentar_feld,
                ft.FilledButton("Senden", icon=ft.Icons.SEND, on_click=kommentar_senden),
                status_text,
            ])

        # --------------------------------------------------------------
        # Seite: Themengebiete
        # --------------------------------------------------------------
        def zeige_themen(e=None):
            themen_liste = ft.Column([], spacing=4)
            name_feld        = ft.TextField(label="Name", width=300)
            beschreibung_feld = ft.TextField(label="Beschreibung (optional)", width=400)
            status_text = ft.Text("", size=13)

            def themen_neu_laden():
                themen = db.themen_laden()
                themen_liste.controls.clear()
                for t in themen:
                    beschreibung = t["beschreibung"] if t["beschreibung"] else "–"
                    themen_liste.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.FOLDER_OUTLINED, color=ft.Colors.BLUE_600),
                            title=ft.Text(t["name"]),
                            subtitle=ft.Text(beschreibung, size=12),
                            dense=True,
                        )
                    )
                page.update()

            def thema_anlegen(e):
                if name_feld.value.strip() == "":
                    status_text.value = "Bitte einen Namen eingeben!"
                    status_text.color = "red"
                    page.update()
                    return
                try:
                    neue_id = db.thema_anlegen(
                        name_feld.value.strip(),
                        beschreibung_feld.value.strip()
                    )
                    status_text.value = "Themengebiet angelegt (ID: " + str(neue_id) + ")"
                    status_text.color = "green"
                    name_feld.value = ""
                    beschreibung_feld.value = ""
                    themen_neu_laden()
                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                    status_text.color = "red"
                page.update()

            themen_neu_laden()

            seite_laden([
                ft.Text("Themengebiete", size=26, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Vorhandene Themen", size=15, weight=ft.FontWeight.W_600),
                            themen_liste,
                        ], spacing=6),
                        width=320,
                        padding=14,
                        border=ft.Border(
                            top=ft.BorderSide(1, "#dee2e6"),
                            bottom=ft.BorderSide(1, "#dee2e6"),
                            left=ft.BorderSide(1, "#dee2e6"),
                            right=ft.BorderSide(1, "#dee2e6"),
                        ),
                        border_radius=8,
                        bgcolor=ft.Colors.WHITE,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Neues Thema anlegen", size=15, weight=ft.FontWeight.W_600),
                            name_feld,
                            beschreibung_feld,
                            ft.FilledButton("Anlegen", icon=ft.Icons.ADD, on_click=thema_anlegen),
                            status_text,
                        ], spacing=14),
                        padding=ft.Padding(top=0, left=28, right=0, bottom=0),
                        expand=True,
                    ),
                ], spacing=0, expand=True),
            ])

        # --------------------------------------------------------------
        # Seite: Benutzer
        # --------------------------------------------------------------
        def zeige_benutzer(e=None):
            benutzer_tabelle = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Name")),
                    ft.DataColumn(ft.Text("E-Mail")),
                    ft.DataColumn(ft.Text("Rolle")),
                    ft.DataColumn(ft.Text("Registriert am")),
                ],
                rows=[],
                border=ft.Border(
                    top=ft.BorderSide(1, "#dee2e6"),
                    bottom=ft.BorderSide(1, "#dee2e6"),
                    left=ft.BorderSide(1, "#dee2e6"),
                    right=ft.BorderSide(1, "#dee2e6"),
                ),
                border_radius=8,
                heading_row_color="#e9ecef",
            )

            def benutzer_neu_laden():
                benutzer = db.benutzer_laden()
                benutzer_tabelle.rows.clear()
                for b in benutzer:
                    benutzer_tabelle.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(b["benutzer_id"]))),
                            ft.DataCell(ft.Text(b["anzeigename"])),
                            ft.DataCell(ft.Text(b["email"])),
                            ft.DataCell(ft.Text(b["rolle"])),
                            ft.DataCell(ft.Text(str(b["erstellt_am"])[:10])),
                        ])
                    )
                page.update()

            # Neuen Benutzer anlegen
            rollen = db.rollen_laden()
            name_feld     = ft.TextField(label="Anzeigename", width=280)
            email_feld    = ft.TextField(label="E-Mail",       width=280)
            passwort_feld = ft.TextField(label="Passwort",     width=280, password=True, can_reveal_password=True)
            rollen_dd = ft.Dropdown(
                label="Rolle",
                width=200,
                options=[
                    ft.dropdown.Option(key=str(r["rollen_id"]), text=r["name"])
                    for r in rollen
                ],
            )
            status_text = ft.Text("", size=13)

            def anlegen(e):
                if not name_feld.value.strip() or not email_feld.value.strip() or not passwort_feld.value:
                    status_text.value = "Bitte alle Felder ausfüllen!"
                    status_text.color = "red"
                    page.update()
                    return

                # E-Mail-Validierung
                if not db.email_gueltig(email_feld.value.strip()):
                    status_text.value = "Ungültige E-Mail-Adresse!"
                    status_text.color = "red"
                    page.update()
                    return

                if not rollen_dd.value:
                    status_text.value = "Bitte eine Rolle auswählen!"
                    status_text.color = "red"
                    page.update()
                    return

                try:
                    neue_id = db.benutzer_anlegen(
                        name_feld.value.strip(),
                        email_feld.value.strip(),
                        passwort_feld.value,
                        int(rollen_dd.value),
                    )
                    status_text.value = "Benutzer angelegt (ID: " + str(neue_id) + ")"
                    status_text.color = "green"
                    name_feld.value = ""
                    email_feld.value = ""
                    passwort_feld.value = ""
                    benutzer_neu_laden()
                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                    status_text.color = "red"
                page.update()

            benutzer_neu_laden()

            seite_laden([
                ft.Text("Benutzer", size=26, weight=ft.FontWeight.BOLD),
                ft.Container(content=benutzer_tabelle, padding=ft.Padding(top=0, left=0, right=0, bottom=16)),
                ft.Divider(),
                ft.Text("Neuen Benutzer anlegen", size=15, weight=ft.FontWeight.W_600),
                ft.Row([name_feld, email_feld], spacing=12),
                ft.Row([passwort_feld, rollen_dd], spacing=12),
                ft.FilledButton("Anlegen", icon=ft.Icons.PERSON_ADD, on_click=anlegen),
                status_text,
            ])

        # --------------------------------------------------------------
        # Navigation
        # --------------------------------------------------------------
        def navigation_geaendert(e):
            idx = e.control.selected_index
            if   idx == 0: zeige_materialien()
            elif idx == 1: zeige_upload()
            elif idx == 2: zeige_abfragen()
            elif idx == 3: zeige_kommentare()
            elif idx == 4: zeige_themen()
            elif idx == 5: zeige_benutzer()

        nav = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=105,
            bgcolor=ft.Colors.WHITE,
            on_change=navigation_geaendert,
            leading=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "BBS\nliothek",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        aktueller_benutzer["name"],
                        size=10,
                        color="grey",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=ft.Padding(top=14, left=4, right=4, bottom=4),
            ),
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIBRARY_BOOKS_OUTLINED,
                    selected_icon=ft.Icons.LIBRARY_BOOKS,
                    label="Materialien",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.UPLOAD_FILE_OUTLINED,
                    selected_icon=ft.Icons.UPLOAD_FILE,
                    label="Upload",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.QUERY_STATS_OUTLINED,
                    selected_icon=ft.Icons.QUERY_STATS,
                    label="Abfragen",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.COMMENT_OUTLINED,
                    selected_icon=ft.Icons.COMMENT,
                    label="Kommentare",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FOLDER_OUTLINED,
                    selected_icon=ft.Icons.FOLDER,
                    label="Themen",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE_OUTLINED,
                    selected_icon=ft.Icons.PEOPLE,
                    label="Benutzer",
                ),
            ],
        )

        page.add(
            ft.Row(
                controls=[
                    nav,
                    ft.VerticalDivider(width=1),
                    ft.Container(
                        content=inhalt,
                        expand=True,
                        padding=24,
                        bgcolor="#f8f9fa",
                    ),
                ],
                expand=True,
                spacing=0,
            )
        )
        page.update()
        zeige_materialien()

    # App mit Login starten
    zeige_login()


if __name__ == "__main__":
    # Startmodus bestimmen
    # python main.py        -> Desktop-App
    # python main.py --web  -> Webbrowser (auch vom Handy erreichbar)
    # PORT=8080 python main.py --web -> anderer Port
    if "--web" in sys.argv:
        port = int(os.getenv("PORT", "3000"))
        print("Webbrowser-Modus: http://localhost:" + str(port))
        print("Im lokalen Netzwerk: http://<IP-Adresse>:" + str(port))
        ft.run(main, view=ft.AppView.WEB_BROWSER, port=port)
    else:
        ft.run(main)
