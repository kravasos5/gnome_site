from django.utils import timezone

from django.db.models import Count, Q
from django.dispatch import Signal
from django.http import JsonResponse
from django.db.utils import DataError, IntegrityError
from django.middleware.csrf import get_token

from .templatetags.profile_extras import date_ago, key, likes_dislikes, is_full, post_views
from django.template.defaultfilters import linebreaks

from .models import PostViewCount, SuperPostComment, SubPostComment, PostComment, CommentLike, CommentDisLike, PostLike, \
    PostDisLike, PostFavourite, Post, SubRubric, AdvUser, Notification, PostTag
from .utilities import get_client_ip


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

class ViewIncrementMixin:
    '''Миксин, увеличивающий просмотры'''

    def get_object(self):
        obj = super().get_object()
        ip_address = get_client_ip(self.request)
        if hasattr(self.request, 'user') and self.request.user.id != None:
            user = self.request.user
            PostViewCount.objects.get_or_create(post=obj,
                                                ip_address=ip_address,
                                                user=user)
        else:
            # на разработке
            PostViewCount.objects.filter(post=obj,
                                         ip_address=ip_address)[0]
            # на продакшене
            # PostViewCount.objects.get_or_create(post=obj,
            #                             ip_address=ip_address)
        return obj

class CommentDispatcherMixin:
    '''
    Миксин комментариев поста
    Прогружает комментарии, создаёт новые, ставит лайки/дизлайки на комментарии
    '''

    def new_supercomment(self, context, post, new_comm):
        '''Функция нового НАДкомментария'''
        try:
            if new_comm == '':
                raise DataError
            new_comment = SuperPostComment.objects.create(post=post, user=self.request.user,
                                                          comment=new_comm)
            date = date_ago(new_comment.created_at, new_comment.is_changed)
            # формирование ответа
            context['new_comment'] = {'username': new_comment.user.username,
                                      'comment': linebreaks(new_comm),
                                      'created_at': date,
                                      'id': new_comment.id,
                                      'user_url': new_comment.user.get_absolute_url(),
                                      'avatar_url': new_comment.user.avatar.url}
        except (DataError, IntegrityError):
            return JsonResponse(
                data={'ex': 'Комментарий не должен превышать длину в 500 символов и должен содержать хотя бы 1 символ'},
                status=400)

    def new_subcomment(self, context, post, new_subcomm, super_username, super_id):
        '''Новый ПОДкомментарий'''
        try:
            if f"{new_subcomm.rstrip(' ')}" == f"{super_username}" or new_subcomm == '':
                raise DataError
            s_comment = PostComment.objects.get(id=super_id)
            # Если это ответ на другой ПОДкомментарий, то взять в качестве НАДкомментария
            # НАДкомментарий комментария, на который отвечают
            if s_comment.super_comment != None:
                super_comment = s_comment.super_comment
            else:
                super_comment = s_comment
            comment = new_subcomm
            # В ответе должен быть сформирована ссылка на человека, которому отвечают, если её оставил пользователь
            # @username, <comment> - вот в таком формате
            if '@' in new_subcomm:
                comment = ' '.join([
                                       f'<a href="/user/{super_username[1:].lower()}" class="nametag">{x}</a>' if x.startswith(
                                           '@') else x for x in new_subcomm.split(' ')])
            # формирование нового подкомментария
            new_comment = SubPostComment.objects.create(post=post, user=self.request.user, comment=comment,
                                                        super_comment=super_comment)
            date = date_ago(new_comment.created_at, new_comment.is_changed)
            # формирование ответа
            context['new_comment'] = {'username': new_comment.user.username,
                                      'comment': linebreaks(comment),
                                      'created_at': date,
                                      'id': new_comment.id,
                                      'user_url': new_comment.user.get_absolute_url(),
                                      'avatar_url': new_comment.user.avatar.url,
                                      'super_id': new_comment.super_comment.id, }

        except (DataError, IntegrityError):
            return JsonResponse(
                data={'ex': 'Комментарий не должен превышать длину в 500 символов и должен содержать хотя бы 1 символ'},
                status=400)

    def comment_like_dislike(self, is_ld, is_ad, comment_id):
        '''Функция обработчик нового лайка/дизлайка на комментарий'''
        try:
            if is_ld == 'like' and is_ad == 'append':
                # новый like
                comment = PostComment.objects.get(id=comment_id)
                m_dislike = CommentDisLike.objects.filter(comment=comment, user=self.request.user)
                # если есть dislike - удалить
                if m_dislike.exists():
                    m_dislike.delete()
                CommentLike.objects.create(comment=comment, user=self.request.user)
            elif is_ld == 'dislike' and is_ad == 'append':
                # новый dislike
                comment = PostComment.objects.get(id=comment_id)
                m_like = CommentLike.objects.filter(comment=comment, user=self.request.user)
                # если есть like - удалить
                if m_like.exists():
                    m_like.delete()
                CommentDisLike.objects.create(comment=comment, user=self.request.user)
            elif is_ld == 'like' and is_ad == 'delete':
                # удалить like
                comment = PostComment.objects.get(id=comment_id)
                like = CommentLike.objects.filter(comment=comment, user=self.request.user)
                like.delete()
            elif is_ld == 'dislike' and is_ad == 'delete':
                # удалить dislike
                comment = PostComment.objects.get(id=comment_id)
                dislike = CommentDisLike.objects.filter(comment=comment, user=self.request.user)
                dislike.delete()
        except Exception as ex:
            return JsonResponse(data={'ex': 'Неверные данные comment_like_dislike'}, status=400)

    def load_supercomments(self, context, filter, ids, post,
                           start_comment=0, end_comment=10):
        '''Подгрузка НАДкомментариев'''
        try:
            ids = ids[1:-1].replace('"', '').split(',')
            if ids[0] == '':
                ids = []
            # нахожу соответствующие фильтру комментарии
            if filter == 'popular':
                sups = SuperPostComment.objects.filter(post=post) \
                    .annotate(num_likes=Count('commentlike'), answ_count=Count('postcomment__super_comment')) \
                    .order_by('-num_likes', '-answ_count') \
                    .exclude(id__in=ids) \
                    [start_comment:end_comment]
            elif filter == 'new':
                sups = SuperPostComment.objects.filter(post=post) \
                    .order_by('-created_at') \
                    .exclude(id__in=ids) \
                    [start_comment:end_comment]
            elif filter == 'old':
                sups = SuperPostComment.objects.filter(post=post) \
                    .order_by('created_at') \
                    .exclude(id__in=ids) \
                    [start_comment:end_comment]
            elif filter == 'my':
                sups = SuperPostComment.objects.filter(post=post, user=self.request.user) \
                    .exclude(id__in=ids) \
                    [start_comment:end_comment]

            # формирую ответ
            context['sups'] = []
            if sups:
                for i in sups:
                    date = date_ago(i.created_at, i.is_changed)
                    ccount = key(SubPostComment.objects.filter(super_comment=i.id).count())
                    if is_full(i.commentlike_set, self.request.user.id):
                        like = 'likes_mini_white_full.png'
                        dislike = 'dislikes_mini_white.png'
                    elif is_full(i.commentdislike_set, self.request.user.id):
                        like = 'likes_mini_white.png'
                        dislike = 'dislikes_mini_white_full.png'
                    else:
                        like = 'likes_mini_white.png'
                        dislike = 'dislikes_mini_white.png'

                    report = i.user.id == self.request.user.id

                    context['sups'].append({
                            'username': i.user.username,
                            'comment': linebreaks(i.comment),
                            'created_at': date,
                            'id': i.id,
                            'user_url': i.user.get_absolute_url(),
                            'avatar_url': i.user.avatar.url,
                            'ans_count': ccount,
                            'likes': likes_dislikes(i.commentlike_set.count()),
                            'dislikes': likes_dislikes(i.commentdislike_set.count()),
                            'like': like,
                            'dislike': dislike,
                            'report': report,
                    })
                    if report == False and self.request.user.id != None:
                        context['sups'][-1]['report_url'] = f'/report/{i.post.slug}/comment/{i.id}/'
                    else:
                        context['sups'][-1]['report_url'] = f'/login/'
        except Exception as ex:
            return JsonResponse(data={'ex': f'Неверные данные, {ex}'}, status=400)

    def load_subcomments(self, context, super_id, start_comment, end_comment):
        '''Подгрузка ПОДкомментариев'''
        try:
            # нахожу подкомментарии
            subcomments = SubPostComment.objects.filter(super_comment=super_id).order_by('created_at')[
                          int(start_comment):int(end_comment)]
            # формирую ответ
            context['subs'] = []
            if subcomments:
                for sub in subcomments:
                    if is_full(sub.commentlike_set, self.request.user.id):
                        like = 'likes_mini_white_full.png'
                        dislike = 'dislikes_mini_white.png'
                    elif is_full(sub.commentdislike_set, self.request.user.id):
                        like = 'likes_mini_white.png'
                        dislike = 'dislikes_mini_white_full.png'
                    else:
                        like = 'likes_mini_white.png'
                        dislike = 'dislikes_mini_white.png'
                    report = sub.user.id == self.request.user.id
                    context['subs'].append({
                        'username': sub.user.username,
                        'comment': linebreaks(sub.comment),
                        'created_at': date_ago(sub.created_at, sub.is_changed),
                        'id': sub.id,
                        'user_url': sub.user.get_absolute_url(),
                        'avatar_url': sub.user.avatar.url,
                        'likes': likes_dislikes(sub.commentlike_set.count()),
                        'dislikes': likes_dislikes(sub.commentdislike_set.count()),
                        'super_id': sub.super_comment.id,
                        'like': like,
                        'dislike': dislike,
                        'report': report,
                    })

                    if report == False and self.request.user.id != None:
                        context['subs'][-1]['report_url'] = f'/report/{sub.post.slug}/comment/{sub.id}'
                    else:
                        context['subs'][-1]['report_url'] = f'/login/'
        except Exception as ex:
            return JsonResponse(data={'ex': f'Неверные данные, {ex}'}, status=400)

    def change_comment(self, context, comment_id, new_comment):
        '''Изменение существующего комментария'''
        try:
            comment = PostComment.objects.get(id=comment_id)
            comment.comment = new_comment
            comment.is_changed = True
            comment.save()
            context['new_comment'] = {
                'comment': comment.comment,
            }
            print(context)
        except (DataError, IntegrityError):
            return JsonResponse(data={'ex': 'Комментарий не должен '
                                            'превышать длину в 500 символов и должен содержать '
                                            'хотя бы 1 символ, а также не должен содержать'
                                            'запрещённые символы'}, status=400)

    def delete_comment(self, comment_id):
        '''Удаление комментария'''
        try:
            comment = PostComment.objects.get(id=comment_id)
            comment.delete()
        except Exception as ex:
            return JsonResponse(data={'ex': 'Ошибка при '
                                            f'удалении комментария {ex}'}, status=400)

