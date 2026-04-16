import unittest

from entities.greeting import AudienceLevel, GreetingRequestEntity
from services.greeting_service import GreetingService
from services.greeting_template_service import GreetingTemplateService


class GreetingServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = GreetingService(template_service=GreetingTemplateService())

    def test_create_greeting_updates_stats_and_returns_entity(self) -> None:
        entity = self.service.create_greeting(
            GreetingRequestEntity(
                name="Sam",
                language="en",
                audience=AudienceLevel.FORMAL,
                excited=False,
            )
        )

        self.assertEqual(entity.message, "Hello Sam.")
        self.assertEqual(entity.language, "en")
        self.assertEqual(entity.audience, AudienceLevel.FORMAL)

        stats = self.service.get_stats()
        self.assertEqual(stats.total_requests, 1)
        self.assertEqual(stats.requests_by_language, {"en": 1})

    def test_get_stats_starts_empty(self) -> None:
        stats = self.service.get_stats()

        self.assertEqual(stats.total_requests, 0)
        self.assertEqual(stats.requests_by_language, {})

    def test_get_supported_languages_delegates_to_template_service(self) -> None:
        self.assertEqual(self.service.get_supported_languages(), ["en", "es", "fr"])