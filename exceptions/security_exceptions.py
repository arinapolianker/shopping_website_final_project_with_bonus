from fastapi import HTTPException
from starlette import status


def token_exception() -> HTTPException:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="The token provided is invalid"
    )
    return credentials_exception


def username_taken_exception() -> HTTPException:
    """

    :rtype: object
    """
    username_taken_exception_response = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Username taken - select a different username"
    )
    return username_taken_exception_response


def user_credentials_exception() -> HTTPException:
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )
    return token_exception_response