class RecLoaderMixin:
    '''Миксин, добавляющий метод загрузки рекомендаций'''
    def load_rec(self, context, post, ids):
        '''Прогрузка рекомендаций'''
        try:
            ids = ids[1:-1].replace('"', '').split(',')
            if ids[0] == '':
                ids = []
            ids.append(post.id)
            context['recs'] = []
            tags = post.tag.all()
            recs = Post.objects.filter(is_active=True, tag__in=tags).distinct() \
                       .exclude(id__in=ids)[0:10]
            if len(recs) < 10:
                recs = recs.union(Post.objects.filter(is_active=True).order_by('-created_at') \
                                  .exclude(id__in=ids).distinct()[0:9 - len(recs)])

            if recs:
                for i in recs:
                    date = date_ago(i.created_at)
                    report = i.author.id == self.request.user.id

                    context['recs'].append({
                        'title': i.title,
                        'authorname': i.author.username,
                        'created_at': date,
                        'preview': i.preview.url,
                        'id': i.id,
                        'views': post_views(i.get_view_count()),
                        'user_url': i.author.get_absolute_url(),
                        'post_url': i.get_absolute_url(),
                        'report': report,
                    })

                    if report == False and self.request.user.id != None:
                        context['recs'][-1]['report_url'] = f'/report/{i.slug}/post/'
                    elif self.request.user.id == None:
                        context['recs'][-1]['report_url'] = f'/login/'
                    else:
                        context['recs'][-1]['update_url'] = f'/post/update/{i.slug}/'

        except Exception as ex:
            return JsonResponse(data={'ex': f'Неверные данные, {ex}'}, status=400)

