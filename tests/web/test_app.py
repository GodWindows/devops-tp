import unittest

from fastapi.testclient import TestClient

from app import create_app


class AppRoutingTestCase(unittest.TestCase):
    """Tests for the application-level routes (root redirect + UI mount)."""

    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_root_redirects_to_ui(self) -> None:
        response = self.client.get("/", follow_redirects=False)

        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/ui/")

    def test_root_redirect_followed_serves_frontend(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("DevOps TP", response.text)

    def test_ui_serves_index_html(self) -> None:
        response = self.client.get("/ui/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("API Console", response.text)


if __name__ == "__main__":
    unittest.main()
