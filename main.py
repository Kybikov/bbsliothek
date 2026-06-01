# BBSliothek - Lernmaterialverwaltung
# Flet Dokumentation: https://flet.dev/docs/
# Getting Started Guide: https://flet.dev/docs/getting-started/

import flet as ft
import datenbank as db
import os

# TODO: Login-System mit echten Benutzern implementieren
# Momentan wird einfach der erste Benutzer aus der DB verwendet


def main(page: ft.Page):
    # Grundeinstellungen der Seite
    # Quelle: https://flet.dev/docs/controls/page/
    page.title = "BBSliothek – Lernmaterialverwaltung"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0
    page.bgcolor = "#f8f9fa"

    # Haupt-Inhaltsbereich (rechts von der Navigation)
    inhalt = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=10)

    def seite_laden(controls):
        # Inhalt aktualisieren und Seite neu zeichnen
        inhalt.controls.clear()
        inhalt.controls.extend(controls)
        page.update()

    # ==================================================================
    # Seite: Materialien anzeigen und herunterladen
    # ==================================================================
    def zeige_materialien(e=None):
        titel_feld = ft.TextField(label="Suche nach Titel", width=260, dense=True)
        typ_feld = ft.TextField(label="Dateityp (z.B. .pdf)", width=200, dense=True)
        status_text = ft.Text("", size=13)

        # DataTable laut Flet Dokumentation
        # Quelle: https://flet.dev/docs/controls/datatable/
        tabelle = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Titel")),
                ft.DataColumn(ft.Text("Typ")),
                ft.DataColumn(ft.Text("Thema")),
                ft.DataColumn(ft.Text("Autor")),
                ft.DataColumn(ft.Text("Version")),
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
            column_spacing=20,
        )

        def tabelle_fuellen(titel=None, dateityp=None):
            try:
                # Materialien aus der Datenbank laden
                materialien = db.materialien_laden(titel=titel, dateityp=dateityp)
                tabelle.rows.clear()

                for m in materialien:
                    # Dateigröße in KB umrechnen
                    kb = round(m["dateigroesse_bytes"] / 1024, 1)
                    mid = m["material_id"]

                    tabelle.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(m["material_id"]))),
                            ft.DataCell(ft.Text(m["titel"][:35])),
                            ft.DataCell(ft.Text(m["dateityp"])),
                            ft.DataCell(ft.Text(m["themengebiet"][:20])),
                            ft.DataCell(ft.Text(m["autor"][:20])),
                            ft.DataCell(ft.Text(str(m["version"]))),
                            ft.DataCell(ft.Text(str(kb) + " KB")),
                            ft.DataCell(
                                # Download-Button für jede Zeile
                                ft.IconButton(
                                    icon=ft.Icons.DOWNLOAD_OUTLINED,
                                    tooltip="Herunterladen",
                                    icon_color=ft.Colors.BLUE_600,
                                    on_click=lambda e, x=mid: datei_herunterladen(x),
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

        def datei_herunterladen(material_id):
            try:
                pfad = db.material_herunterladen(material_id)
                status_text.value = "Gespeichert: " + pfad
                status_text.color = "green"
                page.update()
                # Datei automatisch öffnen (nur Windows)
                # Auf Linux/Mac: subprocess.run(["xdg-open", pfad])
                os.startfile(pfad)
            except Exception as fehler:
                status_text.value = "Fehler beim Download: " + str(fehler)
                status_text.color = "red"
                page.update()

        def suchen_geklickt(e):
            tabelle_fuellen(
                titel=titel_feld.value if titel_feld.value else None,
                dateityp=typ_feld.value if typ_feld.value else None
            )

        def filter_zuruecksetzen(e):
            titel_feld.value = ""
            typ_feld.value = ""
            tabelle_fuellen()

        # Beim ersten Laden alle Materialien anzeigen
        tabelle_fuellen()

        seite_laden([
            ft.Text("Lernmaterialien", size=26, weight=ft.FontWeight.BOLD),
            ft.Row([
                titel_feld,
                typ_feld,
                ft.FilledButton("Suchen", icon=ft.Icons.SEARCH, on_click=suchen_geklickt),
                ft.TextButton("Zurücksetzen", on_click=filter_zuruecksetzen),
            ], spacing=10),
            status_text,
            ft.Container(content=tabelle, padding=ft.Padding(top=8, left=0, right=0, bottom=0)),
        ])

    # ==================================================================
    # Seite: Material hochladen
    # ==================================================================
    def zeige_upload(e=None):
        # Dictionary um den Dateipfad zu speichern
        # (normale Variable würde in der Closure nicht funktionieren)
        datei_info = {"pfad": None}
        dateiname_text = ft.Text("Keine Datei ausgewählt", italic=True, color="grey")

        titel_feld = ft.TextField(label="Titel des Materials", width=420)

        # Themengebiete für Dropdown laden
        themen = db.themen_laden()
        thema_dropdown = ft.Dropdown(
            label="Themengebiet",
            width=300,
            options=[
                ft.dropdown.Option(key=str(t["themengebiet_id"]), text=t["name"])
                for t in themen
            ],
        )

        # Benutzer für Dropdown laden
        benutzer_liste = db.benutzer_laden()
        autor_dropdown = ft.Dropdown(
            label="Autor",
            width=300,
            options=[
                ft.dropdown.Option(key=str(b["benutzer_id"]), text=b["anzeigename"])
                for b in benutzer_liste
            ],
        )

        version_feld = ft.TextField(
            label="Material-ID für neue Version (leer = neues Material anlegen)",
            width=420,
            hint_text="z.B. 3",
        )
        status_text = ft.Text("", size=13)

        # FilePicker muss zu page.overlay hinzugefügt werden
        # Quelle: https://flet.dev/docs/controls/filepicker/
        # Hinweis: on_result kann nicht im Konstruktor übergeben werden (TypeError),
        # sondern muss nach der Erstellung als Eigenschaft gesetzt werden
        def datei_ausgewaehlt(e: ft.FilePickerResultEvent):
            if e.files:
                datei_info["pfad"] = e.files[0].path
                dateiname_text.value = e.files[0].name
                dateiname_text.color = ft.Colors.BLUE_700
                page.update()

        file_picker = ft.FilePicker()
        file_picker.on_result = datei_ausgewaehlt
        page.overlay.append(file_picker)
        page.update()

        def hochladen_geklickt(e):
            # Eingaben überprüfen bevor Upload startet
            if datei_info["pfad"] is None:
                status_text.value = "Bitte zuerst eine Datei auswählen!"
                status_text.color = "red"
                page.update()
                return

            if not autor_dropdown.value:
                status_text.value = "Bitte einen Autor auswählen!"
                status_text.color = "red"
                page.update()
                return

            try:
                autor_id = int(autor_dropdown.value)

                # Prüfen ob neue Version oder neues Material
                if version_feld.value.strip() == "":
                    mat_id = None
                else:
                    mat_id = int(version_feld.value.strip())

                if mat_id is None:
                    # Neues Material hochladen
                    if titel_feld.value.strip() == "":
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
                        quelldatei=datei_info["pfad"],
                        autor_id=autor_id,
                        titel=titel_feld.value.strip(),
                        thema_id=int(thema_dropdown.value),
                    )
                else:
                    # Neue Version eines bestehenden Materials hochladen
                    result = db.material_hochladen(
                        quelldatei=datei_info["pfad"],
                        autor_id=autor_id,
                        material_id=mat_id,
                    )

                status_text.value = (
                    "Erfolgreich hochgeladen!  "
                    "Material-ID: " + str(result["material_id"]) + "  |  "
                    "Version: " + str(result["version"]) + "  |  "
                    "Strategie: " + result["strategie"]
                )
                status_text.color = "green"
                page.update()

            except Exception as fehler:
                status_text.value = "Fehler beim Upload: " + str(fehler)
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
                                "Datei auswählen ...",
                                icon=ft.Icons.ATTACH_FILE,
                                on_click=lambda e: file_picker.pick_files(),
                            ),
                            dateiname_text,
                        ]),
                        ft.Divider(height=20),
                        ft.Text("2. Informationen eingeben", size=15, weight=ft.FontWeight.W_600),
                        titel_feld,
                        ft.Row([thema_dropdown, autor_dropdown], spacing=20),
                        version_feld,
                        ft.Text(
                            "Wenn eine Material-ID angegeben wird, wird eine neue Version erstellt.",
                            size=12,
                            color="grey",
                        ),
                        ft.Divider(height=20),
                        ft.FilledButton(
                            "Hochladen",
                            icon=ft.Icons.CLOUD_UPLOAD,
                            on_click=hochladen_geklickt,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_700,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                        status_text,
                    ], spacing=14),
                ),
            ),
        ])

    # ==================================================================
    # Seite: Standardabfragen ausführen
    # ==================================================================
    def zeige_abfragen(e=None):
        # Ergebnisbereich rechts
        ergebnis_bereich = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True)

        def abfrage_ausfuehren(index):
            try:
                titel, beschreibung, zeilen = db.standardabfrage_ausfuehren(index)

                if not zeilen:
                    ergebnis_bereich.controls = [
                        ft.Text("Keine Ergebnisse gefunden.", color="grey")
                    ]
                    page.update()
                    return

                # Spaltenüberschriften aus den Dictionary-Keys holen
                spalten_namen = list(zeilen[0].keys())

                tabelle = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text(s)) for s in spalten_namen],
                    rows=[
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(z.get(s, "")))) for s in spalten_namen
                            ]
                        )
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

                ergebnis_bereich.controls = [
                    ft.Text(titel, size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(beschreibung, color="grey", size=13),
                    ft.Text(str(len(zeilen)) + " Zeile(n)", size=12, color="grey"),
                    ft.Divider(height=10),
                    ft.Container(content=tabelle, padding=ft.Padding(top=0, left=0, right=0, bottom=20)),
                ]
                page.update()

            except Exception as fehler:
                ergebnis_bereich.controls = [
                    ft.Text("Fehler: " + str(fehler), color="red")
                ]
                page.update()

        # Liste mit allen 7 Abfragen als klickbare Elemente
        abfrage_liste = ft.Column(spacing=4)
        for i in range(len(db.STANDARDABFRAGEN)):
            a = db.STANDARDABFRAGEN[i]
            # i in eigene Variable kopieren sonst haben alle Buttons den letzten Wert
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
                    on_click=lambda e, x=n: abfrage_ausfuehren(x),
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
                        content=ergebnis_bereich,
                        expand=True,
                        padding=ft.Padding(top=0, left=16, right=0, bottom=0),
                    ),
                ],
                expand=True,
                spacing=0,
            ),
        ])

    # ==================================================================
    # Seite: Kommentare anzeigen und hinzufügen
    # ==================================================================
    def zeige_kommentare(e=None):
        materialien = db.materialien_laden()
        benutzer_liste = db.benutzer_laden()

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
        autor_dropdown = ft.Dropdown(
            label="Dein Name",
            width=260,
            options=[
                ft.dropdown.Option(key=str(b["benutzer_id"]), text=b["anzeigename"])
                for b in benutzer_liste
            ],
        )
        kommentar_feld = ft.TextField(
            label="Kommentar schreiben",
            multiline=True,
            min_lines=3,
            max_lines=6,
            width=520,
        )
        kommentar_liste = ft.Column([], spacing=8)
        status_text = ft.Text("", size=13)

        def kommentare_anzeigen(e=None):
            if not material_dropdown.value:
                return
            try:
                kommentare = db.kommentare_laden(int(material_dropdown.value))
                kommentar_liste.controls.clear()

                if len(kommentare) == 0:
                    kommentar_liste.controls.append(
                        ft.Text(
                            "Noch keine Kommentare für dieses Material.",
                            color="grey",
                            italic=True,
                        )
                    )
                else:
                    for k in kommentare:
                        # Jeder Kommentar als eigene Card
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
                                            ft.Text(
                                                str(k["erstellt_am"])[:16],
                                                size=11,
                                                color="grey",
                                            ),
                                        ], spacing=6),
                                        ft.Text(k["kommentartext"], size=13),
                                    ], spacing=4),
                                ),
                            )
                        )

                page.update()

            except Exception as fehler:
                status_text.value = "Fehler: " + str(fehler)
                status_text.color = "red"
                page.update()

        def kommentar_absenden(e):
            if not material_dropdown.value:
                status_text.value = "Bitte ein Material auswählen!"
                status_text.color = "red"
                page.update()
                return
            if not autor_dropdown.value:
                status_text.value = "Bitte deinen Namen auswählen!"
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
                    int(autor_dropdown.value),
                    kommentar_feld.value.strip(),
                )
                kommentar_feld.value = ""
                status_text.value = "Kommentar gespeichert!"
                status_text.color = "green"
                # Kommentarliste neu laden
                kommentare_anzeigen()

            except Exception as fehler:
                status_text.value = "Fehler: " + str(fehler)
                status_text.color = "red"

            page.update()

        # Kommentare automatisch laden wenn Material ausgewählt wird
        material_dropdown.on_change = kommentare_anzeigen

        seite_laden([
            ft.Text("Kommentare", size=26, weight=ft.FontWeight.BOLD),
            material_dropdown,
            ft.Container(
                content=kommentar_liste,
                padding=ft.Padding(top=8, left=0, right=0, bottom=8),
            ),
            ft.Divider(),
            ft.Text("Neuen Kommentar hinzufügen", size=15, weight=ft.FontWeight.W_600),
            autor_dropdown,
            kommentar_feld,
            ft.FilledButton(
                "Kommentar senden",
                icon=ft.Icons.SEND,
                on_click=kommentar_absenden,
            ),
            status_text,
        ])

    # ==================================================================
    # Seite: Themengebiete verwalten
    # ==================================================================
    def zeige_themen(e=None):
        themen_liste = ft.Column([], spacing=4)
        name_feld = ft.TextField(label="Name des Themengebiets", width=300)
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

        def thema_anlegen_geklickt(e):
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
                    width=340,
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
                        ft.Text("Neues Themengebiet anlegen", size=15,
                                weight=ft.FontWeight.W_600),
                        name_feld,
                        beschreibung_feld,
                        ft.FilledButton("Anlegen", icon=ft.Icons.ADD,
                                         on_click=thema_anlegen_geklickt),
                        status_text,
                    ], spacing=14),
                    padding=ft.Padding(top=0, left=30, right=0, bottom=0),
                    expand=True,
                ),
            ], spacing=0, expand=True),
        ])

    # ==================================================================
    # Navigation (NavigationRail)
    # Quelle: https://flet.dev/docs/controls/navigationrail/
    # ==================================================================
    def navigation_geaendert(e):
        index = e.control.selected_index
        if index == 0:
            zeige_materialien()
        elif index == 1:
            zeige_upload()
        elif index == 2:
            zeige_abfragen()
        elif index == 3:
            zeige_kommentare()
        elif index == 4:
            zeige_themen()

    nav = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=105,
        bgcolor=ft.Colors.WHITE,
        on_change=navigation_geaendert,
        leading=ft.Container(
            content=ft.Text(
                "BBS\nliothek",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_700,
                text_align=ft.TextAlign.CENTER,
            ),
            padding=ft.Padding(top=16, left=0, right=0, bottom=8),
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
        ],
    )

    # Layout: Navigation links, Inhalt rechts
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

    # Startseite anzeigen
    zeige_materialien()


if __name__ == "__main__":
    ft.run(main)
