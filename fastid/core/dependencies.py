from fastid.core.config import main_settings
from fastid.core.logging.config import config_dict
from fastid.core.logging.provider import LogProvider

log_provider = LogProvider(config_dict)
log = log_provider.logger(main_settings.discovery_name)
