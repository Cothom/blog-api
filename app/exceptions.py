"""Server exceptions"""


class ServerError(RuntimeError):
    """Root class for errors"""

    message = "Unknown server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail
        super().__init__(self.message, self.detail)


class InvalidArticleIdError(ServerError):
    """Raised in case of using article with an invalid Id"""

    message = "Article Id is not valid"


class InvalidRequestedIdError(ServerError):
    """Raised if a request is received with an invalid Id"""

    message = "Requested article Id is not valid"


class ArticleNotFoundError(ServerError):
    """Raised if no article can be found with the given Id"""

    message = "Requested article Id doest not exist"