class PostInfoAddMixin:
    '''Миксин, добавляющий методы добавления/удаления лайков, дизлайков, избранного'''
    def add_info(self, data, status, post):
        '''Добавляет/удаляет лайки, дизлайки, избранное'''
        try:
            # добавить лайк на пост
            if data == 'like' and status == 'append':
                # если есть дизлайк на этом посте от этого же пользователя,
                # то удалить его
                m_dislike = PostDisLike.objects.filter(post=post, user=self.request.user)
                if m_dislike.exists():
                    m_dislike.delete()
                PostLike.objects.create(post=post, user=self.request.user)
            # добавить дизлайк на пост
            elif data == 'dislike' and status == 'append':
                # если есть лайк на этом посте от этого же пользователя,
                # то удалить его
                m_like = PostLike.objects.filter(post=post, user=self.request.user)
                if m_like.exists():
                    m_like.delete()
                PostDisLike.objects.create(post=post, user=self.request.user)
            # удалить лайк с поста
            elif data == 'like' and status == 'delete':
                like = PostLike.objects.get(post=post, user=self.request.user)
                like.delete()
            # удалить дизлайк с поста
            elif data == 'dislike' and status == 'delete':
                dislike = PostDisLike.objects.get(post=post, user=self.request.user)
                dislike.delete()
            # добавить пост в избранное
            elif data == 'favourite' and status == 'append':
                PostFavourite.objects.create(post=post, user=self.request.user)
            # удалить пост из избранного
            elif data == 'favourite' and status == 'delete':
                fav = PostFavourite.objects.get(post=post, user=self.request.user)
                fav.delete()
        except Exception as ex:
            return JsonResponse(data={'ex': 'Неверные данные post'}, status=400)

