from __future__ import annotations

import unittest

from bbsliothek.services.query_service import QueryService


class FakeQueryRepository:
    def run_standard_query(self, query_key: str):
        return ("Titel", "Beschreibung", [{"schluessel": query_key}])


class QueryServiceTest(unittest.TestCase):
    def test_catalog_contains_seven_required_queries(self) -> None:
        service = QueryService(FakeQueryRepository())
        queries = service.list_standard_queries()
        self.assertEqual(len(queries), 7)
        self.assertEqual(queries[0][0], "1")
        self.assertEqual(queries[-1][0], "7")

    def test_standard_query_is_forwarded_to_repository(self) -> None:
        service = QueryService(FakeQueryRepository())
        title, description, rows = service.run_standard_query("4")
        self.assertEqual(title, "Titel")
        self.assertEqual(description, "Beschreibung")
        self.assertEqual(rows[0]["schluessel"], "4")


if __name__ == "__main__":
    unittest.main()
