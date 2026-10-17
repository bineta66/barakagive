from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class AIErrorType(str, Enum):
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


TRANSIENT_ERRORS = {
    AIErrorType.RATE_LIMIT,
    AIErrorType.TIMEOUT,
    AIErrorType.NETWORK_ERROR,
    AIErrorType.SERVER_ERROR,
}


class AIProviderError(Exception):
    def __init__(self, error_type: AIErrorType, message: str = "Provider request failed", status: int | None = None):
        super().__init__(message)
        self.error_type = error_type
        self.status = status
        self.retryable = error_type in TRANSIENT_ERRORS


@dataclass
class AIResponse:
    content: str
    provider: str
    model: str
    request_id: str
    latency_ms: int


class AIProvider(Protocol):
    name: str
    model_name: str

    def is_enabled(self) -> bool: ...

    def generate(self, prompt: str, *, timeout: float) -> str: ...


def error_from_status(status: int) -> AIProviderError:
    if status == 429:
        kind = AIErrorType.RATE_LIMIT
    elif status in (408,):
        kind = AIErrorType.TIMEOUT
    elif status >= 500:
        kind = AIErrorType.SERVER_ERROR
    elif status in (401, 403):
        kind = AIErrorType.AUTH_ERROR
    elif status == 400:
        kind = AIErrorType.BAD_REQUEST
    else:
        kind = AIErrorType.UNKNOWN_ERROR
    error = AIProviderError(kind, status=status)
    # Keep fallback restricted to the explicitly transient gateway statuses.
    if status >= 500:
        error.retryable = status in (502, 503, 504)
    return error
