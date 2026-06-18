import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from entities.person import PersonModel  # noqa: F401 — registers the table on Base
from repositories.person_repository import PersonRepository


class PersonRepositoryTestCase(unittest.TestCase):
    """Tests the repository against a real in-memory SQLite database.

    Each test gets a fresh schema, so the CRUD and stats logic is exercised
    end to end without depending on the on-disk persons.db file.
    """

    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.repo = PersonRepository(self.db)

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_create_assigns_id_and_persists(self) -> None:
        person = self.repo.create(name="Alice", age=30, language="fr")

        self.assertIsNotNone(person.id)
        self.assertEqual(person.name, "Alice")
        self.assertEqual(self.repo.get_by_id(person.id).age, 30)

    def test_get_by_id_returns_none_when_missing(self) -> None:
        self.assertIsNone(self.repo.get_by_id(999))

    def test_get_all_returns_every_row(self) -> None:
        self.repo.create(name="Alice", age=30, language="fr")
        self.repo.create(name="Bob", age=45, language="en")

        self.assertEqual(len(self.repo.get_all()), 2)

    def test_update_modifies_existing_row(self) -> None:
        person = self.repo.create(name="Alice", age=30, language="fr")

        updated = self.repo.update(person_id=person.id, name="Alice 2", age=31, language="en")

        self.assertEqual(updated.name, "Alice 2")
        self.assertEqual(updated.age, 31)
        self.assertEqual(updated.language, "en")

    def test_update_returns_none_when_missing(self) -> None:
        self.assertIsNone(self.repo.update(person_id=999, name="x", age=1, language="fr"))

    def test_delete_removes_row(self) -> None:
        person = self.repo.create(name="Alice", age=30, language="fr")

        self.assertTrue(self.repo.delete(person.id))
        self.assertIsNone(self.repo.get_by_id(person.id))

    def test_delete_returns_false_when_missing(self) -> None:
        self.assertFalse(self.repo.delete(999))

    def test_get_stats_on_empty_database(self) -> None:
        self.assertEqual(
            self.repo.get_stats(),
            {"total": 0, "average_age": 0.0, "by_language": {}},
        )

    def test_get_stats_aggregates_count_average_and_languages(self) -> None:
        self.repo.create(name="Alice", age=30, language="fr")
        self.repo.create(name="Bob", age=40, language="fr")
        self.repo.create(name="Carlos", age=50, language="es")

        stats = self.repo.get_stats()

        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["average_age"], 40.0)
        self.assertEqual(stats["by_language"], {"fr": 2, "es": 1})


if __name__ == "__main__":
    unittest.main()
