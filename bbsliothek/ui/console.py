from __future__ import annotations

from bbsliothek.config import AppConfig
from bbsliothek.exceptions import AppError, ValidationError
from bbsliothek.ui.formatting import render_table


class ConsoleApp:
    def __init__(self, material_service, query_service, config: AppConfig) -> None:
        self.material_service = material_service
        self.query_service = query_service
        self.config = config

    def run(self) -> None:
        while True:
            self._print_header("BBSliothek - Hauptmenü")
            print("1. Material hochladen oder neue Version anlegen")
            print("2. Material suchen")
            print("3. Material herunterladen oder öffnen")
            print("4. Kommentare anzeigen")
            print("5. Kommentar hinzufügen")
            print("6. Themengebiete verwalten")
            print("7. Stammdaten/Testdaten anzeigen")
            print("8. Programm beenden")

            choice = input("Auswahl: ").strip()
            try:
                if choice == "1":
                    self._upload_flow()
                elif choice == "2":
                    self._search_flow()
                elif choice == "3":
                    self._download_flow()
                elif choice == "4":
                    self._show_comments_flow()
                elif choice == "5":
                    self._add_comment_flow()
                elif choice == "6":
                    self._topic_flow()
                elif choice == "7":
                    self._master_data_flow()
                elif choice == "8":
                    print("Programm wird beendet.")
                    return
                else:
                    print("Bitte eine gültige Menüoption auswählen.")
            except AppError as exc:
                print(f"Fehler: {exc}")
            input("\nWeiter mit Enter...")

    def _upload_flow(self) -> None:
        self._print_header("Upload")
        source_path = self._prompt_non_empty("Pfad zur Quelldatei")
        author_id = self._prompt_user_id()

        material_id_input = input(
            "Vorhandene Material-ID für neue Version (leer = neues Material): "
        ).strip()

        if material_id_input:
            result = self.material_service.upload_material(
                source_path=source_path,
                author_id=author_id,
                material_id=int(material_id_input),
            )
        else:
            title = self._prompt_non_empty("Titel des Materials")
            topic_id = self._prompt_topic_id()
            result = self.material_service.upload_material(
                source_path=source_path,
                author_id=author_id,
                title=title,
                topic_id=topic_id,
            )

        print(
            "Material erfolgreich gespeichert: "
            f"Material-ID={result.material_id}, Version={result.versionsnummer}, "
            f"Strategie={result.speicherstrategie}"
        )

    def _search_flow(self) -> None:
        while True:
            self._print_header("Suche")
            print("1. Freie Filtersuche")
            for key, title, _ in self.query_service.list_standard_queries():
                print(f"{int(key) + 1}. {title}")
            print("9. Zurück")

            choice = input("Auswahl: ").strip()
            if choice == "1":
                self._free_search_flow()
            elif choice in {"2", "3", "4", "5", "6", "7", "8"}:
                query_key = str(int(choice) - 1)
                title, description, rows = self.query_service.run_standard_query(query_key)
                self._print_header(title)
                print(description)
                print(render_table(rows))
            elif choice == "9":
                return
            else:
                print("Ungültige Auswahl.")

    def _free_search_flow(self) -> None:
        title_filter = input("Titel oder Dateiname enthält (leer = egal): ").strip() or None
        file_type = input("Dateityp enthält (leer = egal): ").strip() or None
        topic_id = self._prompt_optional_int("Themengebiet-ID (leer = egal)")
        author_id = self._prompt_optional_int("Autor-ID (leer = egal)")
        rows = self.material_service.list_materials(
            title_filter=title_filter,
            file_type=file_type,
            topic_id=topic_id,
            author_id=author_id,
        )
        print(render_table(rows))

    def _download_flow(self) -> None:
        self._print_header("Download")
        self._show_material_overview()
        material_id = self._prompt_int("Material-ID")
        destination_dir = input(
            f"Zielordner (leer = {self.config.download_root}): "
        ).strip() or None
        auto_open = input("Datei nach dem Export öffnen? (j/n): ").strip().lower() == "j"
        exported_path = self.material_service.download_material(
            material_id=material_id,
            destination_dir=destination_dir,
            auto_open=auto_open,
        )
        print(f"Datei wurde exportiert nach: {exported_path}")

    def _show_comments_flow(self) -> None:
        self._print_header("Kommentare anzeigen")
        self._show_material_overview()
        material_id = self._prompt_int("Material-ID")
        rows = self.material_service.list_comments(material_id)
        print(render_table(rows))

    def _add_comment_flow(self) -> None:
        self._print_header("Kommentar hinzufügen")
        self._show_material_overview()
        material_id = self._prompt_int("Material-ID")
        author_id = self._prompt_user_id()
        text = self._prompt_non_empty("Kommentartext")
        comment_id = self.material_service.add_comment(material_id, author_id, text)
        print(f"Kommentar {comment_id} wurde gespeichert.")

    def _topic_flow(self) -> None:
        while True:
            self._print_header("Themengebiete")
            print("1. Themengebiete anzeigen")
            print("2. Themengebiet anlegen")
            print("3. Zurück")
            choice = input("Auswahl: ").strip()

            if choice == "1":
                print(render_table(self.material_service.list_topics()))
            elif choice == "2":
                name = self._prompt_non_empty("Name")
                beschreibung = input("Beschreibung: ").strip()
                topic_id = self.material_service.create_topic(name, beschreibung)
                print(f"Themengebiet {topic_id} wurde angelegt.")
            elif choice == "3":
                return
            else:
                print("Ungültige Auswahl.")

    def _master_data_flow(self) -> None:
        self._print_header("Stammdaten")
        print("Rollen")
        print(render_table(self.material_service.list_roles()))
        print("\nBenutzer")
        print(render_table(self.material_service.list_users()))
        print("\nThemengebiete")
        print(render_table(self.material_service.list_topics()))

    def _show_material_overview(self) -> None:
        materials = self.material_service.list_materials()
        if not materials:
            print("Es sind noch keine Materialien vorhanden.")
            raise ValidationError("Für diese Aktion werden zuerst Materialien benötigt.")
        print(render_table(materials))

    def _prompt_user_id(self) -> int:
        print(render_table(self.material_service.list_users()))
        return self._prompt_int("Benutzer-ID")

    def _prompt_topic_id(self) -> int:
        print(render_table(self.material_service.list_topics()))
        return self._prompt_int("Themengebiet-ID")

    def _prompt_optional_int(self, label: str) -> int | None:
        value = input(f"{label}: ").strip()
        if not value:
            return None
        if not value.isdigit():
            raise ValidationError(f"{label} muss eine Zahl sein.")
        return int(value)

    def _prompt_int(self, label: str) -> int:
        value = input(f"{label}: ").strip()
        if not value.isdigit():
            raise ValidationError(f"{label} muss eine Zahl sein.")
        return int(value)

    def _prompt_non_empty(self, label: str) -> str:
        value = input(f"{label}: ").strip()
        if not value:
            raise ValidationError(f"{label} darf nicht leer sein.")
        return value

    def _print_header(self, title: str) -> None:
        print(f"\n{title}\n{'=' * len(title)}")
