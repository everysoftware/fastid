from fastid.core.config import CoreSettings, branding_settings, core_settings
from fastid.core.logging.config import config_dict
from fastid.core.logging.provider import LogProvider

log_provider = LogProvider(config_dict)
log = log_provider.logger(branding_settings.service_name)


def get_core_settings() -> CoreSettings:
    return core_settings
