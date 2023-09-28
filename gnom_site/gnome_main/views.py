from django.utils import timezone

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.signing import BadSignature
from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordResetDoneView
from django.template.defaultfilters import truncatewords, safe
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView, DetailView, ListView
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import PostCommentSerializer

from .forms import RegisterUserForm, ChangeUserInfoForm, DeleteUserForm, PostReportForm, CommentReportForm
from .mixins import PostViewCountMixin, BlogMixin
from .models import *
from .apps import user_delete_signal
from .templatetags.profile_extras import date_ago, post_views, is_full, comment_pluralize
from .utilities import signer

# Главная страница
def main(request):
    # print(request.context)
    # context = {'cur_user': cur_user,}
    return render(request, 'gnome_main/main.html') #, context=context

# Блог
class BlogView(BlogMixin, ListView):
    '''Представление блога'''
    model = Post
    template_name = 'gnome_main/blog.html'
    context_object_name = 'posts'
    paginate_by = 2
    # .annotate(num_likes=Count('like'), num_postcomments=Count('postcomment')) \
        # .order_by('num_likes', 'num_postcomments')

class BlogFilterView(BlogMixin, ListView):
    '''Представление блога с фильтром'''
    model = Post
    template_name = 'gnome_main/blog.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        date_from = self.request.GET.get('date-from')
        date_to = self.request.GET.get('date-to')
        author = self.request.GET.get('author')
        rubrics = self.request.GET.getlist('rubric')
        radio = self.request.GET.get('radio-filters')
        find_text = self.request.GET.get('text-find')
        d = dict(self.request.GET)
        print(d)
        if find_text == None:
            if len(rubrics) > 0:
                queryset = queryset.filter(is_active=True,
                                           rubric__name__in=rubrics)
            if author != '':
                queryset2 = queryset.filter(author__username__icontains=author,
                                           is_active=True)
                queryset1 = queryset.filter(author__username__contains=author,
                                            is_active=True)
                queryset = (queryset1 | queryset2).distinct()
            if radio != None:
                if radio == 'new':
                    queryset = queryset.filter(is_active=True).order_by('-created_at')
                elif radio == 'old':
                    queryset = queryset.filter(is_active=True).order_by('created_at')
                elif radio == 'more-views':
                    queryset = queryset.filter(is_active=True) \
                        .distinct() \
                        .annotate(views_count=Count('postviewcount')) \
                        .order_by('views_count')
                elif radio == 'popular':
                    queryset = queryset.filter(is_active=True) \
                        .distinct() \
                        .annotate(num_likes=Count('postlike'),
                                  num_dislikes=Count('postdislike'),
                                  num_comments=Count('postcomment'),
                                  num_favourite=Count('postfavourite'),
                                  views_count=Count('postviewcount')) \
                        .order_by('-views_count', '-num_likes',
                                  '-num_comments', '-num_favourite',
                                  'num_dislikes')
            if date_from != '' and date_to == '':
                date_list = date_from.split('-')
                date = timezone.make_aware(timezone.datetime(int(date_list[0]), int(date_list[1]), int(date_list[2])))
                queryset = queryset.filter(created_at__gte=date,
                                            is_active=True)
            elif date_to != '' and date_from == '':
                date_list = date_to.split('-')
                date = timezone.make_aware(timezone.datetime(int(date_list[0]), int(date_list[1]), int(date_list[2])))
                queryset = queryset.filter(created_at__lte=date,
                                            is_active=True)
            elif date_from != '' and date_to != '':
                date_list_from = date_from.split('-')
                date_list_to = date_to.split('-')
                date_f = timezone.make_aware(timezone.datetime(int(date_list_from[0]), int(date_list_from[1]), int(date_list_from[2])))
                date_t = timezone.make_aware(timezone.datetime(int(date_list_to[0]), int(date_list_to[1]), int(date_list_to[2])))
                queryset = queryset.filter(created_at__gte=date_f,
                                            created_at__lte=date_t,
                                            is_active=True)
        elif find_text != None:
            tags = PostTag.objects.filter(tag__icontains=find_text)
            queryset = (queryset | Post.objects.filter(Q(tag__in=tags) |
                                        Q(title__icontains=find_text) |
                                        Q(content__icontains=find_text))).distinct()
        # print(queryset)
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['subscriptions'] = AdvUser.objects.filter(subscriptions=self.request.user)
        context['rubrics'] = SubRubric.objects.all()
        context['csrf_token'] = get_token(self.request)

        date_from = self.request.GET.get('date-from')
        date_to = self.request.GET.get('date-to')
        author = self.request.GET.get('author')
        rubrics = self.request.GET.getlist('rubric')
        radio = self.request.GET.get('radio-filters')

        url_str = f'date-from={date_from}&date-to={date_to}&author={author}'
        if len(rubrics) > 0:
            url_str += '&' + f'&'.join([f"rubric={r}" for r in rubrics])
        if radio != None:
            url_str += f'&radio-filters={radio}'
        context['filter_url'] = url_str + '&'
        return context

