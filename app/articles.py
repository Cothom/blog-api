import enum
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.utils import datetime_to_iso_string, iso_string_to_datetime


class OperationType(enum.Enum):
    CREATED = 0
    READ = 1
    UPDATED = 2
    DELETED = 3


@dataclass
class Article:
    content: str
    title: str
    date: datetime
    uuid: UUID = uuid4()


class RequestArticle(BaseModel):
    title: str
    content: str
    creation: str | None
    id: str | None  # On creation request, no idea is yet assigned to article

    @staticmethod
    def to_article(request: "RequestArticle") -> Article:
        kwargs: dict[str, str | datetime | UUID] = {
            "title": request.title,
            "content": request.content,
            "date": iso_string_to_datetime(request.creation),
        }
        if request.id:
            kwargs["uuid"] = UUID(request.id)
        return Article(**kwargs)  # type: ignore


class ResponseArticle(RequestArticle):
    id: str  # In a response, there is always already an id assigne to article

    @staticmethod
    def from_article(article: Article) -> "ResponseArticle":
        title = article.title
        content = article.content
        creation = datetime_to_iso_string(article.date)
        id = article.uuid.hex
        return ResponseArticle(
            content=content, title=title, creation=creation, id=id
        )


_all: dict[UUID, Article] = {}


def _add(article: Article) -> None:
    _all[article.uuid] = article


def _get(id: str) -> Article | None:
    uuid = UUID(id)
    return _all.get(uuid, None)


def _update(old: Article, new: Article) -> None:
    # UUID must be preserved when updating
    new.uuid = old.uuid
    _all[old.uuid] = new


def get_all() -> tuple[list[ResponseArticle], OperationType]:
    return (
        [ResponseArticle.from_article(article) for article in _all.values()],
        OperationType.READ,
    )


def get_by_id(id: str) -> tuple[ResponseArticle | None, OperationType]:
    article: Article | None = _get(id)
    if article is not None:
        return ResponseArticle.from_article(article), OperationType.READ
    else:
        return None, OperationType.READ


def create(request: RequestArticle) -> OperationType:
    new = RequestArticle.to_article(request)
    _add(new)
    return OperationType.CREATED


def update(id: str, request: RequestArticle) -> OperationType:
    old = _get(id)
    new = RequestArticle.to_article(request)
    if old:
        _update(old, new)
        return OperationType.UPDATED
    else:
        _add(new)
        return OperationType.CREATED
