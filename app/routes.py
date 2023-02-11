"""Endpoints of the API"""

import logging

from fastapi import FastAPI, HTTPException, Response

from app.articles import (
    OperationType,
    RequestArticle,
    ResponseArticle,
    create,
    get_all,
    get_by_id,
    update,
)

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
def hello_world():
    """Dummy function returning an "Hello World!" message

    Returns:
        None
    """
    logger.info("Request 'hello-world' received!")
    return {"message": "Hello World!"}


@app.get("/articles")
def get_all_articles() -> list[ResponseArticle]:
    """Get all articles

    Returns:
        list[ResponseArticle]: The list of articles to return
    """
    articles, _ = get_all()
    return articles


@app.get("/articles/{article_id}")
def get_article(article_id: str) -> ResponseArticle:
    """Get one article according to given Id

    Args:
        article_id (str): Id of the requested article

    Raises:
        HTTPException: Returns 404 if article is not found

    Returns:
        ResponseArticle: Requested article
    """
    article, _ = get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return article


@app.post("/articles", status_code=201)
def new_article(article: RequestArticle, response: Response) -> None:
    """Create a new article

    Args:
        article (RequestArticle): Article to create
    """
    article_id, _ = create(article)
    # New created article's Id must be returned for consumer to re-access later
    response.headers["Location"] = article_id


@app.put("/articles/{article_id}", status_code=204)
def update_article(
    article_id: str, article: RequestArticle, response: Response
) -> None:
    """Update an article
    The article is updated if it already exists
    The article is created if it does not already exists

    Args:
        article_id (str): Id of the requested article to update
        article (RequestArticle): New content for the article
        response (Response): Arg provided by FastAPI to edit HTTP code
    """
    op: OperationType = update(article_id, article)
    if op == OperationType.CREATED:
        response.status_code = 201
