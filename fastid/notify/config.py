from collections.abc import Mapping

from fastid.auth.schemas import ContactType
from fastid.core.schemas import BaseSettings


class NotificationSettings(BaseSettings):
    contact_priority: Mapping[ContactType, int] = {ContactType.telegram: 0, ContactType.email: 1}


notify_settings = NotificationSettings()
