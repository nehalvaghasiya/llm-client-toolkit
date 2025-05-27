import abc
import json
from typing import Generic, Type, TypeVar

from pydantic import BaseModel, ValidationError

__all__ = [
    "ParserError",
    "Parser",
    "JsonParser",
    "PydanticParser",
]

T = TypeVar("T")


class ParserError(RuntimeError):
    """Raised when a :class:`Parser` fails to turn text into structured data."""


class Parser(abc.ABC, Generic[T]):
    """Anything that converts *raw string* → *structured output*."""

    @abc.abstractmethod
    def parse(self, text: str) -> T:
        raise NotImplementedError


class JsonParser(Parser[dict]):
    """Strict JSON loader."""

    def parse(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ParserError(str(e)) from e


class PydanticParser(Parser[T]):
    """Validate JSON output against a user-supplied pydantic model."""

    def __init__(self, schema: Type[BaseModel]):
        self._schema = schema

    def parse(self, text: str) -> T:
        try:
            data = json.loads(text)
            return self._schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ParserError(str(e)) from e
