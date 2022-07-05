class CoriolisException(Exception):
    pass


class HTTPError(Exception):

    """Base exception for HTTP errors."""

    def __init__(self, message, status_code=0):
        super(HTTPError, self).__init__(message)
        self.status_code = status_code


class HTTPAuthError(HTTPError):

    """Raised for 401 Unauthorized responses from the server."""

    def __init__(self, message, status_code=401):
        super(HTTPAuthError, self).__init__(message, status_code)


class MetalHubEndpointNotFound(CoriolisException):
    """
    Raised when metal-hub endpoint could not be found in service catalogue
    """

    def __init__(self, *args, **kw):
        super(MetalHubEndpointNotFound, self).__init__(
            "no metal-hub endpoint found in service catalogue")
