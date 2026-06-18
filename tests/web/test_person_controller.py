import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from controllers.person_controller import get_db
from database import Base
from entities.person import PersonModel  # noqa: F401 — registers the table on Base


class PersonControllerWebTestCase(unittest.TestCase):
    """End-to-end tests for the /persons endpoints.

    The get_db dependency is overridden with a dedicated in-memory SQLite
    database so each test runs against a clean, isolated schema and never
    touches the real data/persons.db file.
    """

    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        TestingSession = sessionmaker(bind=self.engine)

        def override_get_db():
            db = TestingSession()
            try:
                yield db
            finally:
                db.close()

        self.app = create_app()
        self.app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def _create(self, name="Alice", age=30, language="fr"):
        return self.client.post("/persons", json={"name": name, "age": age, "language": language})

    # ------------------------------------------------------------- create
    def test_create_person_returns_201_with_resource(self) -> None:
        response = self._create()

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["name"], "Alice")
        self.assertEqual(body["age"], 30)
        self.assertEqual(body["language"], "fr")
        self.assertIn("id", body)

    def test_create_person_missing_fields_returns_422(self) -> None:
        response = self.client.post("/persons", json={"name": "Ghost"})
        self.assertEqual(response.status_code, 422)

    def test_create_person_invalid_age_returns_422(self) -> None:
        response = self._create(age=-5)
        self.assertEqual(response.status_code, 422)

    # ------------------------------------------------------------- read
    def test_list_persons_returns_all(self) -> None:
        self._create(name="Alice")
        self._create(name="Bob", age=45, language="en")

        response = self.client.get("/persons")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_get_person_by_id(self) -> None:
        created = self._create().json()

        response = self.client.get(f"/persons/{created['id']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Alice")

    def test_get_person_not_found_returns_404(self) -> None:
        response = self.client.get("/persons/999")
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------- stats
    def test_stats_reflects_created_persons(self) -> None:
        self._create(name="Alice", age=30, language="fr")
        self._create(name="Bob", age=40, language="fr")
        self._create(name="Carlos", age=50, language="es")

        response = self.client.get("/persons/stats")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"total": 3, "average_age": 40.0, "by_language": {"fr": 2, "es": 1}},
        )

    # ------------------------------------------------------------- update
    def test_update_person_replaces_resource(self) -> None:
        created = self._create().json()

        response = self.client.put(
            f"/persons/{created['id']}",
            json={"name": "Alice Updated", "age": 31, "language": "en"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["name"], "Alice Updated")
        self.assertEqual(body["age"], 31)
        self.assertEqual(body["language"], "en")

    def test_update_person_not_found_returns_404(self) -> None:
        response = self.client.put(
            "/persons/999",
            json={"name": "Nobody", "age": 20, "language": "fr"},
        )
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------- delete
    def test_delete_person_returns_204(self) -> None:
        created = self._create().json()

        response = self.client.delete(f"/persons/{created['id']}")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get(f"/persons/{created['id']}").status_code, 404)

    def test_delete_person_not_found_returns_404(self) -> None:
        response = self.client.delete("/persons/999")
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------- greet
    def test_greet_adult_is_formal(self) -> None:
        created = self._create(name="Bob", age=40, language="en").json()

        response = self.client.get(f"/persons/{created['id']}/greet")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["message"], "Hello Bob.")
        self.assertEqual(body["language"], "en")
        self.assertEqual(body["audience"], "formal")

    def test_greet_unsupported_language_falls_back_to_english(self) -> None:
        created = self._create(name="Hans", age=30, language="de").json()

        response = self.client.get(f"/persons/{created['id']}/greet")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["language"], "en")
        self.assertEqual(body["message"], "Hello Hans.")

    def test_greet_person_not_found_returns_404(self) -> None:
        response = self.client.get("/persons/999/greet")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
