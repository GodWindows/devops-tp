import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from entities.greeting import AudienceLevel
from services.person_greeting_service import PersonGreetingService


def _person(name="Alice", age=30, language="fr"):
    """Lightweight stand-in for a PersonModel row."""
    return SimpleNamespace(name=name, age=age, language=language)


class PersonGreetingServiceTestCase(unittest.TestCase):
    """Unit tests for PersonGreetingService.

    The repository is mocked so no database is required; the real
    GreetingTemplateService is used since it is pure logic.
    """

    def setUp(self) -> None:
        patcher = patch("services.person_greeting_service.PersonRepository")
        self.repo_cls = patcher.start()
        self.addCleanup(patcher.stop)

        self.repo = MagicMock()
        self.repo_cls.return_value = self.repo

        self.service = PersonGreetingService(MagicMock())

    def test_returns_none_when_person_missing(self) -> None:
        self.repo.get_by_id.return_value = None

        self.assertIsNone(self.service.greet(404))
        self.repo.get_by_id.assert_called_once_with(404)

    def test_child_is_greeted_casually(self) -> None:
        self.repo.get_by_id.return_value = _person(name="Kid", age=10, language="fr")

        result = self.service.greet(1)

        self.assertEqual(result.audience, AudienceLevel.CASUAL)
        self.assertEqual(result.language, "fr")
        self.assertEqual(result.message, "Salut Kid.")

    def test_adult_is_greeted_formally(self) -> None:
        self.repo.get_by_id.return_value = _person(name="Bob", age=40, language="en")

        result = self.service.greet(1)

        self.assertEqual(result.audience, AudienceLevel.FORMAL)
        self.assertEqual(result.message, "Hello Bob.")

    def test_senior_is_greeted_as_vip(self) -> None:
        self.repo.get_by_id.return_value = _person(name="Rosa", age=70, language="es")

        result = self.service.greet(1)

        self.assertEqual(result.audience, AudienceLevel.VIP)
        self.assertEqual(result.message, "Bienvenido, estimado Rosa!".replace("!", "."))

    def test_boundary_18_is_formal(self) -> None:
        self.repo.get_by_id.return_value = _person(age=18)
        self.assertEqual(self.service.greet(1).audience, AudienceLevel.FORMAL)

    def test_boundary_65_is_vip(self) -> None:
        self.repo.get_by_id.return_value = _person(age=65)
        self.assertEqual(self.service.greet(1).audience, AudienceLevel.VIP)

    def test_unsupported_language_falls_back_to_english(self) -> None:
        self.repo.get_by_id.return_value = _person(name="Hans", age=30, language="de")

        result = self.service.greet(1)

        self.assertEqual(result.language, "en")
        self.assertEqual(result.message, "Hello Hans.")


if __name__ == "__main__":
    unittest.main()
