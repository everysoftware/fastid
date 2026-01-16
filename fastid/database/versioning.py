from sqlalchemy_continuum.utils import version_class

from fastid.apps.models import App
from fastid.auth.models import User
from fastid.notify.models import EmailTemplate, TelegramTemplate

UserVersion = version_class(User)
AppVersion = version_class(App)
EmailTemplateVersion = version_class(EmailTemplate)
TelegramTemplateVersion = version_class(TelegramTemplate)
