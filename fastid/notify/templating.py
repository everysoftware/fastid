from jinja2 import Environment, FileSystemLoader

from fastid.core.config import branding_settings

jinja_env = Environment(autoescape=True, loader=FileSystemLoader("templates"))
jinja_env.globals["from_name"] = branding_settings.notify_from