class BlogSearchView(BlogMixin, ListView):
    '''Представление блога с фильтром'''
    model = Post
    template_name = 'gnome_main/blog.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        find_text = self.request.GET.get('text-find')
        d = dict(self.request.GET)
        print(d)
        if find_text != None:
            tags = PostTag.objects.filter(tag__icontains=find_text)
            queryset = queryset.filter(Q(tag__in=tags) |
                        Q(title__icontains=find_text) |
                        Q(content__icontains=find_text) |
                        Q(author__username__icontains=find_text)).distinct()
        # print(queryset)
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['subscriptions'] = AdvUser.objects.filter(subscriptions=self.request.user)
        context['rubrics'] = SubRubric.objects.all()
        context['csrf_token'] = get_token(self.request)

        find_text = self.request.GET.get('text-find')

        url_str = f'text-find={find_text}&'
        context['filter_url'] = url_str
        return context


class PostView(PostViewCountMixin, DetailView):
    '''Представление детального просмотра поста'''
    model = Post
    template_name = 'gnome_main/show_post.html'
    context_object_name = 'post'

class UserProfile(View):
    '''Представление профиля пользователя'''
    template_name = 'gnome_main/user_profile.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        csrf_token = get_token(self.request)
        context['csrf_token'] = csrf_token
        return context

    def get(self, request, slug):
        cur_user = get_object_or_404(AdvUser, slug=slug)
        user = request.user
        count = cur_user.subscriptions.count()
        is_subscribe = cur_user.subscriptions.filter(id=user.id).exists()
        posts = Post.objects.filter(author=cur_user).order_by('-created_at')[:10]
        context = {'cur_user': cur_user, 'sub_count': count,
                   'is_subscribe': is_subscribe, 'posts_count': posts.count(),
                   'posts': posts}
        return render(request, 'gnome_main/user_profile.html', context=context)

    def post(self, request, slug):
        d = dict(request.POST)
        print(d)
        cur_user = get_object_or_404(AdvUser, slug=slug)
        user = request.user
        # формирования контекста
        context = {}
        if 'subscribe' in d:
            try:
                if d['subscribe'][0] == 'true':
                    cur_user.subscriptions.remove(user)
                elif d['subscribe'][0] == 'false':
                    cur_user.subscriptions.add(user)
            except:
                return JsonResponse(data={'ex': 'Неверные данные post'}, status=400)
        elif 'filter' in d:
            # try:
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
                context['posts_is_full'] = True
            # except Exception as ex:
            #     return JsonResponse(data={'ex': f'Неверные данные post {ex}'}, status=400)
        elif 'favourite' in d:
            try:
                post = Post.objects.get(id=d['p_id'][0])
                if d['status'][0] == 'append':
                    PostFavourite.objects.create(post=post, user=request.user)
                elif d['status'][0] == 'delete':
                    fav = PostFavourite.objects.get(post=post, user=request.user)
                    fav.delete()
            except Exception as ex:
                return JsonResponse(data={'ex': f'Неверные данные post: {ex}'}, status=400)
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

    # def form_valid(self, form):
    #     super().form_valid(form)
    #     response_data = {
    #         'success': True,
    #         'success_url': self.get_success_url()
    #     }
    #     return JsonResponse(response_data)

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

class PostReportView(LoginRequiredMixin, CreateView):
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

class CommentReportView(LoginRequiredMixin, CreateView):
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

# REST
class PostCommentAPI(APIView):
    '''ViewSet, который будет возвращать 10 новых комментариев'''
    # queryset = PostComment.objects.all()
    # serializer = PostCommentSerializer()

    def get(self, request):
        queryset = PostComment.objects.all()
        return Response({'get': PostCommentSerializer(queryset, many=True).data})