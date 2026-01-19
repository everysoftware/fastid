from sqlalchemy_continuum.utils import transaction_class, version_class

from fastid.apps.models import App
from fastid.auth.models import User
from fastid.notify.models import EmailTemplate, TelegramTemplate

Transaction = transaction_class(User)

UserVersion = version_class(User)
AppVersion = version_class(App)
EmailTemplateVersion = version_class(EmailTemplate)
TelegramTemplateVersion = version_class(TelegramTemplate)
