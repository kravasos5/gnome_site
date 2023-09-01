from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.signing import BadSignature
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordResetDoneView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView, DetailView, ListView

from .forms import RegisterUserForm, ChangeUserInfoForm, DeleteUserForm
from .mixins import PostViewCountMixin
from .models import *
from .apps import user_delete_signal
from .utilities import signer

# Главная страница
def main(request):
    # print(request.context)
    # context = {'cur_user': cur_user,}
    return render(request, 'gnome_main/main.html') #, context=context

# Блог
class BlogView(ListView):
    '''Представление блога'''
    model = Post
    template_name = 'gnome_main/blog.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        subscriptions = AdvUser.objects.filter(subscriptions=self.request.user)
        rubrics = SubRubric.objects.all()
        context['rubrics'] = rubrics
        context['subscriptions'] = subscriptions
        return context

    def post(self, request, *args, **kwargs):
        for (key, value) in dict(request.POST).items():
            if key == 'csrfmiddlewaretoken':
                pass
            elif value[0] == '' or value[0] == 'false' or key == 'x' or key == 'y':
                pass
            else:
                print(f'{key} --- {value}')

        posts = Post.objects.all()
        subscriptions = AdvUser.objects.filter(subscriptions=request.user)
        rubrics = SubRubric.objects.all()
        context = {'rubrics': rubrics, 'subscriptions': subscriptions, 'posts': posts}
        return render(request, 'gnome_main/blog.html', context)

class PostView(PostViewCountMixin, DetailView):
    '''Представление детального просмотра поста'''
    model = Post
    template_name = 'gnome_main/show_post.html'
    context_object_name = 'post'

class UserProfile(View):
    '''Представление профиля пользователя'''
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

class Login_view(LoginView):
    '''Вход в аккаунт'''
    template_name = 'gnome_main/login.html'

    def get_success_url(self):
        return reverse_lazy('gnome_main:main')

class Logout_view(LoginRequiredMixin, LogoutView):
    '''Выход из аккаунта'''
    template_name = 'gnome_main/main.html'


class RegisterUserView(CreateView):
    '''Регистрация'''
    model = AdvUser
    template_name = 'gnome_main/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('gnome_main:register-confrim')


class RegisterConfrimView(TemplateView):
    '''подтверждение регистрации'''
    template_name = 'gnome_main/register_confrim.html'

# активация пользователя
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

class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    '''Изменение данных пользователя'''
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

    def form_valid(self, form):
        super().form_valid(form)
        response_data = {
            'success': True,
            'success_url': self.get_success_url()
        }
        return JsonResponse(response_data)

# Сброс пароля
class PasswordReset(PasswordResetView):
    '''Представление сброса пароля'''
    template_name = 'gnome_main/password_reset.html'
    html_email_template_name = 'email/reset_letter_body.html'
    email_template_name = 'email/reset_letter_body.txt'
    subject_template_name = 'email/reset_letter_subject.txt'
    success_url = reverse_lazy('gnome_main:password-reset-done')

class PasswordResetDone(PasswordResetDoneView):
    '''Оповещение о отправленном письме'''
    template_name = 'gnome_main/password_reset_done.html'

class PasswordResetConfrim(PasswordResetConfirmView):
    '''Представление подтверждения сброса пароля (ввод нового пароля)'''
    template_name = 'gnome_main/password_reset_confrim.html'
    success_url = reverse_lazy('gnome_main:password-reset-complete')

class PasswordResetComplete(PasswordResetCompleteView):
    '''Пароль успешно сброшен'''
    template_name = 'gnome_main/password_reset_complete.html'

# Удаление пользователя
@login_required
def deleteUserStarting(request, slug):
    protocol = request.scheme
    domain = request.get_host()
    user_delete_signal.send('deleteUserStarting', instance=request.user, protocol=protocol, domain=domain)
    return render(request, 'gnome_main/delete_user_starting.html')

class DeleteUserView(LoginRequiredMixin, DeleteView):
    '''Удаление аккаунта пользователя'''
    model = AdvUser
    template_name = 'gnome_main/delete_user.html'
    success_url = reverse_lazy('gnome_main:main')
    form_class = DeleteUserForm

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.id
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = DeleteUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = AdvUser.objects.get(id=self.user_id)
            if username == user.username and user.check_password(password):
                logout(request)
                messages.add_message(request, messages.SUCCESS,
                                     'Пользователь удалён')
                return super().post(request, *args, **kwargs)
            else:
                messages.add_message(request, messages.ERROR, "Поля заполнены неверно")
                return render(request, 'gnome_main/delete_user.html', {'form': form})
        else:
            messages.add_message(request, messages.ERROR, "Неправильная форма")
            return render(request, 'gnome_main/delete_user.html', {'form': form})

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class PostDetailView(PostViewCountMixin, DetailView):
    '''Детальный просмотр записи'''
    model = Post
    template_name = 'gnome_main/show_post.html'