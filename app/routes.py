"""Endpoints of the API"""

import logging

from fastapi import FastAPI, HTTPException, Response

from app.articles import (RequestArticle, ResponseArticle, create, get_all,
                          get_by_id, update)
from app.exceptions import ArticleNotFoundError, InvalidRequestedIdError

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
    articles = get_all()
    logger.debug(f"Returning {len(articles)} articles")
    return articles


@app.get("/articles/{article_id}")
def get_article(article_id: str) -> ResponseArticle:
    """Get one article according to given Id

    Args:
        article_id (str): Id of the requested article

    Raises:
        HTTPException: Returns 400 if article Id is invalid. Returns 404 if article is not found

    Returns:
        ResponseArticle: Requested article
    """
    logger.debug(f"Looking for article with id {article_id}")
    try:
        article = get_by_id(article_id)
    except InvalidRequestedIdError as irie:
        raise HTTPException(status_code=400, detail=irie.message)
    except ArticleNotFoundError as anfe:
        raise HTTPException(status_code=404, detail=anfe.message)

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return article


@app.post("/articles", status_code=201)
def new_article(article: RequestArticle, response: Response) -> None:
    """Create a new article

    Args:
        article (RequestArticle): Article to create
    """
    logger.info("Creating article...")
    article_id = create(article)
    # New created article's Id must be returned for consumer to re-access later
    article_location: str = "/articles/%s" % article_id
    response.headers["Location"] = article_location
    logger.debug(f"Location header: {article_location}")


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
    try:
        update(article_id, article)
    except InvalidRequestedIdError as irie:
        raise HTTPException(status_code=400, detail=irie.message)
    except ArticleNotFoundError as anfe:
        raise HTTPException(status_code=404, detail=anfe.message)
