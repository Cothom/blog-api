import copy
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.articles import (
    Article,
    RequestArticle,
    ResponseArticle,
    _add,
    _all,
    _get,
    _update,
)


class TestRequestArticle(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now()
        self.now_str = self.now.isoformat()
        self.uuid = uuid4()
        self.req_article = RequestArticle(
            content="c", title="t", creation=self.now_str, id=self.uuid.hex
        )
        self.article = Article(
            content="c", title="t", date=self.now, uuid=self.uuid
        )
        return super().setUp()

    @patch("app.articles.iso_string_to_datetime")
    def test_to_article_converts_correctly(self, mock: MagicMock):
        mock.return_value = self.now
        expected = self.article
        output = RequestArticle.to_article(self.req_article)
        self.assertEqual(expected, output)


class TestResponseArticle(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now()
        self.now_str = self.now.isoformat()
        self.uuid = uuid4()
        self.res_article = ResponseArticle(
            content="c", title="t", creation=self.now_str, id=self.uuid.hex
        )
        self.article = Article(
            content="c", title="t", date=self.now, uuid=self.uuid
        )
        return super().setUp()

    @patch("app.articles.datetime_to_iso_string")
    def test_from_article_converts_correctly(self, mock: MagicMock):
        mock.return_value = self.now_str
        expected = self.res_article
        output = ResponseArticle.from_article(self.article)
        self.assertEqual(expected, output)


class TestProtectedFunctions(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now()
        self.uuid = uuid4()
        self.article = Article(
            content="c", title="t", date=self.now, uuid=self.uuid
        )

    def test__add(self):
        _add(self.article)
        self.assertEqual(len(_all.keys()), 1)
        self.assertEqual(_all[self.article.uuid], self.article)

    def test__get(self):
        _all[self.article.uuid] = self.article
        output = _get(self.article.uuid.hex)
        self.assertEqual(self.article, output)

    def test__update(self):
        _all[self.article.uuid] = self.article
        self.new = copy.deepcopy(self.article)
        self.new.content = "new content"
        _update(self.article, self.new)
        updated = _all[self.article.uuid]
        self.assertEqual(self.new, updated)


class TestPublicFunctions(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now()
        self.uuid = uuid4()
        self.article = Article(
            content="c", title="t", date=self.now, uuid=self.uuid
        )

    @patch("app.articles.ResponseArticle.from_article")
    def test_get_all(self, mock: MagicMock):
        self.assertEqual(0, 1)

    @patch("app.articles.ResponseArticle.from_article")
    def test_get_by_id(self, mock: MagicMock):
        self.assertEqual(0, 1)

    @patch("app.articles.ResponseArticle.from_article")
    def test_create(self, mock: MagicMock):
        self.assertEqual(0, 1)

    @patch("app.articles.ResponseArticle.from_article")
    def test_update(self, mock: MagicMock):
        self.assertEqual(0, 1)
