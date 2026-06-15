import smtplib
from typing import Annotated

from fastapi import Depends

from fastid.email.client import MailClient
from fastid.email.config import email_settings


def get_smtp() -> smtplib.SMTP:
    server: smtplib.SMTP
    if email_settings.smtp_ssl:
        server = smtplib.SMTP_SSL(email_settings.smtp_host, email_settings.smtp_port)
    else:
        server = smtplib.SMTP(email_settings.smtp_host, email_settings.smtp_port)
    if email_settings.smtp_auth:
        server.login(email_settings.smtp_username, email_settings.smtp_password)
    return server


def get_mail(server: Annotated[smtplib.SMTP, Depends(get_smtp)]) -> MailClient:
    return MailClient(
        server,
        mail_from=email_settings.smtp_from,
    )


MailDep = Annotated[MailClient, Depends(get_mail)]
