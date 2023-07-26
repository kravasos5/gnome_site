from django.apps import AppConfig
from django.dispatch import Signal
from .utilities import send_activation_notification

class GnomeMainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gnome_main'
    verbose_name = 'Сайт о гномах'

user_registered = Signal()

def user_registered_dispatcher(sender, **kwargs):
    print('Сигнал дошёл до user_registered_dispatcher')
    send_activation_notification(kwargs['instance'])

user_registered.connect(user_registered_dispatcher)