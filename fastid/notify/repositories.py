from typing import Any

from fastid.database.repository import SQLAlchemyRepository
from fastid.database.specification import Specification
from fastid.notify.models import EmailTemplate, TelegramTemplate


class EmailTemplateRepository(SQLAlchemyRepository[EmailTemplate]):
    model_type = EmailTemplate


class EmailTemplateSlugSpecification(Specification):
    def __init__(self, slug: str) -> None:
        self.slug = slug

    def apply(self, stmt: Any) -> Any:
        return stmt.where(EmailTemplate.slug == self.slug)


class TelegramTemplateRepository(SQLAlchemyRepository[TelegramTemplate]):
    model_type = TelegramTemplate


class TelegramTemplateSlugSpecification(Specification):
    def __init__(self, slug: str) -> None:
        self.slug = slug

    def apply(self, stmt: Any) -> Any:
        return stmt.where(TelegramTemplate.slug == self.slug)
