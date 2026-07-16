from sqlalchemy_continuum.utils import transaction_class, version_class

from fastid.apps.models import App
from fastid.auth.models import User
from fastid.notify.models import EmailTemplate, TelegramTemplate
from fastid.oauth.models import OAuthAccount, OAuthProvider
from fastid.webhooks.models import Webhook

Transaction = transaction_class(User)

UserVersion = version_class(User)
OAuthAccountVersion = version_class(OAuthAccount)
AppVersion = version_class(App)
OAuthProviderVersion = version_class(OAuthProvider)
EmailTemplateVersion = version_class(EmailTemplate)
TelegramTemplateVersion = version_class(TelegramTemplate)
WebhookVersion = version_class(Webhook)
