import copy
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.articles import _add  # type: ignore  -> Testing private functions
from app.articles import _all  # type: ignore
from app.articles import _get  # type: ignore
from app.articles import _update  # type: ignore
from app.articles import (Article, ArticleId, RequestArticle, ResponseArticle,
                          create, get_all, get_by_id, update)
from app.exceptions import ArticleNotFoundError


class TestRequestArticle(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now()
        self.now_str = self.now.isoformat()
        self.article_id = ArticleId()
        self.req_article = RequestArticle(
            content="c",
            title="t",
            creation=self.now_str,
            id=self.article_id.as_str(),
        )
        self.article = Article(
            content="c", title="t", date=self.now, id=self.article_id
        )
        return super().setUp()

    @patch("app.articles.iso_string_to_datetime")
    def test_to_article_converts_correctly(self, mock_iso_to_date: MagicMock):
        mock_iso_to_date.return_value = self.now
        expected = self.article
        output = RequestArticle.to_article(self.req_article)
        self.assertEqual(expected, output)


class TestResponseArticle(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now()
        self.now_str = self.now.isoformat()
        self.article_id = ArticleId()
        self.res_article = ResponseArticle(
            content="c",
            title="t",
            creation=self.now_str,
            id=self.article_id.as_str(),
        )
        self.article = Article(
            content="c", title="t", date=self.now, id=self.article_id
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
        self.article_id = ArticleId()
        self.article = Article(
            content="c", title="t", date=self.now, id=self.article_id
        )
        _all.clear()

    def test__add(self):
        _add(self.article)
        self.assertEqual(len(_all.keys()), 1)
        self.assertEqual(_all[self.article.id], self.article)  # type: ignore

    def test__get(self):
        _all[self.article.id] = self.article  # type: ignore
        output = _get(self.article.id)  # type: ignore
        self.assertEqual(self.article, output)

    def test__update(self):
        _all[self.article.id] = self.article
        self.new = copy.deepcopy(self.article)
        self.new.content = "new content"
        _update(self.article, self.new)
        updated = _all[self.article.id]
        self.assertEqual(self.new, updated)


class TestPublicFunctions(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now()
        self.now_str = self.now.isoformat()
        self.article_id = ArticleId()
        self.req_id = self.article_id.as_str()
        self.article = Article(
            content="c", title="t", date=self.now, id=self.article_id
        )
        self.req_article = RequestArticle(
            content="c", title="t", creation=self.now_str
        )
        self.res_article = ResponseArticle(
            content="c", title="t", creation=self.now_str, id=self.req_id
        )
        # _all[self.article_id] = self.article

    @patch("app.articles.ResponseArticle.from_article")
    def test_get_all(self, mock: MagicMock):
        _all.clear()
        _all[self.article_id] = self.article
        mock.return_value = self.res_article
        articles = get_all()
        expected = [self.res_article]
        self.assertEqual(expected, articles)

    @patch("app.articles.ResponseArticle.from_article")
    def test_get_by_id(self, mock: MagicMock):
        _all.clear()
        _all[self.article_id] = self.article
        mock.return_value = self.res_article
        article = get_by_id(self.req_id)
        expected = self.res_article
        self.assertEqual(expected.id, article.id)

    @patch("app.articles._add")
    @patch("app.articles.ResponseArticle.to_article")
    def test_create(self, mock_to_article: MagicMock, mock__add: MagicMock):
        def _add_side_effect(_):
            _all[self.article_id] = self.article
            _all[self.article_id].id = self.article_id

        mock_to_article.return_value = self.article
        mock__add.side_effect = _add_side_effect
        _ = create(self.req_article)
        self.assertEqual(_all[self.article_id], self.article)

    @patch("app.articles.RequestArticle.to_article")
    @patch("app.articles._get")
    @patch("app.articles._update")
    def test_update_existing(
        self,
        mock__update: MagicMock,
        mock__get: MagicMock,
        mock_to_article: MagicMock,
    ):
        def _update_side_effect(_, new: Article):
            _all[self.article_id] = new

        # Preparing the mocks
        mock__get.return_value = self.article  # Old article
        # Cloning article to give a modified copy as arg
        updated = Article(
            "new content",
            self.article.title,
            self.article.date,
            self.article.id,
        )
        mock_to_article.return_value = updated  # New article
        self.req_article.content = "new content"
        mock__update.side_effect = _update_side_effect
        # Actual updating action
        update(self.req_id, self.req_article)
        self.assertEqual(_all[self.article_id], updated)
        self.assertEqual(_all[self.article_id].id, updated.id)

    @patch("app.articles._get")
    def test_update_not_existing(
        self,
        mock__get: MagicMock
    ):
        # Make sure article does not exist yet
        _all.clear()
        # Preparing the mocks
        mock__get.return_value = None  # Article does not exist yet
        # Actual updating action
        with self.assertRaises(ArticleNotFoundError):
            update(self.req_id, self.req_article)
