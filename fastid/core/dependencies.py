from fastid.core.config import branding_settings
from fastid.core.logging.config import config_dict
from fastid.core.logging.provider import LogProvider

log_provider = LogProvider(config_dict)
log = log_provider.logger(branding_settings.service_name)
