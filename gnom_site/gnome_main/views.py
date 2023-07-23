from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy


# Главная страница
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
def register_view(request):
    return render(request, 'gnome_main/register.html')

# подтверждение регистрации
def register_confrim(request):
    return render(request, 'gnome_main/register_confrim.html')

# регистрация завершена оповещение
def register_complete(request):
    return render(request, 'gnome_main/register_complete.html')

# регистрация завершена оповещение
def register_complete(request):
    return render(request, 'gnome_main/register_complete.html')