from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import BadSignature
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import RegisterUserForm, ChangeUserInfoForm
from .models import *

from .utilities import signer

# Главная страница
def main(request):
    # print(request.context)
    # context = {'cur_user': cur_user,}
    return render(request, 'gnome_main/main.html') #, context=context

# Блог
def blog(request):
    return render(request, 'gnome_main/blog.html')

# профиль пользователя
# def user_profile(request, slug):
#     cur_user = get_object_or_404(AdvUser, slug=slug)
#     user = request.user
#     count = cur_user.subscriptions.count()
#     is_subscribe = cur_user.subscriptions.filter(id=user.id).exists()
#     context = {'cur_user': cur_user, 'sub_count': count, 'is_subscribe': is_subscribe, 'posts_count': 10}
#     return render(request, 'gnome_main/user_profile.html', context=context)

class UserProfile(View):
    ''''Представление профиля пользователя'''
    template_name = 'gnome_main/user_profile.html'

    def get(self, request, slug):
        cur_user = get_object_or_404(AdvUser, slug=slug)
        user = request.user
        count = cur_user.subscriptions.count()
        is_subscribe = cur_user.subscriptions.filter(id=user.id).exists()
        context = {'cur_user': cur_user, 'sub_count': count, 'is_subscribe': is_subscribe, 'posts_count': 10}
        return render(request, 'gnome_main/user_profile.html', context=context)

    def post(self, request, slug):
        subscribe = request.POST.get('subscribe')
        cur_user = get_object_or_404(AdvUser, slug=slug)
        user = request.user
        if subscribe == 'true':
            cur_user.subscriptions.remove(user)
        elif subscribe == 'false':
            cur_user.subscriptions.add(user)
        return JsonResponse(data={'status': '200-ok'}, status=200)

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

# Изменение данных пользователя
class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'gnome_main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_message = 'Данные изменены'

    def setup(self, request, *args, **kwargs):
        self.id = request.user.id
        self.slug = request.user.slug
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return  get_object_or_404(queryset, id=self.id)

    def get_success_url(self):
        return reverse_lazy('gnome_main:user-profile', kwargs={'slug': self.slug})