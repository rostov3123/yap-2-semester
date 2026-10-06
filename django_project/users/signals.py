"""События входа, выхода и ошибки входа без записи учётных данных."""
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def login_success(sender, request, user, **kwargs):
    logger.info('Успешный вход user_id=%s', user.pk)

@receiver(user_logged_out)
def logout_success(sender, request, user, **kwargs):
    logger.info('Выход user_id=%s', getattr(user, 'pk', None))

@receiver(user_login_failed)
def login_failure(sender, credentials, request, **kwargs):
    logger.warning('Неудачный вход: неверные учётные данные')
