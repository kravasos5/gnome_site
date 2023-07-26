from django.core.mail import EmailMessage
from django.core.signing import Signer
from django.template.loader import render_to_string

from gnom_site.settings import ALLOWED_HOSTS
print(ALLOWED_HOSTS)

# создаю подпись для дополнительной защиты данных
signer = Signer()

#обработчик сигнала регистрации нового пользователя
def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http//localhost:8000'
    print('Сигнал дошёл до send_activation_notification')
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