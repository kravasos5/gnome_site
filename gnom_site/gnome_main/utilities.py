from datetime import datetime
from os.path import splitext
from random import choice

from django.core.mail import EmailMessage
from django.core.signing import Signer
from django.template.loader import render_to_string

from gnom_site.settings import ALLOWED_HOSTS

# создаю подпись для дополнительной защиты данных
signer = Signer()

#обработчик сигнала регистрации нового пользователя
def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://127.0.0.1:8000'
    context = {'user': user, 'host': host,
               'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.html',
                               context)
    body_text = render_to_string('email/activation_letter_body.html',
                                 context)
    # user.email_user(subject, body_text)
    em = EmailMessage(subject=subject, body=body_text,
                      to=[f'{user.email}',])
    em.send()

# обработчик сигнала удаления пользователя
def user_delete(user, protocol, domain):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://127.0.0.1:8000'
    context = {'user': user, 'host': host,
               'sign': signer.sign(user.username), 'slug': user.slug}
    subject = render_to_string('email/delete_user_subject.txt',
                               context)
    body_text = render_to_string('email/delete_user_body.html',
                                 context)
    em = EmailMessage(subject=subject, body=body_text,
                      to=[f'{user.email}', ])
    em.send()

# генератор имени для фото в посте
def get_image_path_post(instance, filename):
    return f'{str(datetime.now())[:10]}-{splitext(filename)[0]}{splitext(filename)[1]}'

# получение ip адреса пользователя
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    print(ip)
    return ip

def random_key(len):
    return ''.join([choice('qwqertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM') for _ in range(20)])