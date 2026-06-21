import unittest
from unittest.mock import MagicMock, patch

from services.person_service import PersonService


class PersonServiceTestCase(unittest.TestCase):
    """Unit tests for PersonService with the repository fully mocked.

    The service is a thin orchestration layer over PersonRepository, so we
    patch the repository class and assert the service delegates correctly
    without touching any real database.
    """

    def setUp(self) -> None:
        patcher = patch("services.person_service.PersonRepository")
        self.repo_cls = patcher.start()
        self.addCleanup(patcher.stop)

        self.repo = MagicMock()
        self.repo_cls.return_value = self.repo

        self.db = MagicMock()
        self.service = PersonService(self.db)

    def test_init_builds_repository_with_session(self) -> None:
        self.repo_cls.assert_called_once_with(self.db)

    def test_create_delegates_to_repository(self) -> None:
        self.repo.create.return_value = "created"

        result = self.service.create(name="Alice", age=30, language="fr")

        self.assertEqual(result, "created")
        self.repo.create.assert_called_once_with(name="Alice", age=30, language="fr")

    def test_get_all_delegates_to_repository(self) -> None:
        self.repo.get_all.return_value = ["a", "b"]

        self.assertEqual(self.service.get_all(), ["a", "b"])
        self.repo.get_all.assert_called_once_with()

    def test_get_by_id_delegates_to_repository(self) -> None:
        self.repo.get_by_id.return_value = "person"

        self.assertEqual(self.service.get_by_id(7), "person")
        self.repo.get_by_id.assert_called_once_with(7)

    def test_update_delegates_to_repository(self) -> None:
        self.repo.update.return_value = "updated"

        result = self.service.update(person_id=3, name="Bob", age=45, language="en")

        self.assertEqual(result, "updated")
        self.repo.update.assert_called_once_with(person_id=3, name="Bob", age=45, language="en")

    def test_delete_delegates_to_repository(self) -> None:
        self.repo.delete.return_value = True

        self.assertTrue(self.service.delete(9))
        self.repo.delete.assert_called_once_with(9)

    def test_get_stats_delegates_to_repository(self) -> None:
        stats = {"total": 2, "average_age": 37.5, "by_language": {"fr": 2}}
        self.repo.get_stats.return_value = stats

        self.assertEqual(self.service.get_stats(), stats)
        self.repo.get_stats.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
