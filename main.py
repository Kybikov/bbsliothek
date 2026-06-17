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
    page.window.width = 1200
    page.window.height = 800
    page.padding = 0

    theme_state = {"dark": False}
    ansicht = {"index": 0}

    def farben():
        if theme_state["dark"]:
            return {
                "bg": "#111827",
                "surface": "#1f2937",
                "surface_soft": "#273447",
                "border": "#374151",
                "text": "#f9fafb",
                "muted": "#cbd5e1",
                "primary": ft.Colors.BLUE_300,
                "primary_soft": "#1e3a5f",
                "table_head": "#253244",
            }
        return {
            "bg": "#f8f9fa",
            "surface": ft.Colors.WHITE,
            "surface_soft": "#f1f5f9",
            "border": "#dee2e6",
            "text": "#111827",
            "muted": "#6b7280",
            "primary": ft.Colors.BLUE_700,
            "primary_soft": "#e3f2fd",
            "table_head": "#e9ecef",
        }

    def theme_anwenden():
        c = farben()
        page.theme_mode = ft.ThemeMode.DARK if theme_state["dark"] else ft.ThemeMode.LIGHT
        page.bgcolor = c["bg"]

    def ist_mobil():
        breite = page.width or page.window.width or 1200
        return breite < 760

    def feld_breite(max_breite):
        if not ist_mobil():
            return max_breite
        breite = page.width or 360
        return max(260, min(max_breite, breite - 32))

    def responsive_row(controls, spacing=8, **kwargs):
        return ft.Row(
            controls=controls,
            spacing=spacing,
            run_spacing=spacing,
            wrap=True,
            **kwargs,
        )

    def tabellen_container(tabelle, bottom=0):
        return ft.Container(
            content=ft.Row([tabelle], scroll=ft.ScrollMode.AUTO),
            padding=ft.Padding(top=8, left=0, right=0, bottom=bottom),
        )

    def rahmen():
        c = farben()
        return ft.Border(
            top=ft.BorderSide(1, c["border"]),
            bottom=ft.BorderSide(1, c["border"]),
            left=ft.BorderSide(1, c["border"]),
            right=ft.BorderSide(1, c["border"]),
        )

    def text_muted(wert, size=None, italic=False):
        return ft.Text(wert, color=farben()["muted"], size=size, italic=italic)

    theme_anwenden()

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
        theme_anwenden()
        c = farben()

        benutzername_feld = ft.TextField(label="Benutzername", width=feld_breite(320))
        passwort_feld = ft.TextField(
            label="Passwort",
            password=True,
            can_reveal_password=True,
            width=feld_breite(320),
        )
        fehler_text = ft.Text("", color="red", size=13)

        def theme_wechseln(e):
            theme_state["dark"] = not theme_state["dark"]
            zeige_login()

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
                            color=c["primary"]),
                    text_muted("Lernmaterialverwaltung", size=16),
                    ft.Divider(height=30, color="transparent"),
                    ft.Card(
                        elevation=3,
                        bgcolor=c["surface"],
                        content=ft.Container(
                            padding=32,
                            width=feld_breite(380),
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Anmelden", size=20, weight=ft.FontWeight.W_600),
                                    ft.IconButton(
                                        icon=ft.Icons.LIGHT_MODE_OUTLINED if theme_state["dark"] else ft.Icons.DARK_MODE_OUTLINED,
                                        tooltip="Theme wechseln",
                                        on_click=theme_wechseln,
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Divider(height=10, color="transparent"),
                                benutzername_feld,
                                passwort_feld,
                                fehler_text,
                                ft.FilledButton(
                                    "Anmelden",
                                    icon=ft.Icons.LOGIN,
                                    on_click=anmelden,
                                    width=feld_breite(320),
                                ),
                            ], spacing=12),
                        ),
                    ),
                    text_muted("Benutzername / Passwort: azubi123", size=11),
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
    def zeige_hauptansicht(start_index=0):
        ansicht["index"] = start_index
        page.clean()
        theme_anwenden()
        c = farben()

        inhalt = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=10)

        def seite_laden(controls):
            inhalt.controls.clear()
            inhalt.controls.extend(controls)
            page.update()

        # --------------------------------------------------------------
        # Seite: Materialien
        # --------------------------------------------------------------
        def zeige_materialien(e=None):
            titel_feld  = ft.TextField(label="Titel / Dateiname", width=feld_breite(220), dense=True)
            typ_feld    = ft.TextField(label="Dateityp (.pdf …)", width=feld_breite(160), dense=True)
            status_text = ft.Text("", size=13)

            # Autor-Filter Dropdown
            benutzer_liste = db.benutzer_laden()
            autor_filter = ft.Dropdown(
                label="Autor",
                width=feld_breite(180),
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
                    ft.DataColumn(ft.Text("Größe")),
                    ft.DataColumn(ft.Text("Aktionen")),
                ],
                rows=[],
                border=rahmen(),
                border_radius=8,
                vertical_lines=ft.BorderSide(1, c["border"]),
                heading_row_color=c["table_head"],
                column_spacing=16,
            )

            # Dialog: neue Version hochladen
            neueversion_pfad_feld = ft.TextField(label="Pfad zur neuen Datei", width=feld_breite(400))
            neueversion_mat_id = {"id": None}

            def neueversion_speichern(e):
                pfad = neueversion_pfad_feld.value.strip()
                if not pfad:
                    return
                try:
                    result = db.material_hochladen(pfad, aktueller_benutzer["id"], material_id=neueversion_mat_id["id"])
                    status_text.value = "Version " + str(result["version"]) + " gespeichert!"
                    status_text.color = "green"
                    neueversion_dialog.open = False
                    neueversion_pfad_feld.value = ""
                    tabelle_fuellen()
                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                    status_text.color = "red"
                page.update()

            def neueversion_abbrechen(e):
                neueversion_dialog.open = False
                page.update()

            neueversion_dialog = ft.AlertDialog(
                title=ft.Text("Neue Version hochladen"),
                content=neueversion_pfad_feld,
                actions=[
                    ft.TextButton("Abbrechen", on_click=neueversion_abbrechen),
                    ft.FilledButton("Hochladen", on_click=neueversion_speichern),
                ],
            )
            page.overlay.append(neueversion_dialog)

            # Dialog: löschen bestätigen
            loeschen_mat_id = {"id": None}

            def loeschen_bestaetigen(e):
                try:
                    db.material_loeschen(loeschen_mat_id["id"])
                    status_text.value = "Material gelöscht."
                    status_text.color = "green"
                    loeschen_dialog.open = False
                    tabelle_fuellen()
                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                    status_text.color = "red"
                page.update()

            def loeschen_abbrechen(e):
                loeschen_dialog.open = False
                page.update()

            loeschen_dialog = ft.AlertDialog(
                title=ft.Text("Material löschen?"),
                content=ft.Text("Alle Versionen und Kommentare werden gelöscht."),
                actions=[
                    ft.TextButton("Abbrechen", on_click=loeschen_abbrechen),
                    ft.FilledButton(
                        "Löschen",
                        on_click=loeschen_bestaetigen,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400),
                    ),
                ],
            )
            page.overlay.append(loeschen_dialog)

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
                                ft.DataCell(ft.Text(str(kb) + " KB")),
                                ft.DataCell(
                                    ft.Row([
                                        ft.IconButton(
                                            icon=ft.Icons.DOWNLOAD_OUTLINED,
                                            tooltip="Herunterladen",
                                            icon_color=ft.Colors.BLUE_600,
                                            on_click=lambda e, x=mid: herunterladen(x),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.UPLOAD_FILE_OUTLINED,
                                            tooltip="Neue Version",
                                            icon_color=ft.Colors.GREEN_600,
                                            on_click=lambda e, x=mid: neue_version_oeffnen(x),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            tooltip="Löschen",
                                            icon_color=ft.Colors.RED_400,
                                            on_click=lambda e, x=mid: loeschen_oeffnen(x),
                                        ),
                                    ], spacing=0)
                                ),
                            ])
                        )

                    status_text.value = str(len(materialien)) + " Ergebnis(se)"
                    status_text.color = c["muted"]
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

            def neue_version_oeffnen(material_id):
                neueversion_mat_id["id"] = material_id
                neueversion_pfad_feld.value = ""
                neueversion_dialog.open = True
                page.update()

            def loeschen_oeffnen(material_id):
                loeschen_mat_id["id"] = material_id
                loeschen_dialog.open = True
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
                responsive_row([
                    titel_feld,
                    typ_feld,
                    autor_filter,
                    ft.FilledButton("Suchen", icon=ft.Icons.SEARCH, on_click=suchen),
                    ft.TextButton("Zurücksetzen", on_click=zuruecksetzen),
                ], spacing=8),
                status_text,
                tabellen_container(tabelle),
            ])

        # --------------------------------------------------------------
        # Seite: Upload
        # --------------------------------------------------------------
        def zeige_upload(e=None):
            dateiname_text = text_muted("Keine Datei ausgewählt", italic=True)

            pfad_feld = ft.TextField(
                label="Oder Pfad manuell eingeben",
                width=feld_breite(500),
                hint_text=r"z.B. C:\Users\...\datei.pdf",
            )

            titel_feld = ft.TextField(label="Titel des Materials", width=feld_breite(420))

            themen = db.themen_laden()
            thema_dropdown = ft.Dropdown(
                label="Themengebiet",
                width=feld_breite(280),
                options=[
                    ft.dropdown.Option(key=str(t["themengebiet_id"]), text=t["name"])
                    for t in themen
                ],
            )

            status_text = ft.Text("", size=13)

            async def datei_auswaehlen(e):
                picker = ft.FilePicker()
                files = await picker.pick_files(allow_multiple=False)
                if not files:
                    return
                f = files[0]
                if f.path:
                    pfad_feld.value = f.path
                    dateiname_text.value = f.name
                    dateiname_text.color = c["primary"]
                else:
                    # Web-Modus: Browser gibt keinen lokalen Pfad zurück
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
                try:
                    result = db.material_hochladen(
                        quelldatei,
                        aktueller_benutzer["id"],
                        titel=titel_feld.value.strip(),
                        thema_id=int(thema_dropdown.value),
                    )
                    status_text.value = "Gespeichert! Material-ID: " + str(result["material_id"])
                    status_text.color = "green"
                    titel_feld.value = ""
                    pfad_feld.value = ""
                    page.update()
                except Exception as fehler:
                    status_text.value = "Fehler: " + str(fehler)
                    status_text.color = "red"
                    page.update()

            seite_laden([
                ft.Text("Neues Material hochladen", size=26, weight=ft.FontWeight.BOLD),
                text_muted("Neue Version eines bestehenden Materials → Materialien → Upload-Symbol", size=12),
                ft.Card(
                    elevation=2,
                    bgcolor=c["surface"],
                    content=ft.Container(
                        padding=24,
                        content=ft.Column([
                            responsive_row([
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
                                size=11, color=c["muted"],
                            ),
                            ft.Divider(height=10),
                            titel_feld,
                            thema_dropdown,
                            ft.Text(
                                "Hochladen als: " + aktueller_benutzer["name"],
                                size=12, color=c["muted"],
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
                        border=rahmen(),
                        border_radius=8,
                        heading_row_color=c["table_head"],
                    )

                    ergebnis.controls = [
                        ft.Text(titel, size=18, weight=ft.FontWeight.BOLD),
                        text_muted(beschreibung, size=13),
                        text_muted(str(len(zeilen)) + " Zeile(n)", size=12),
                        ft.Divider(height=8),
                        tabellen_container(tabelle, bottom=20),
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
                            bgcolor=c["primary_soft"],
                        ),
                        title=ft.Text(a["titel"], size=13),
                        subtitle=ft.Text(a["beschreibung"], size=11),
                        on_click=lambda e, x=n: abfrage_starten(x),
                        hover_color=c["primary_soft"],
                    )
                )

            abfragen_layout = ft.Column if ist_mobil() else ft.Row
            seite_laden([
                ft.Text("Standardabfragen", size=26, weight=ft.FontWeight.BOLD),
                abfragen_layout(
                    controls=[
                        ft.Container(
                            content=abfrage_liste,
                            width=feld_breite(400),
                            padding=10,
                            border=rahmen(),
                            border_radius=8,
                            bgcolor=c["surface"],
                        ),
                        ft.VerticalDivider(width=1) if not ist_mobil() else ft.Divider(height=1),
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
                seite_laden([text_muted("Noch keine Materialien vorhanden.")])
                return

            material_dropdown = ft.Dropdown(
                label="Material auswählen",
                width=feld_breite(440),
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
                width=feld_breite(520),
            )
            kommentar_liste = ft.Column([], spacing=8)
            status_text = ft.Text("", size=13)

            # Dialog zum Bearbeiten eines Kommentars
            # AlertDialog ist einfacher als inline-Bearbeitung
            edit_dialog_feld = ft.TextField(
                label="Kommentar bearbeiten",
                multiline=True,
                min_lines=3,
                width=feld_breite(420),
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
                            text_muted("Noch keine Kommentare.", italic=True)
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
                                    bgcolor=c["surface"],
                                    content=ft.Container(
                                        padding=12,
                                        content=ft.Column([
                                            ft.Row([
                                                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=18,
                                                        color=c["primary"]),
                                                ft.Text(k["autor"],
                                                        weight=ft.FontWeight.BOLD, size=14),
                                                ft.Text(str(k["erstellt_am"])[:16],
                                                        size=11, color=c["muted"]),
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
                text_muted("Als: " + aktueller_benutzer["name"], size=12),
                kommentar_feld,
                ft.FilledButton("Senden", icon=ft.Icons.SEND, on_click=kommentar_senden),
                status_text,
            ])

        # --------------------------------------------------------------
        # Seite: Themengebiete
        # --------------------------------------------------------------
        def zeige_themen(e=None):
            themen_liste = ft.Column([], spacing=4)
            name_feld        = ft.TextField(label="Name", width=feld_breite(300))
            beschreibung_feld = ft.TextField(label="Beschreibung (optional)", width=feld_breite(400))
            status_text = ft.Text("", size=13)

            def themen_neu_laden():
                themen = db.themen_mit_anzahl()
                themen_liste.controls.clear()
                for t in themen:
                    themen_liste.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.FOLDER_OUTLINED, color=c["primary"]),
                            title=ft.Text(t["name"]),
                            subtitle=ft.Text(str(t["anzahl_materialien"]) + " Materialien", size=12),
                            trailing=ft.IconButton(
                                icon=ft.Icons.ARROW_FORWARD_IOS,
                                icon_size=14,
                                tooltip="Materialien anzeigen",
                                on_click=lambda e, tid=t["themengebiet_id"]: zeige_materialien_nach_thema(tid),
                            ),
                            dense=True,
                        )
                    )
                page.update()

            def zeige_materialien_nach_thema(thema_id):
                zeilen = db.materialien_laden(thema_id=thema_id)
                status_text.value = str(len(zeilen)) + " Materialien in diesem Thema"
                status_text.color = c["muted"]
                # Materialien-Seite mit Filter öffnen
                zeige_materialien()
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
                responsive_row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Vorhandene Themen", size=15, weight=ft.FontWeight.W_600),
                            themen_liste,
                        ], spacing=6),
                        width=feld_breite(320),
                        padding=14,
                        border=rahmen(),
                        border_radius=8,
                        bgcolor=c["surface"],
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Neues Thema anlegen", size=15, weight=ft.FontWeight.W_600),
                            name_feld,
                            beschreibung_feld,
                            ft.FilledButton("Anlegen", icon=ft.Icons.ADD, on_click=thema_anlegen),
                            status_text,
                        ], spacing=14),
                        padding=ft.Padding(top=0, left=0 if ist_mobil() else 28, right=0, bottom=0),
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
                    ft.DataColumn(ft.Text("Name")),
                    ft.DataColumn(ft.Text("Rolle")),
                    ft.DataColumn(ft.Text("Materialien")),
                ],
                rows=[],
                border=rahmen(),
                border_radius=8,
                heading_row_color=c["table_head"],
            )

            def benutzer_neu_laden():
                benutzer_liste = db.benutzer_mit_anzahl()
                benutzer_tabelle.rows.clear()
                for b in benutzer_liste:
                    benutzer_tabelle.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(b["name"])),
                            ft.DataCell(ft.Text(b["rolle"])),
                            ft.DataCell(ft.Text(str(b["anzahl_materialien"]))),
                        ])
                    )
                page.update()

            # Neuen Benutzer anlegen
            rollen = db.rollen_laden()
            name_feld     = ft.TextField(label="Vorname",  width=feld_breite(180))
            nachname_feld = ft.TextField(label="Nachname", width=feld_breite(180))
            email_feld    = ft.TextField(label="E-Mail",   width=feld_breite(280))
            passwort_feld = ft.TextField(label="Passwort", width=feld_breite(280), password=True, can_reveal_password=True)
            rollen_dd = ft.Dropdown(
                label="Rolle",
                width=feld_breite(200),
                options=[
                    ft.dropdown.Option(key=str(r["rollen_id"]), text=r["name"])
                    for r in rollen
                ],
            )
            status_text = ft.Text("", size=13)

            def anlegen(e):
                if not name_feld.value.strip() or not nachname_feld.value.strip() or not email_feld.value.strip() or not passwort_feld.value:
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
                        nachname_feld.value.strip(),
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
                tabellen_container(benutzer_tabelle, bottom=16),
                ft.Divider(),
                ft.Text("Neuen Benutzer anlegen", size=15, weight=ft.FontWeight.W_600),
                responsive_row([name_feld, nachname_feld], spacing=12),
                responsive_row([email_feld], spacing=12),
                responsive_row([passwort_feld, rollen_dd], spacing=12),
                ft.FilledButton("Anlegen", icon=ft.Icons.PERSON_ADD, on_click=anlegen),
                status_text,
            ])

        # --------------------------------------------------------------
        # Navigation
        # --------------------------------------------------------------
        def bereich_anzeigen(idx):
            ansicht["index"] = idx
            if   idx == 0: zeige_materialien()
            elif idx == 1: zeige_upload()
            elif idx == 2: zeige_kommentare()
            elif idx == 3: zeige_themen()
            elif idx == 4: zeige_benutzer()

        def navigation_geaendert(e):
            bereich_anzeigen(e.control.selected_index)

        def theme_wechseln(e):
            theme_state["dark"] = not theme_state["dark"]
            zeige_hauptansicht(ansicht["index"])

        def bei_resize(e):
            zeige_hauptansicht(ansicht["index"])

        page.on_resize = bei_resize

        theme_button = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE_OUTLINED if theme_state["dark"] else ft.Icons.DARK_MODE_OUTLINED,
            tooltip="Theme wechseln",
            on_click=theme_wechseln,
        )

        nav = ft.NavigationRail(
            selected_index=ansicht["index"],
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=105,
            bgcolor=c["surface"],
            on_change=navigation_geaendert,
            leading=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "BBS\nliothek",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=c["primary"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(aktueller_benutzer["name"], size=10, color=c["muted"], text_align=ft.TextAlign.CENTER),
                    theme_button,
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

        content = ft.Container(
            content=inhalt,
            expand=True,
            padding=16 if ist_mobil() else 24,
            bgcolor=c["bg"],
        )

        if ist_mobil():
            mobile_nav = ft.NavigationBar(
                selected_index=ansicht["index"],
                bgcolor=c["surface"],
                on_change=navigation_geaendert,
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.LIBRARY_BOOKS_OUTLINED, selected_icon=ft.Icons.LIBRARY_BOOKS, label="Material"),
                    ft.NavigationBarDestination(icon=ft.Icons.UPLOAD_FILE_OUTLINED, selected_icon=ft.Icons.UPLOAD_FILE, label="Upload"),
                    ft.NavigationBarDestination(icon=ft.Icons.COMMENT_OUTLINED, selected_icon=ft.Icons.COMMENT, label="Kommentare"),
                    ft.NavigationBarDestination(icon=ft.Icons.FOLDER_OUTLINED, selected_icon=ft.Icons.FOLDER, label="Themen"),
                    ft.NavigationBarDestination(icon=ft.Icons.PEOPLE_OUTLINED, selected_icon=ft.Icons.PEOPLE, label="Benutzer"),
                ],
            )
            page.add(
                ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor=c["surface"],
                            padding=ft.Padding(top=10, left=16, right=8, bottom=8),
                            content=ft.Row(
                                controls=[
                                    ft.Column([
                                        ft.Text("BBSliothek", size=18, weight=ft.FontWeight.BOLD, color=c["primary"]),
                                        ft.Text(aktueller_benutzer["name"], size=11, color=c["muted"]),
                                    ], spacing=0),
                                    theme_button,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ),
                        content,
                        mobile_nav,
                    ],
                    expand=True,
                    spacing=0,
                )
            )
        else:
            page.add(
                ft.Row(
                    controls=[
                        nav,
                        ft.VerticalDivider(width=1),
                        content,
                    ],
                    expand=True,
                    spacing=0,
                )
            )
        page.update()
        bereich_anzeigen(ansicht["index"])

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
