from __future__ import annotations

from bbsliothek.db.query_catalog import STANDARD_QUERIES


class QueryService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def list_standard_queries(self) -> list[tuple[str, str, str]]:
        return [
            (definition.key, definition.title, definition.description)
            for definition in STANDARD_QUERIES.values()
        ]

    def run_standard_query(self, query_key: str):
        return self.repository.run_standard_query(query_key)
