from unittest import TestCase

from fastapi.testclient import TestClient
from httpx import Response

from app.routes import app

client = TestClient(app)


class TestCreateAndGet(TestCase):
    def test_create_and_get(self):
        response: Response = client.post(
            "/articles",
            json={
                "title": "a",
                "content": "b",
                "creation": "01/01/2023",
            },
        )
        # Assert the request was succesful
        self.assertEqual(201, response.status_code)
        self.assertIn("location", response.headers.keys())
        location = response.headers["location"]
        response = client.get(location)
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        self.assertEqual("a", response_body["title"])

    def test_create_and_update_and_get(self):
        # Initial article
        article = {
            "title": "a",
            "content": "b",
            "creation": "01/01/2023",
        }
        # Create article
        response: Response = client.post("/articles", json=article)
        # Assert the request was succesful
        self.assertEqual(201, response.status_code)
        self.assertIn("location", response.headers.keys())
        # Get location of newly created article
        location = response.headers["location"]
        # Creation of new article
        article = {
            "title": "new title",
            "content": "new content",
            "creation": "01/01/2023",
        }
        response: Response = client.put(location, json=article)
        # Assert the request was succesful
        self.assertEqual(204, response.status_code)
        response = client.get(location)
        self.assertEqual(200, response.status_code)
        response_body = response.json()
        # Assert article has been updated successfully
        self.assertEqual("new title", response_body["title"])
        self.assertEqual("new content", response_body["content"])
