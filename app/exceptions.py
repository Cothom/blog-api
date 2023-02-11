"""Server exceptions"""


class ServerError(RuntimeError):
    """Root class for errors"""

    message = "Unknown server error"

    def __init__(self, detail: str | None):
        self.detail = detail
        super().__init__(self.message, self.detail)


class InvalidArticleIdError(ServerError):
    """Raised in case of using article with an invalid Id"""

    message = "Article Id is not valid"
