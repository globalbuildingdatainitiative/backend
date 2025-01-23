from typing import NewType

import strawberry
from email_validator import validate_email

EmailAddress = strawberry.scalar(
    NewType("EmailAddress", str),
    serialize=lambda v: str(v),
    parse_value=lambda v: validate_email(v).normalized,
)
