import unittest

from entities.greeting import AudienceLevel
from services.greeting_template_service import GreetingTemplateService


class GreetingTemplateServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = GreetingTemplateService()

    def test_build_message_formats_expected_template(self) -> None:
        message = self.service.build_message(
            name="Alice",
            language="fr",
            audience=AudienceLevel.VIP,
            excited=True,
        )

        self.assertEqual(message, "Bienvenue, tres cher Alice!")

    def test_build_message_rejects_unsupported_language(self) -> None:
        with self.assertRaises(ValueError):
            self.service.build_message(
                name="Alice",
                language="de",
                audience=AudienceLevel.CASUAL,
                excited=False,
            )

    def test_list_supported_languages_returns_sorted_values(self) -> None:
        self.assertEqual(self.service.list_supported_languages(), ["en", "es", "fr"])