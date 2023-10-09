from django.apps import AppConfig
from django.dispatch import Signal

from .utilities import send_activation_notification, user_delete

class GnomeMainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gnome_main'
    verbose_name = 'Сайт о гномах'

# сигнал регистрации нового пользователя
user_registered = Signal()

def user_registered_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])

user_registered.connect(user_registered_dispatcher)

# сигнал удаления аккаунта пользователя
user_delete_signal = Signal()

def user_delete_dispatcher(sender, **kwargs):
    user_delete(kwargs['instance'], kwargs['protocol'], kwargs['domain'])

user_delete_signal.connect(user_delete_dispatcher)