
# dao exceptions
class DatabaseError(Exception):
    """Exception raised for errors in database operations."""
    pass


# service class exceptions
class UserNotFoundError(Exception):
    """Exception raised when a user is not found."""
    pass

class RateLimitError(Exception):
    """Exception raised when a rate limit is exceeded."""
    pass

class InternalServerError(Exception):
    """Exception raised when an internal server error occurs."""
    pass

class BadRequestError(Exception):
    """Exception raised when a bad request is made."""
    pass

class ConversationNotFoundError(Exception):
    """Exception raised when a conversation is not found."""
    pass