class CsrfMixin:
    '''Миксин, добавляющий в контекст csrf_token'''
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        csrf_token = get_token(self.request)
        context['csrf_token'] = csrf_token
        return context

class IsPostSubscribeMixin:
    '''
    Миксин вычисляющий подписан ли пользователь
    на автора поста, добавляет is_subscribe в context,
    is_subscribe либо True, либо False
    '''
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['slug'] = self.kwargs['slug']
        if self.request.user.id != None:
            is_subscribe = self.get_object().author.subscriptions.filter(id=self.request.user.id).exists()
        else:
            is_subscribe = False
        context['is_subscribe'] = is_subscribe
        return context

class SubscribeMixin:
    # Миксин, добавляющий метод подписки на пользователя
    def subscribe(self, subscribe_user, subscribe):
        '''Добавляет подписку на пользователя'''
        try:
            if subscribe == 'false':
                subscribe_user.subscriptions.remove(self.request.user)
            elif subscribe == 'true':
                subscribe_user.subscriptions.add(self.request.user)
                user_subsript.send(AdvUser, instance=self.request.user, user=subscribe_user)
        except Exception as ex:
            return JsonResponse(data={'ex': 'Ошибка при '
                                            f'подписке/отписке {ex}'}, status=400)

class SubscriptionsMixin:
    '''Миксин, добавляющий список подписчиков в контекст'''
    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.id != None:
            context['subscriptions'] = AdvUser.objects.filter(subscriptions=self.request.user)
        else:
            context['subscriptions'] = None
        return context

