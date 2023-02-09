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

app = FastAPI()


@app.get("/")
def hello_world():
    return {"message": "Hello World!"}


@app.get("/articles")
def get_all_articles() -> list[ResponseArticle]:
    articles, _ = get_all()
    return articles


@app.get("/articles/{article_id}")
def get_article(article_id: str) -> ResponseArticle:
    article, _ = get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return article


@app.post("/articles", status_code=201)
def new_article(article: RequestArticle) -> None:
    create(article)


@app.put("/articles/{article_id}", status_code=204)
def update_article(
    article_id: str, article: RequestArticle, response: Response
) -> None:
    op: OperationType = update(article_id, article)
    if op == OperationType.CREATED:
        response.status_code = 201
