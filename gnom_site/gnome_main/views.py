from time import mktime

from django.db.models.functions import TruncDate
from django.db.models.signals import post_save
from django.dispatch import Signal
from django.utils import timezone

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.signing import BadSignature
from django.db import IntegrityError
from django.db.models import Count
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordResetDoneView
from django.template.defaultfilters import truncatewords, safe
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView, DetailView, ListView

from .forms import RegisterUserForm, ChangeUserInfoForm, DeleteUserForm, PostReportForm, CommentReportForm, \
    PostCreationForm, AIFormSet
from .mixins import BlogMixin, NotificationCheckMixin, BlogFilterMixin, BlogSearchMixin, ViewIncrementMixin, \
    CommentDispatcherMixin, RecLoaderMixin, PostInfoAddMixin, CsrfMixin, SubscribeMixin, IsPostSubscribeMixin
from .models import *
from .apps import user_delete_signal
from .templatetags.profile_extras import date_ago, post_views, is_full, comment_pluralize
from .utilities import signer, get_client_ip


##############################################################
# Сигналы
##############################################################
# Обработчик сигнала создания нового комментария
def comment_save_dispathcher(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        post_author = instance.post.author
        if post_author != instance.user:
            title = 'c'
            message = f'Пользователь <a href="{instance.user.get_absolute_url()}" ' \
                      f'class="nametag">' \
                      f'{instance.user.username}</a> оставил комментарий под вашим ' \
                      f'постом <a href="{instance.post.get_absolute_url()}" class="nametag">' \
                      f'{instance.post.title}</a><br>' + \
                      f'Вот его текст: {instance.comment}'
            Notification.objects.create(user=post_author, title=title,
                                                    message=message)
# сигнал создания нового комментария
post_save.connect(comment_save_dispathcher, sender=SuperPostComment)
post_save.connect(comment_save_dispathcher, sender=SubPostComment)

# Обработчик сигнала создания новой жалобы на Пост
def post_report_save_dispathcher(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        type = instance.type

        title = 'r'
        message = f'Пользователь <a href="{instance.user.get_absolute_url()}" ' \
                  f'class="nametag">' \
                  f'{instance.user.username}</a> подал жалобу на ваш пост: ' \
                  f'<a href="{instance.post.get_absolute_url()}" class="nametag">' \
                  f'{instance.post.title}</a><br>' \
                  f'Тип жалобы: {type}'
        if instance.text:
            message += f'<br>Вот текст жалобы: {instance.text}'

        Notification.objects.create(user=instance.post.author, title=title,
                                                message=message)
# сигнал создания новой жалобы на Пост
post_save.connect(post_report_save_dispathcher, sender=PostReport)

# обработчик сигнала создания новой жалобы на Комментарий
def comment_report_save_dispathcher(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        type = instance.type

        title = 'r'
        message = f'Пользователь <a href="{instance.user.get_absolute_url()}" ' \
                  f'class="nametag">' \
                  f'{instance.user.username}</a> подал жалобу на ваш комментарий:<br>' \
                  f'{instance.comment.comment}<br>' \
                  f'Тип жалобы: {type}'
        if instance.text:
            message += f'<br>Вот текст жалобы: {instance.text}'

        Notification.objects.create(user=instance.comment.user, title=title,
                                                message=message)
# сигнал создания новой жалобы на Комментарий
post_save.connect(comment_report_save_dispathcher, sender=CommentReport)

# обработчик сигнала новой подписки
def user_subsript_notification(instance, user):
    message = f'Ваш новый подписчик: <a href={instance.get_absolute_url()} ' \
              f'class="nametag">' \
              f'{instance.username}</a>'
    Notification.objects.create(title='s', user=user, message=message)

# сигнал новой подписки на пользователя
user_subsript = Signal()

def user_subsript_dispatcher(sender, **kwargs):
    user_subsript_notification(kwargs['instance'], kwargs['user'])

user_subsript.connect(user_subsript_dispatcher)



##############################################################
# Представления
##############################################################
# Главная страница
class Main(NotificationCheckMixin, TemplateView):
    template_name = 'gnome_main/main.html'

class BlogBase:
    '''Блог базовый класс'''
    model = Post
    template_name = 'gnome_main/blog.html'
    context_object_name = 'posts'
    paginate_by = 10

# Блог
class BlogView(BlogBase, NotificationCheckMixin, CsrfMixin, BlogMixin, ListView):
    '''Представление блога'''

class BlogFilterView(BlogBase, NotificationCheckMixin, CsrfMixin, BlogFilterMixin, ListView):
    '''Представление блога с фильтром'''

class BlogSearchView(BlogBase, NotificationCheckMixin, CsrfMixin, BlogSearchMixin, ListView):
    '''Представление блога с фильтром'''

class PostView(NotificationCheckMixin, ViewIncrementMixin, CommentDispatcherMixin,
               RecLoaderMixin, PostInfoAddMixin, CsrfMixin, IsPostSubscribeMixin,
               SubscribeMixin, DetailView):
    '''Представление детального просмотра поста'''
    model = Post
    template_name = 'gnome_main/show_post.html'
    context_object_name = 'post'

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        d = dict(request.POST)
        # формирования контекста
        context = {}
        # если пользователь оставил SuperComment
        if 'new_supercomment' in d:
            self.new_supercomment(context, post, d['new_supercomment'][0])
        # если пользователь оставил SubComment
        elif 'new_subcomment' in d:
            self.new_subcomment(context, post, d['new_subcomment'][0],
                                d['s-username'][0], d['super-id'][0])
        # если пользователь поставил лайк/дизлайк на комментарий
        elif 'comment-new-info' in d:
            self.comment_like_dislike(d['data'][0], d['status'][0], d['comment-new-info'][0])
        # если пользователь поставил лайк/дизлайк на пост или добавил пост в избранное
        elif 'post-new-info' in d:
            self.add_info(d['data'][0], d['status'][0], post)
        # подгрузить дополнительные НАДкомментарии
        elif 'load_supercomments' in d:
            self.load_supercomments(context, d['filter'][0], d['ids'][0], post)
        # подгрузить рекомендации
        elif 'load_rec' in d:
            self.load_rec(context, post, d['ids'][0])
        # подгрузить дополнительные ПОДкомментарии
        elif 'load_subcomments' in d:
            self.load_subcomments(context, d['super_id'][0], int(d['start_scomment'][0]),
                                  int(d['end_scomment'][0]))
        # изменить комментарий
        elif 'change_comment' in d:
            self.change_comment(context, d['с_id'][0], d['change-comment-line'][0])
        # удалить комментарий
        elif 'delete_comment' in d:
            self.delete_comment(d['c_id'][0])
        # подписаться на автора поста
        elif 'subscribe' in d:
            self.subscribe(post.author, d['subscribe'][0])

        return JsonResponse(data=context, status=200)

class UserProfile(NotificationCheckMixin, PostInfoAddMixin, SubscribeMixin, CsrfMixin, TemplateView):
    '''Представление профиля пользователя'''
    template_name = 'gnome_main/user_profile.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        cur_user = get_object_or_404(AdvUser, slug=self.kwargs.get('slug'))
        count = cur_user.subscriptions.count()
        posts = Post.objects.filter(author=cur_user).order_by('-created_at')[:10]
        context['cur_user'] = cur_user
        context['sub_count'] = count
        context['posts_count'] = posts.count()
        context['posts'] = posts
        context['is_subscribe'] = cur_user.subscriptions.filter(id=self.request.user.id).exists()
        return context

    def post(self, request, slug):
        d = dict(request.POST)
        cur_user = get_object_or_404(AdvUser, slug=slug)
        # формирования контекста
        context = {}
        if 'subscribe' in d:
            self.subscribe(cur_user, d['subscribe'][0])
        elif 'filter' in d:
            try:
                context['posts'] = []
                if d['filter'][0] == 'popular':
                    posts = Post.objects.filter(is_active=True, author=cur_user) \
                                .distinct() \
                                .annotate(num_likes=Count('postlike'),
                                          num_dislikes=Count('postdislike'),
                                          num_comments=Count('postcomment'),
                                          num_favourite=Count('postfavourite'),
                                          views_count=Count('postviewcount')) \
                                .order_by('-views_count', '-num_likes',
                                          '-num_comments', '-num_favourite',
                                          'num_dislikes')
                elif d['filter'][0] == 'new':
                    posts = Post.objects.filter(is_active=True, author=cur_user) \
                                .distinct() \
                                .order_by('-created_at')
                elif d['filter'][0] == 'old':
                    posts = Post.objects.filter(is_active=True, author=cur_user) \
                                .distinct() \
                                .order_by('created_at')
                elif d['filter'][0] == 'more_views':
                    posts = Post.objects.filter(is_active=True, author=cur_user) \
                                .distinct() \
                                .annotate(views_count=Count('postviewcount')) \
                                .order_by('-views_count')
                elif d['filter'][0] == 'with_media':
                    posts = Post.objects.all() \
                                .distinct() \
                                .annotate(num_media=Count('postadditionalimage')) \
                                .filter(is_active=True, num_media__gt=0, author=cur_user)

                if 'ids' in d:
                    ids = d['ids'][0][1:-1].replace('"', '').split(',')
                    if ids[0] == '':
                        ids = []
                    posts = posts.exclude(id__in=ids)[:1]
                else:
                    posts = posts[:10]

                if posts:
                    for i in posts:
                        date = date_ago(i.created_at)
                        report = i.author.id == request.user.id
                        like_img = '/static/gnome_main/css/images/likes.png'
                        dislike_img = '/static/gnome_main/css/images/dislikes.png'
                        favourite_img = '/static/gnome_main/css/images/favourite.png'
                        if is_full(i.postlike_set, request.user.id):
                            like_img = '/static/gnome_main/css/images/likes_full.png'
                        if is_full(i.postdislike_set, request.user.id):
                            dislike_img = '/static/gnome_main/css/images/dislikes_full.png'
                        if is_full(i.postfavourite_set, request.user.id):
                            favourite_img = '/static/gnome_main/css/images/favourite_full.png'
                        context['posts'].append({
                            'id': i.id,
                            'post_url': i.get_absolute_url(),
                            'preview': i.preview.url,
                            'title': i.title,
                            'content': truncatewords(i.content, 100),
                            'authorname': i.author.username,
                            'created_at': date,
                            'views': post_views(i.get_view_count()),
                            'view_img': '/static/gnome_main/css/images/views.png',
                            'likes': i.get_like_count(),
                            'like_img': like_img,
                            'dislikes': i.get_dislike_count(),
                            'dislike_img': dislike_img,
                            'user_url': i.author.get_absolute_url(),
                            'comments': comment_pluralize(i.get_comment_count()),
                            'comment_img': '/static/gnome_main/css/images/comments.png',
                            'favourite_img': favourite_img,
                            'report': report,
                        })


                        if report == False:
                            context['posts'][-1]['report_url'] = f'/report/{i.slug}/post/'
                        else:
                            context['posts'][-1]['update_url'] = f'/post/update/{i.slug}/'
            except Exception as ex:
                return JsonResponse(data={'ex': f'Неверные данные post {ex}'}, status=400)
        elif 'post-new-info' in d:
            post = Post.objects.get(id=d['post_id'][0])
            self.add_info(data=d['data'][0], status=d['status'][0], post=post)

        return JsonResponse(data=context, status=200)

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
    template_name = 'gnome_main/register_confirm.html'

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

class ChangeUserInfoView(NotificationCheckMixin, SuccessMessageMixin, LoginRequiredMixin, UpdateView):
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
        return HttpResponseRedirect(self.get_success_url())

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
    template_name = 'gnome_main/password_reset_confirm.html'
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

class PostReportView(NotificationCheckMixin, LoginRequiredMixin, CreateView):
    model = PostReport
    template_name = 'gnome_main/report.html'
    form_class = PostReportForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        slug = self.kwargs['slug']
        context['slug'] = slug
        return context

    def get_success_url(self, *args, **kwargs):
        slug = self.kwargs['slug']
        return reverse('gnome_main:show-post', kwargs={'slug': slug})

    def form_valid(self, form, *args, **kwargs):
        form.instance.user = self.request.user
        slug = self.kwargs['slug']
        post = Post.objects.get(slug=slug)
        form.instance.post = post
        try:
            return super().form_valid(form)
        except IntegrityError as ex:
            answer = self.form_invalid(form, *args, **kwargs)
            return answer

    def form_invalid(self, form, *args, **kwargs):
        slug = self.kwargs['slug']
        post = Post.objects.get(slug=slug)
        if PostReport.objects.get(post_id=post, user_id=self.request.user):
            form.add_error(None, 'Вы уже отправили жалобу на данную запись')
        else:
            form.add_error(None, 'Ошибка при отправке жалобы')
        return super().form_invalid(form)

class CommentReportView(NotificationCheckMixin, LoginRequiredMixin, CreateView):
    model = PostReport
    template_name = 'gnome_main/report.html'
    form_class = CommentReportForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        slug = self.kwargs['slug']
        context['slug'] = slug
        return context

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse('gnome_main:show-post', kwargs={'slug': slug})

    def form_valid(self, form, *args, **kwargs):
        form.instance.user = self.request.user
        comment_id = self.kwargs['id']
        comment = PostComment.objects.get(id=comment_id)
        form.instance.comment = comment
        try:
            return super().form_valid(form)
        except IntegrityError as ex:
            answer = self.form_invalid(form, *args, **kwargs)
            return answer

    def form_invalid(self, form, *args, **kwargs):
        comment_id = self.kwargs['id']
        comment = PostComment.objects.get(id=comment_id)
        if CommentReport.objects.get(comment_id=comment, user_id=self.request.user):
            form.add_error(None, 'Вы уже отправили жалобу на данный комментарий')
        else:
            form.add_error(None, 'Ошибка при отправке жалобы')
        return super().form_invalid(form)

class PostInLine:
    '''Базовый класс для представлений создания и обновления поста'''
    form_class = PostCreationForm
    model = Post

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        form.instance.author = self.request.user

        self.object = form.save()

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, f'formset_{name}_valid', None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('gnome_main:blog')

    def formset_images_valid(self, formset):
        """
        Hook for custom formset saving. Useful if you have multiple formsets
        """
        images = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for image in images:
            image.post = self.object
            image.save()

class PostCreateView(NotificationCheckMixin, LoginRequiredMixin, PostInLine, CreateView):
    '''Создание поста'''
    template_name = 'gnome_main/post_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['named_formsets'] = self.get_named_formsets()
        return context

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'images': AIFormSet(prefix='images'),
            }
        else:
            return {
                'images': AIFormSet(self.request.POST or None, self.request.FILES or None, prefix='images'),
            }

class PostUpdateView(NotificationCheckMixin, LoginRequiredMixin, PostInLine, UpdateView):
    '''Представление для обновления поста'''
    template_name = 'gnome_main/post_update.html'

    def get(self, request, *args, **kwargs):
        if request.user.slug != self.kwargs['slug'].split('-')[0]:
            return HttpResponseRedirect(reverse_lazy('gnome_main:access-denied'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['named_formsets'] = self.get_named_formsets()
        return context

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, slug=self.kwargs['slug'])

    def get_named_formsets(self):
        return {
            'images': AIFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='images'),
        }

class PostDeleteView(NotificationCheckMixin, LoginRequiredMixin, DeleteView):
    '''Представление удаления записи'''
    model = Post
    template_name = 'gnome_main/post_delete.html'
    success_url = reverse_lazy('gnome_main:blog')

    def get(self, request, *args, **kwargs):
        if request.user.slug != self.kwargs['slug'].split('-')[0]:
            return HttpResponseRedirect(reverse_lazy('gnome_main:access-denied'))
        return super().get(request, *args, **kwargs)

class NotificationView(NotificationCheckMixin, CsrfMixin, LoginRequiredMixin, ListView):
    '''Представление уведомлений'''
    template_name = 'gnome_main/notifications.html'
    context_object_name = 'notification'

    def get_queryset(self):
        notif = Notification.objects.filter(user=self.request.user)
        # Обновление текущих нотификаций
        notif.update(is_read=True)
        return notif[:20]

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['notif_index'] = False
        return context

    def post(self, request, *args, **kwargs):
        d = dict(request.POST)
        context = {}
        if 'more-notif' in d:
            ids = d['ids[]']
            if ids == '' or ids[0] == 'false':
                ids = []
            new_notif = Notification.objects.filter(user=self.request.user) \
                        .exclude(id__in=ids)
            filter = d['filter'][0]
            if filter != '' and filter != 'all':
                if filter == 'reports':
                    new_notif = new_notif.filter(title='r')
                elif filter == 'comments':
                    new_notif = new_notif.filter(title='c')
                elif filter == 'subs':
                    new_notif = new_notif.filter(title='s')
            new_notif = new_notif[:10]
            context['new_notif'] = []
            for i in new_notif:
                context['new_notif'].append(
                    {'id': i.id,
                    'title': i.get_title_display(),
                     'message': safe(i.message),
                     'is_read': i.is_read,
                     'created_at': date_ago(i.created_at)}
                )
        return JsonResponse(data=context, status=200)

############################################################################
# Студия аналитики пользователя
class UserStudio(LoginRequiredMixin, NotificationCheckMixin, TemplateView):
    template_name = 'gnome_main/studio.html'

    def get(self, request, *args, **kwargs):
        if request.user.slug != self.kwargs['slug']:
            return HttpResponseRedirect(reverse_lazy('gnome_main:access-denied'))
        context = self.get_context_data(*args, **kwargs)
        return render(request, 'gnome_main/studio.html', context=context)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # данные аналитики
        cur_user = AdvUser.objects.get(slug=self.kwargs['slug'])
        posts = Post.objects.filter(author=cur_user)
        end_date_week = timezone.now()
        start_date_week = end_date_week - timezone.timedelta(days=7)
        end_date_2week = start_date_week
        start_date_2week = end_date_2week - timezone.timedelta(days=14)
        # нахожу все просмотры
        views = PostViewCount.objects.filter(post__in=posts).count()
        views_last_week = PostViewCount.objects.filter(post__in=posts,
                        viewed_on__range=(start_date_week, end_date_week)).count()
        views_last_2week = PostViewCount.objects.filter(post__in=posts,
                        viewed_on__range=(start_date_2week, end_date_2week)).count()
        if views_last_week > 0 and views_last_2week > 0:
            views_diff = views_last_week * 100 / views_last_2week - 100
            if views_diff < 0:
                views_diff = abs(views_diff)
                views_arrow = '/static/gnome_main/css/images/arrow_down.png'
                up = False
            else:
                views_arrow = '/static/gnome_main/css/images/arrow_up.png'
                up = True
        else:
            views_diff = 0
            views_arrow = '/static/gnome_main/css/images/arrow_up.png'
            up = True
        # нахожу все лайки и дизлайки
        likes = PostLike.objects.filter(post__in=posts).count()
        dislikes = PostDisLike.objects.filter(post__in=posts).count()
        # нахожу все комментарии
        comments = PostComment.objects.filter(post__in=posts).count()
        # нахожу все жалобы
        reports = PostReport.objects.filter(post__in=posts).count() + \
            CommentReport.objects.filter(comment__user=cur_user).count()
        # добавляю аналитику в контекст
        context['data'] = (
            {
                'title': 'Просмотры',
                'all': views,
                'all_title': 'просмотров',
                'last_week': views_last_week,
                'diff': int(views_diff),
                'arrow_url': views_arrow,
                'up': up,
                'section': 'views',
            },
            {
                'title': 'Лайки',
                'all': likes,
                'all_title': 'лайков',
                'section': 'likes',
            },
            {
                'title': 'Дизлайки',
                'all': dislikes,
                'all_title': 'дизлайков',
                'section': 'dislikes',
            },
            {
                'title': 'Комментарии',
                'all': comments,
                'all_title': 'комментариев',
                'section': 'comments',
            },
            {
                'title': 'Жалобы',
                'all': reports,
                'all_title': 'жалоб',
                'section': 'reports',
            },
        )
        return context

class StudioDetailView(LoginRequiredMixin, NotificationCheckMixin, TemplateView):
    '''Детальный просмотр категории'''
    template_name = 'gnome_main/studio_detail.html'

    def get(self, request, *args, **kwargs):
        if request.user.slug != self.kwargs['slug']:
            return HttpResponseRedirect(reverse_lazy('gnome_main:access-denied'))
        context = self.get_context_data(*args, **kwargs)
        section = self.kwargs['section']
        ld_indicator = 'false'
        if section == 'views':
            context['g_title'] = 'Просмотры'
            cur_model = PostViewCount
            field = 'viewed_on'
        elif section == 'likes':
            context['g_title'] = 'Лайки'
            cur_model = PostLike
            field = 'created_at'
            ld_indicator = 'true'
        elif section == 'dislikes':
            context['g_title'] = 'Дизлайки'
            cur_model = PostDisLike
            field = 'created_at'
            ld_indicator = 'true'
        elif section == 'reports':
            context['g_title'] = 'Жалобы'
            field = 'created_at'
        elif section == 'comments':
            context['g_title'] = 'Комментарии'
            cur_model = PostComment
            field = 'created_at'
        context['ld_indicator'] = ld_indicator
        if section == 'reports':
            # извлекаю жалобы на комменты и посты пользователя
            views = PostReport.objects.filter(post__author__slug=self.kwargs['slug']) \
                .annotate(report_date=TruncDate(field)) \
                .values('report_date')\
                .annotate(rep_count=Count('id')) \
                .order_by('report_date')
            views1 = CommentReport.objects.filter(comment__user__slug=self.kwargs['slug']) \
                .annotate(report_date=TruncDate(field)) \
                .values('report_date') \
                .annotate(rep_count=Count('id')) \
                .order_by('report_date')
            # собираю все жалобы в data
            data = []
            combined_reports = list(views) + list(views1)
            for view in combined_reports:
                date = mktime(view['report_date'].timetuple()) * 1000
                views = view['rep_count']
                data.append([date, views])
            # убираю повторяющиеся и обновляю количество для них же
            new_data = []
            for d in data:
                count = data.count(d)
                new_data.append([d[0], count])
                for i in range(count):
                    data.remove(d)
            data = new_data
        elif ld_indicator == 'false' and section != 'reports':
            views = cur_model.objects.filter(post__author__slug=self.kwargs['slug']) \
                .annotate(viewing_date=TruncDate(field)) \
                .values('viewing_date').annotate(view_count=Count('id')) \
                .order_by('viewing_date')
            data = []

            for view in views:
                date = mktime(view['viewing_date'].timetuple()) * 1000
                views = view['view_count']
                data.append([date, views])
        elif ld_indicator == 'true' and section != 'reports':
            views = cur_model.objects.filter(post__author__slug=self.kwargs['slug']) \
                .values('post__title') \
                .annotate(ld_count=Count('post')) \
                .order_by('post')
            all_views_count = cur_model.objects.filter(post__author__slug=self.kwargs['slug']).count()

            data = []
            for view in views:
                data.append({'name': view['post__title'], 'y': view['ld_count']*100/all_views_count,
                            'count': view['ld_count']})

        context['data'] = data
        return render(request, 'gnome_main/studio_detail.html', context=context)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['section'] = self.kwargs['section']
        return context

############################################################################
# Запрет доступа
class AccessDenied(NotificationCheckMixin, TemplateView):
    template_name = 'gnome_main/access_denied.html'

############################################################################
# Записи пользователя
class AuthorPostsBase(BlogBase):
    '''Базовый класс для записей пользователя'''
    template_name = 'gnome_main/author_posts.html'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(author__slug=self.kwargs['slug'])
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['author_slug'] = self.kwargs['slug']
        return context

class AuthorPostsView(NotificationCheckMixin, CsrfMixin, LoginRequiredMixin, BlogMixin, AuthorPostsBase, ListView):
    '''Представление окна записей пользователя'''

class AuthorPostsFilteredView(NotificationCheckMixin, CsrfMixin, LoginRequiredMixin, BlogFilterMixin, AuthorPostsBase, ListView):
    '''Представление окна записей пользователя фильтр'''

class AuthorPostsSearchView(NotificationCheckMixin, CsrfMixin, LoginRequiredMixin, BlogSearchMixin, AuthorPostsBase, ListView):
    '''Представление окна записей пользователя поиск'''

############################################################################
# Понравившиеся записи и избранное пользователя

class FavLikeStarting(NotificationCheckMixin, LoginRequiredMixin, TemplateView):
    '''Страница выбора того, что хочет посмотреть пользователь "Избранное" или "Понравившиеся записи"'''
    template_name = 'gnome_main/fav_like_start.html'

class UserFavLikeBase:
    '''Базовый класс для понравившихся записей и избранного'''
    model = Post
    context_object_name = 'posts'
    paginate_by = 30

class UserLiked(NotificationCheckMixin, CsrfMixin, LoginRequiredMixin, PostInfoAddMixin, UserFavLikeBase, ListView):
    '''Понравившиеся записи пользователя'''
    template_name = 'gnome_main/liked.html'

    def get_queryset(self, *args, **kwargs):
        # нахожу все посты, на которые пользователь поставил лайк
        posts_liked = PostLike.objects.select_related('post').filter(user=self.request.user).order_by('-created_at')
        queryset = [x.post for x in posts_liked]
        return queryset

    def post(self, request, *args, **kwargs):
        # Получаю ответ
        d = dict(request.POST)
        # нахожу удаляемый пост
        post = Post.objects.get(id=d['post_id'][0])
        # удаляю лайк на пост
        self.add_info('like', 'delete', post)
        return JsonResponse(data={}, status=204)

class UserFavourites(NotificationCheckMixin, CsrfMixin, LoginRequiredMixin, PostInfoAddMixin, UserFavLikeBase, ListView):
    '''Избранные записи пользователя'''
    template_name = 'gnome_main/favourites.html'

    def get_queryset(self, *args, **kwargs):
        # нахожу все посты, которые пользователь добавил в избранное
        posts_favourite = PostFavourite.objects.select_related('post').filter(user=self.request.user).order_by('-created_at')
        queryset = [x.post for x in posts_favourite]
        return queryset

    def post(self, request, *args, **kwargs):
        # Получаю ответ
        d = dict(request.POST)
        # нахожу удаляемый пост
        post = Post.objects.get(id=d['post_id'][0])
        # удаляю пост из избранного
        self.add_info('favourite', 'delete', post)
        return JsonResponse(data={}, status=204)

class UserHistory(NotificationCheckMixin, CsrfMixin, LoginRequiredMixin, UserFavLikeBase, ListView):
    '''История пользователя'''
    template_name = 'gnome_main/history.html'

    def get_queryset(self, *args, **kwargs):
        # нахожу все посты, которые пользователь добавил в избранное
        posts_views = PostViewCount.objects.select_related('post').filter(user=self.request.user).order_by('-viewed_on')
        queryset = [x.post for x in posts_views]
        return queryset

    def post(self, request, *args, **kwargs):
        # Получаю ответ
        d = dict(request.POST)
        # нахожу удаляемый пост
        post = Post.objects.get(id=d['post_id'][0])
        # получаю ip пользователя
        ip_address = get_client_ip(self.request)
        # удаляю сведения о просмотре
        view = PostViewCount.objects.get(post=post, user=request.user, ip_address=ip_address)
        view.delete()
        return JsonResponse(data={}, status=204)