class RubricsMixin:
    '''Миксин, добавляющий рубрики в контекст'''
    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rubrics'] = SubRubric.objects.all()
        return context

class BlogMixin(PostInfoAddMixin, SubscriptionsMixin, RubricsMixin):
    '''Миксин страницы блога'''

    def get_context_data(self, *args, object_list=None, **kwargs):
        '''Нужно добавить в контекст filter_url'''
        context = super().get_context_data(*args, **kwargs)
        context['filter_url'] = ''
        return context

    def post(self, request):
        '''
        Обработка post-запроса, используется только для того чтобы
        добавить лайк, дизлайк на пост или добавить пост в избранное
        через его "карточку", не переходя при этом на страницу детального
        просмотра
        '''
        d = dict(request.POST)
        if 'favourite' in d:
            post = Post.objects.get(id=d['post_id'][0])
            self.add_info('favourite', d['status'][0], post)
        elif 'post-new-info' in d:
            post = Post.objects.get(id=d['post_id'][0])
            self.add_info(d['data'][0], d['status'][0], post)
        return JsonResponse({}, status=200)

class BlogFilterMixin(BlogMixin):
    '''Миксин страницы блога с фильтром'''
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        # извлекаю данные фильтрации
        date_from = self.request.GET.get('date-from')
        date_to = self.request.GET.get('date-to')
        author = self.request.GET.get('author')
        rubrics = self.request.GET.getlist('rubric')
        radio = self.request.GET.get('radio-filters')
        find_text = self.request.GET.get('text-find')
        d = dict(self.request.GET)
        # применяю фильтры
        # если есть рубрики
        if len(rubrics) > 0:
            queryset = queryset.filter(is_active=True,
                                       rubric__name__in=rubrics)
        # если указан автор
        if author != '':
            queryset2 = queryset.filter(author__username__icontains=author,
                                       is_active=True)
            queryset1 = queryset.filter(author__username__contains=author,
                                        is_active=True)
            queryset = (queryset1 | queryset2).distinct()
        # фильтр записей по категориям: популярные, старые, новые,
        # больше просмотров
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
        # фильтрация по дате
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
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # добавляю в контекст данные фильтрации
        date_from = self.request.GET.get('date-from')
        date_to = self.request.GET.get('date-to')
        author = self.request.GET.get('author')
        rubrics = self.request.GET.getlist('rubric')
        radio = self.request.GET.get('radio-filters')
        # меняю url, добавляю в него данные фильтрации
        url_str = f'date-from={date_from}&date-to={date_to}&author={author}'
        if len(rubrics) > 0:
            url_str += '&' + f'&'.join([f"rubric={r}" for r in rubrics])
        if radio != None:
            url_str += f'&radio-filters={radio}'
        context['filter_url'] = url_str + '&'
        return context

class BlogSearchMixin(BlogMixin):
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        find_text = self.request.GET.get('text-find')
        d = dict(self.request.GET)
        if find_text != None:
            tags = PostTag.objects.filter(tag__icontains=find_text)
            queryset = queryset.filter(Q(tag__in=tags) |
                        Q(title__icontains=find_text) |
                        Q(content__icontains=find_text) |
                        Q(author__username__icontains=find_text)).distinct()
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        find_text = self.request.GET.get('text-find')

        url_str = f'text-find={find_text}&'
        context['filter_url'] = url_str
        return context

class NotificationCheckMixin:
    '''Миксин для добавление в контекст'''
    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.id != None:
            notification = Notification.objects.filter(user=self.request.user,
                                                       is_read=False).exists()
        else:
            notification = False
        context['notif_index'] = notification
        return context