import logging
import time

log = logging.getLogger("api.access")


class RequestLogMiddleware:
    """Registra metadados sem registrar corpo, querystring, credenciais ou PII."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        elapsed_ms = (time.monotonic() - start) * 1000
        log.info("method=%s path=%s status=%s elapsed_ms=%.1f", request.method, request.path, response.status_code, elapsed_ms)
        return response
