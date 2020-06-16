import functools

from fastapi import status, HTTPException


class ServiceError(Exception):
    pass


class ValidationError(ServiceError):
    pass


class AuthenticationError(ServiceError):
    pass


class AuthorizationError(ServiceError):
    pass


class NotFoundError(ServiceError):
    pass


EXCEPTION_RESPONSE = {
    ValidationError: {
        'status': status.HTTP_400_BAD_REQUEST
    },
    AuthenticationError: {
        'status': status.HTTP_401_UNAUTHORIZED,
        'headers': {'WWW-Authenticate': 'Bearer'}
    },
    AuthorizationError: {
        'status': status.HTTP_403_FORBIDDEN
    },
    NotFoundError: {
        'status': status.HTTP_404_NOT_FOUND
    }
}

DEFAULT_RESPONSE = {
    'status': status.HTTP_500_INTERNAL_SERVER_ERROR
}


def handled(controller):
    @functools.wraps(controller)
    def wrap_controller(*args, **kwargs):
        try:
            return controller(*args, **kwargs)

        except Exception as e:
            response_data = EXCEPTION_RESPONSE.get(type(e), DEFAULT_RESPONSE)
            raise HTTPException(
                status_code=response_data.get('status'),
                detail=response_data.get('detail') or f'{e}',
                headers=response_data.get('headers')
            )

    return wrap_controller

