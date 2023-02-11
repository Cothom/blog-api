import copy
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.articles import _add  # type: ignore  -> Testing private functions
from app.articles import _all  # type: ignore
from app.articles import _get  # type: ignore
from app.articles import _update  # type: ignore
from app.articles import (
    Article,
    OperationType,
    RequestArticle,
    ResponseArticle,
    create,
    get_all,
    get_by_id,
    update,
)


class TestRequestArticle(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now()
        self.now_str = self.now.isoformat()
        self.uuid = uuid4()
        self.req_article = RequestArticle(
            content="c", title="t", creation=self.now_str
        )
        self.article = Article(
            content="c", title="t", date=self.now, uuid=self.uuid
        )
        return super().setUp()

    @patch("app.articles.iso_string_to_datetime")
    def test_to_article_converts_correctly(self, mock_iso_to_date: MagicMock):
        mock_iso_to_date.return_value = self.now
        expected = self.article
        output = RequestArticle.to_article(self.req_article)
        # Nested call to uuid4 cannot be patched
        output.uuid = self.uuid
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
        self.now_str = self.now.isoformat()
        self.uuid = uuid4()
        self.req_id = self.uuid.hex
        self.article = Article(
            content="c", title="t", date=self.now, uuid=self.uuid
        )
        self.req_article = RequestArticle(
            content="c", title="t", creation=self.now_str
        )
        self.res_article = ResponseArticle(
            content="c", title="t", creation=self.now_str, id=self.req_id
        )
        # _all[self.uuid] = self.article

    @patch("app.articles.ResponseArticle.from_article")
    def test_get_all(self, mock: MagicMock):
        _all.clear()
        _all[self.uuid] = self.article
        mock.return_value = self.res_article
        articles, op = get_all()
        expected = [self.res_article]
        self.assertEqual(expected, articles)
        self.assertEqual(OperationType.READ, op)

    @patch("app.articles.ResponseArticle.from_article")
    def test_get_by_id(self, mock: MagicMock):
        _all.clear()
        _all[self.uuid] = self.article
        mock.return_value = self.res_article
        article, op = get_by_id(self.req_id)
        expected = self.res_article
        self.assertEqual(expected, article)
        self.assertEqual(OperationType.READ, op)

    @patch("app.articles._add")
    @patch("app.articles.ResponseArticle.to_article")
    def test_create(self, mock_to_article: MagicMock, mock__add: MagicMock):
        def _add_side_effect(_):
            _all[self.uuid] = self.article
            _all[self.uuid].uuid = self.uuid

        mock_to_article.return_value = self.article
        mock__add.side_effect = _add_side_effect
        _, op = create(self.req_article)
        self.assertEqual(_all[self.uuid], self.article)
        self.assertEqual(OperationType.CREATED, op)

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
            _all[self.uuid] = new

        # Preparing the mocks
        mock__get.return_value = self.article  # Old article
        # Cloning article to give a modified copy as arg
        updated = Article(
            "new content",
            self.article.title,
            self.article.date,
            self.article.uuid,
        )
        mock_to_article.return_value = updated  # New article
        self.req_article.content = "new content"
        mock__update.side_effect = _update_side_effect
        # Actual updating action
        op = update(self.req_id, self.req_article)
        self.assertEqual(_all[self.uuid], updated)
        self.assertEqual(_all[self.uuid].uuid, updated.uuid)
        self.assertEqual(OperationType.UPDATED, op)

    @patch("app.articles.RequestArticle.to_article")
    @patch("app.articles._get")
    @patch("app.articles._add")
    def test_update_not_existing(
        self,
        mock__add: MagicMock,
        mock__get: MagicMock,
        mock_to_article: MagicMock,
    ):
        def _add_side_effect(new: Article):
            _all[self.uuid] = new

        # Make sure article does not exist yet
        _all.clear()
        # Preparing the mocks
        mock__get.return_value = None  # Article does not exist yet
        mock_to_article.return_value = self.article  # Article to create
        mock__add.side_effect = _add_side_effect
        # Actual updating action
        op = update(self.req_id, self.req_article)
        self.assertEqual(_all[self.uuid], self.article)
        self.assertEqual(_all[self.uuid].uuid, self.uuid)
        self.assertEqual(OperationType.CREATED, op)
