import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import Response
from fastapi.testclient import TestClient

from app.routes import *

client = TestClient(app)


class TestHelloWorld(unittest.TestCase):
    def test_hello_world(self):
        expected = {"message": "Hello World!"}
        output = hello_world()
        self.assertEqual(expected, output)

    def test_returns_200(self):
        response: Response = client.get("/")  # type: ignore
        self.assertEqual(200, response.status_code)


class TestGetAllArticles(unittest.TestCase):
    def setUp(self) -> None:
        now = datetime.now().isoformat()
        self.req_article = RequestArticle(content="c", title="t", creation=now)
        self.res_article = ResponseArticle(
            content="c", title="t", creation=now, id=uuid4().hex
        )
        return super().setUp()

    @patch("app.routes.get_all")
    def test_returns_empty_when_no_articles(self, mock: MagicMock):
        mock.return_value = [], OperationType.READ
        expected = []
        output = get_all_articles()
        self.assertEqual(expected, output)

    @patch("app.routes.get_all")
    def test_get_all_articles(self, mock: MagicMock):
        mock.return_value = [self.res_article], OperationType.READ
        expected: list[ResponseArticle] = [self.res_article]
        output = get_all_articles()
        self.assertEqual(expected, output)

    @patch("app.routes.get_all")
    def test_returns_200_even_if_empty(self, mock: MagicMock):
        mock.return_value = [], OperationType.READ
        response: Response = client.get("/articles")  # type: ignore
        self.assertEqual(200, response.status_code)

    @patch("app.routes.get_all")
    def test_returns_200_if_not_empty(self, mock: MagicMock):
        mock.return_value = [self.res_article], OperationType.READ
        response: Response = client.get("/articles")  # type: ignore
        self.assertEqual(200, response.status_code)


class TestGetArticle(unittest.TestCase):
    def setUp(self) -> None:
        now = datetime.now().isoformat()
        self.res_article = ResponseArticle(
            content="c", title="t", creation=now, id=uuid4().hex
        )
        return super().setUp()

    @patch("app.routes.get_by_id")
    def test_raises_HTTPException(self, mock: MagicMock):
        mock.return_value = None, OperationType.READ
        with self.assertRaises(HTTPException):
            get_article("does not exist")

    @patch("app.routes.get_by_id")
    def test_returns_article_if_exists(self, mock: MagicMock):
        mock.return_value = self.res_article, OperationType.READ
        expected = self.res_article
        output = get_article("does exist")
        self.assertEqual(expected, output)

    @patch("app.routes.get_by_id")
    def test_returns_200_if_found(self, mock: MagicMock):
        mock.return_value = self.res_article, OperationType.READ
        response: Response = client.get(
            "/articles/" + str(uuid4())
        )  # type: ignore
        self.assertEqual(200, response.status_code)

    @patch("app.routes.get_by_id")
    def test_returns_404_if_not_found(self, mock: MagicMock):
        mock.return_value = None, OperationType.READ
        response: Response = client.get(
            "/articles/" + str(uuid4())
        )  # type: ignore
        self.assertEqual(404, response.status_code)


class TestNewArticle(unittest.TestCase):
    def setUp(self) -> None:
        now = datetime.now().isoformat()
        self.req_article = RequestArticle(content="c", title="t", creation=now)
        return super().setUp()

    @patch("app.routes.create")
    def test_returns_201_if_article_valid(self, mock: MagicMock):
        mock.return_value = "new id", OperationType.CREATED
        response: Response = client.post(
            "/articles",
            json={
                "title": "a",
                "content": "b",
                "creation": "01/01/2023",
            },
        )  # type: ignore
        self.assertEqual(201, response.status_code)

    @patch("app.routes.create")
    def test_set_location_if_article_valid(self, mock: MagicMock):
        mock.return_value = "new id", OperationType.CREATED
        response: Response = client.post(
            "/articles",
            json={
                "title": "a",
                "content": "b",
                "creation": "01/01/2023",
            },
        )  # type: ignore
        self.assertEqual(201, response.status_code)
        self.assertTrue("location" in response.headers.keys())

    @patch("app.routes.create")
    def test_returns_201_if_no_id_provided(self, mock: MagicMock):
        mock.return_value = "new id", OperationType.CREATED
        response: Response = client.post(
            "/articles",
            json={
                "title": "a",
                "content": "b",
                "creation": "",
            },
        )  # type: ignore
        self.assertEqual(201, response.status_code)

    @patch("app.routes.create")
    def test_returns_422_if_article_invalid(self, mock: MagicMock):
        mock.return_value = None
        # Mandatory fields "title" is missing
        response: Response = client.post(
            "/articles", json={"content": "b", "creation": "01/01/2023"}
        )  # type: ignore
        self.assertEqual(422, response.status_code)

    @patch("app.routes.create")
    def test_returns_422_if_request_empty(self, mock: MagicMock):
        mock.return_value = None
        response: Response = client.post("/articles")  # type: ignore
        self.assertEqual(422, response.status_code)


class TestUpdateArticle(unittest.TestCase):
    @patch("app.routes.update")
    def test_returns_201_if_article_created(self, mock: MagicMock):
        mock.return_value = OperationType.CREATED
        response: Response = client.put(
            "/articles/" + str(uuid4()),
            json={
                "title": "a",
                "content": "b",
                "creation": "01/01/2023",
                "id": uuid4().hex,
            },
        )  # type: ignore
        self.assertEqual(201, response.status_code)

    @patch("app.routes.update")
    def test_returns_204_if_article_updated(self, mock: MagicMock):
        mock.return_value = OperationType.UPDATED
        response: Response = client.put(
            "/articles/" + str(uuid4()),
            json={
                "title": "a",
                "content": "b",
                "creation": "01/01/2023",
                "id": uuid4().hex,
            },
        )  # type: ignore
        self.assertEqual(204, response.status_code)

    @patch("app.routes.update")
    def test_returns_422_if_article_invalid(self, mock: MagicMock):
        mock.return_value = None
        # Mandatory fields "title" and "id" are missing
        response: Response = client.put(
            "/articles/" + uuid4().hex,
            json={"content": "b", "creation": "01/01/2023"},
        )  # type: ignore
        self.assertEqual(422, response.status_code)

    @patch("app.routes.update")
    def test_returns_422_if_request_empty(self, mock: MagicMock):
        mock.return_value = None
        response: Response = client.put(
            "/articles/" + uuid4().hex
        )  # type: ignore
        self.assertEqual(422, response.status_code)
