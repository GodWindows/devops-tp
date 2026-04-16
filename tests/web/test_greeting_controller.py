import unittest

from fastapi.testclient import TestClient

from app import create_app


class GreetingControllerWebTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_hello_world_endpoint_returns_expected_payload(self) -> None:
        response = self.client.get("/hello-world")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["message"], "Hello World.")
        self.assertEqual(payload["language"], "en")
        self.assertEqual(payload["audience"], "formal")
        self.assertIn("generated_at", payload)

    def test_create_greeting_endpoint_accepts_payload(self) -> None:
        response = self.client.post(
            "/greetings",
            json={"name": "Nora", "language": "FR", "audience": "vip", "excited": True},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["message"], "Bienvenue, tres cher Nora!")
        self.assertEqual(payload["language"], "fr")
        self.assertEqual(payload["audience"], "vip")

    def test_list_languages_endpoint_returns_supported_languages(self) -> None:
        response = self.client.get("/greetings/languages")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ["en", "es", "fr"])

    def test_stats_endpoint_reflects_created_greetings(self) -> None:
        self.client.post(
            "/greetings",
            json={"name": "Nora", "language": "fr", "audience": "casual", "excited": False},
        )
        self.client.post(
            "/greetings",
            json={"name": "Leo", "language": "en", "audience": "formal", "excited": False},
        )

        response = self.client.get("/greetings/stats")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"total_requests": 2, "requests_by_language": {"fr": 1, "en": 1}})

    def test_invalid_language_returns_bad_request(self) -> None:
        response = self.client.post(
            "/greetings",
            json={"name": "Nora", "language": "de", "audience": "casual", "excited": False},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Unsupported language: de"})