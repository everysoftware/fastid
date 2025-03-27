from app.logging.config import config_dict
from app.logging.provider import LogProvider
from app.main.config import main_settings

provider = LogProvider(config_dict)
log = provider.logger(main_settings.discovery_name)
