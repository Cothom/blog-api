"""Entities handled by API and functions to manipulate them."""

import enum
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.utils import datetime_to_iso_string, iso_string_to_datetime


class OperationType(enum.Enum):
    """Classify the operation that is done on stored entities"""

    CREATED = 0
    READ = 1
    UPDATED = 2
    DELETED = 3


@dataclass
class Article:
    """Data class representing an article of the blog."""

    content: str
    title: str
    date: datetime
    uuid: UUID = uuid4()


class RequestArticle(BaseModel):
    """Class representing an article the way it is sent by API consumer"""

    title: str
    content: str
    creation: str | None
    # On creation request, no idea is yet assigned to article

    @staticmethod
    def to_article(request: "RequestArticle") -> Article:
        """Converts an instance of this class into a new instance of Article

        Args:
            request (RequestArticle): The article to convert

        Returns:
            Article: The converted article
        """
        kwargs: dict[str, str | datetime] = {
            "title": request.title,
            "content": request.content,
            "date": iso_string_to_datetime(request.creation),
        }
        return Article(**kwargs)  # type: ignore


class ResponseArticle(RequestArticle):
    """Class representing an article the way it is returned to API consumer"""

    id: str  # In a response, there is always already an id assigned to article

    @staticmethod
    def from_article(article: Article) -> "ResponseArticle":
        """Converts an instance of Article into a new instance of this class

        Args:
            article (Article): The article to convert

        Returns:
            ResponseArticle: The converted article
        """
        title: str = article.title
        content: str = article.content
        creation: str = datetime_to_iso_string(article.date)
        id: str = article.uuid.hex
        return ResponseArticle(
            content=content, title=title, creation=creation, id=id
        )


# Represents the in-memory storage
_all: dict[UUID, Article] = {}


def _add(article: Article) -> None:
    """Add an Article entity to the storage

    Args:
        article (Article): article to store
    """
    _all[article.uuid] = article


def _get(id: str) -> Article | None:
    """Fetch the article corresponding to given Id from storage if exists

    Args:
        id (str): Id of the article to get

    Returns:
        Article | None: Fetched article if exists, None otherwise
    """
    uuid: UUID = UUID(id)
    return _all.get(uuid, None)


def _update(old: Article, new: Article) -> None:
    """Replace old article with the new one

    Args:
        old (Article): Article to replace
        new (Article): New article
    """
    # UUID must be preserved when updating
    new.uuid = old.uuid
    _all[old.uuid] = new


def get_all() -> tuple[list[ResponseArticle], OperationType]:
    """Get all stored articles and return them as ResponseArticle objects
    along with an OperationType

    Returns:
        tuple[list[ResponseArticle], OperationType]: All articles and operation
    """
    return (
        [ResponseArticle.from_article(article) for article in _all.values()],
        OperationType.READ,
    )


def get_by_id(id: str) -> tuple[ResponseArticle | None, OperationType]:
    """Get one article from storage if exists

    Args:
        id (str): Id of the article to get

    Returns:
        tuple[ResponseArticle | None, OperationType]: Article and operation
    """
    article: Article | None = _get(id)
    if article is not None:
        return ResponseArticle.from_article(article), OperationType.READ
    else:
        return None, OperationType.READ


def create(request: RequestArticle) -> tuple[str, OperationType]:
    """Create a new article

    Args:
        request (RequestArticle): Article to create

    Returns:
        OperationType: Operation type
    """
    new: Article = RequestArticle.to_article(request)
    response: ResponseArticle = ResponseArticle.from_article(new)
    _add(new)
    return response.id, OperationType.CREATED


def update(id: str, request: RequestArticle) -> OperationType:
    """Update the article with given Id if exists, create it otherwise

    Args:
        id (str): Id of the article to update
        request (RequestArticle): New article

    Returns:
        OperationType: Operation type indicating if it was created or updated
    """
    old: Article | None = _get(id)
    new: Article = RequestArticle.to_article(request)
    if old:
        _update(old, new)
        return OperationType.UPDATED
    else:
        _add(new)
        return OperationType.CREATED
