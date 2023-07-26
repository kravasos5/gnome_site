from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.signing import BadSignature
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import RegisterUserForm
from .models import *

# Главная страница
from .utilities import signer


def main(request):
    return render(request, 'gnome_main/main.html')

# Блог
def blog(request):
    return render(request, 'gnome_main/blog.html')

# Вход в аккаунт
class Login_view(LoginView):
    template_name = 'gnome_main/login.html'

    def get_success_url(self):
        return reverse_lazy('gnome_main:main')

# Выход из аккаунта
class Logout_view(LoginRequiredMixin, LogoutView):
    template_name = 'gnome_main/main.html'

# Регистрация
class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'gnome_main/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('gnome_main:register-confrim')

# подтверждение регистрации
class RegisterConfrimView(TemplateView):
    template_name = 'gnome_main/register_confrim.html'

# подтверждение регистрации
def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'gnome_main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'gnome_main/user_is_activated.html'
    else:
        template = 'gnome_main/register_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)