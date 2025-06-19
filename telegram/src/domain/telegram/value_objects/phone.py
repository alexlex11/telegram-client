import re
from dataclasses import dataclass
from typing import final

from src.domain.common.exceptions import DomainError
from src.domain.common.value_objects import ValueObject

PHONE_LENGTH = 11
PHONE_PATTERN = re.compile(r"^[78]\d{10}$")


@dataclass(eq=False)
class WrongPhoneValueError(ValueError, DomainError):
    phone: str


class EmptyPhoneError(WrongPhoneValueError):
    @property
    def title(self) -> str:
        return "Phone number can't be empty"


class TooShortPhoneError(WrongPhoneValueError):
    @property
    def title(self) -> str:
        return f'Too short phone number "{self.phone}"'


class WrongPhoneFormatError(WrongPhoneValueError):
    @property
    def title(self) -> str:
        return f'Wrong phone number format "{self.phone}"'


@final
@dataclass(frozen=True)
class PhoneNumber(ValueObject[str | None]):
    value: str | None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.value is None:
            return

        cleaned = self._normalize(self.value)

        if not cleaned:
            raise EmptyPhoneError(self.value)
        if len(cleaned) < 10:
            raise TooShortPhoneError(self.value)
        if len(cleaned) != PHONE_LENGTH or not PHONE_PATTERN.match(cleaned):
            raise WrongPhoneFormatError(self.value)

    @staticmethod
    def _normalize(phone: str) -> str:
        """Нормализует номер телефона к формату 7XXXXXXXXXX."""
        cleaned = re.sub(r"[^\d]", "", phone.strip())

        if cleaned.startswith("8") and len(cleaned) == 11:
            return "7" + cleaned[1:]
        elif cleaned.startswith("+7") and len(cleaned) == 12:
            return "7" + cleaned[2:]
        elif cleaned.startswith("7") and len(cleaned) == 11:
            return cleaned
        elif len(cleaned) == 10:
            return "7" + cleaned

        return cleaned

    def exists(self) -> bool:
        return self.value is not None

    @property
    def normalized(self) -> str | None:
        """Возвращает нормализованный номер или None."""
        if self.value is None:
            return None
        return self._normalize(self.value)
