"""Entities handled by API and functions to manipulate them."""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.exceptions import (ArticleNotFoundError, InvalidArticleIdError,
                            InvalidRequestedIdError)
from app.utils import datetime_to_iso_string, iso_string_to_datetime

logger = logging.getLogger(__name__)


class ArticleId:
    def __init__(self, /, id: str | None = None, uuid: UUID | None = None):
        """At most, only one of "id" and "uuid" must be provided.
        If both are provided, "uuid" will be used and "id" will be discarded.
        If none is provided, a new UUID will be generated.

        Args:
            id (str | None, optional): String formatted UUID. Defaults to None.
            uuid (UUID | None, optional): UUID object. Defaults to None.
        """
        if id is None:
            self.uuid: UUID = uuid or uuid4()
        else:
            try:
                self.uuid: UUID = UUID(id)
            except ValueError:
                raise InvalidArticleIdError(f"Id '{id}' is not a valid UUID")

    def as_str(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.uuid)  # '12345678-9012-3456-7890-123456789012'

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, ArticleId) and __o.uuid == self.uuid


@dataclass
class Article:
    """Data class representing an article of the blog."""

    def __init__(
        self,
        content: str,
        title: str,
        date: datetime,
        id: ArticleId | None = None,
    ):
        self.content: str = content
        self.title: str = title
        self.date: datetime = date
        self.id: ArticleId = id or ArticleId()

    def __repr__(self) -> str:
        return json.dumps(self.__dict__, default=str, indent=4)


class RequestArticle(BaseModel):
    """Class representing an article the way it is sent by API consumer"""

    title: str
    content: str
    creation: str | None = None
    id: str | None = None
    # On creation request, no id is yet assigned to article

    @staticmethod
    def to_article(
        request: "RequestArticle", id: ArticleId | None = None
    ) -> Article:
        """Converts an instance of this class into a new instance of Article

        Args:
            request (RequestArticle): The article to convert

        Returns:
            Article: The converted article
        """
        kwargs: dict[str, str | datetime | ArticleId] = {
            "title": request.title,
            "content": request.content,
            "date": iso_string_to_datetime(request.creation),
        }
        if id:
            kwargs["id"] = id
        elif request.id:
            kwargs["id"] = request.id

        article: Article = Article(**kwargs)  # type: ignore
        logger.debug(f"New article with {article.id} created")
        return article


class ResponseArticle(RequestArticle):
    """Class representing an article the way it is returned to API consumer"""

    @staticmethod
    def from_article(article: Article) -> "ResponseArticle":
        """Converts an instance of Article into a new instance of this class

        Args:
            article (Article): The article to convert

        Returns:
            ResponseArticle: The converted article
        """
        id: str = article.id.as_str()
        title: str = article.title
        content: str = article.content
        creation: str = datetime_to_iso_string(article.date)
        return ResponseArticle(
            content=content, title=title, creation=creation, id=id
        )


# Represents the in-memory storage
_all: dict[ArticleId, Article] = {}


def _add(article: Article) -> None:
    """Add an Article entity to the storage

    Args:
        article (Article): article to store
    """
    _all[article.id] = article


def _get(id: ArticleId) -> Article | None:
    """Fetch the article corresponding to given Id from storage if exists

    Args:
        id (str): Id of the article to get

    Returns:
        Article | None: Fetched article if exists, None otherwise
    """
    logger.debug(f"Looking for article with id {id}")
    logger.debug(f"Storage: {_all}")
    result: Article | None = _all.get(id, None)
    return result


def _update(old: Article, new: Article) -> None:
    """Replace old article with the new one

    Args:
        old (Article): Article to replace
        new (Article): New article
    """
    # Id must be preserved when updating
    new.id = old.id
    _all[old.id] = new


def get_all() -> list[ResponseArticle]:
    """Get all stored articles and return them as ResponseArticle objects
    along with an OperationType

    Returns:
        list[ResponseArticle]: All articles
    """
    return [ResponseArticle.from_article(article) for article in _all.values()]


def get_by_id(id: str) -> ResponseArticle:
    """Get one article from storage if exists

    Args:
        id (str): Id of the article to get

    Raises:
        InvalidRequestedIdError: If provided argument 'id' is invalid.

    Returns:
        ResponseArticle | None: Article
    """
    try:
        article_id: ArticleId = ArticleId(id=id)
    except InvalidArticleIdError:
        raise InvalidRequestedIdError(f"Id '{id}' is not a valid article Id")

    article: Article | None = _get(article_id)
    if article:
        return ResponseArticle.from_article(article)
    else:
        raise ArticleNotFoundError(f"Id '{id}' doest not exist.")


def create(request: RequestArticle) -> str:
    """Create a new article

    Args:
        request (RequestArticle): Article to create

    Returns:
        ArticleId: Id of newly created article
    """
    logger.debug("Creating article...")
    new: Article = RequestArticle.to_article(request)
    response: ResponseArticle = ResponseArticle.from_article(new)
    _add(new)
    if not response.id:
        # Mainly for type checking, that sould never happen.
        raise InvalidArticleIdError("Article Id is invalid")
    return response.id


def update(id: str, request: RequestArticle) -> None:
    """Update the article with given Id if it exists.

    Args:
        id (str): Id of the article to update
        request (RequestArticle): New article

    Raises:
        InvalidRequestedIdError: If provided argument 'id' is invalid.
        ArticleNotFoundError: If provided argument 'id' cannot be found.
    """
    try:
        article_id: ArticleId = ArticleId(id=id)
    except InvalidArticleIdError:
        raise InvalidRequestedIdError(f"Id '{id}' is not a valid article Id")

    old: Article | None = _get(article_id)
    if old:
        new: Article = RequestArticle.to_article(request)
        _update(old, new)
    else:
        raise ArticleNotFoundError(f"Id '{id}' doest not exist.")
