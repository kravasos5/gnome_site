from django.db.models import Count
from django.dispatch import Signal
from django.http import JsonResponse
from django.db.utils import DataError, IntegrityError
from django.middleware.csrf import get_token

from .templatetags.profile_extras import date_ago, key, likes_dislikes, is_full, post_views
from django.template.defaultfilters import linebreaks

from .models import PostViewCount, SuperPostComment, SubPostComment, PostComment, CommentLike, CommentDisLike, PostLike, \
    PostDisLike, PostFavourite, Post, SubRubric, AdvUser, Notification
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


class PostMixin:

    '''Миксин, увеличивающий просмотры'''
    def get_object(self):
        obj = super().get_object()
        ip_address = get_client_ip(self.request)
        if hasattr(self.request, 'user'):
            user = self.request.user
            PostViewCount.objects.get_or_create(post=obj,
                                        ip_address=ip_address,
                                        user=user)
        else:
            PostViewCount.objects.get_or_create(post=obj,
                                        ip_address=ip_address)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        csrf_token = get_token(self.request)
        context['comment-csrf'] = csrf_token
        context['slug'] = self.kwargs['slug']
        is_subscribe = self.get_object().author.subscriptions.filter(id=self.request.user.id).exists()
        context['is_subscribe'] = is_subscribe
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        d = dict(request.POST)
        print(d)
        # формирования контекста
        context = {}
        # если пользователь оставил SuperComment
        if 'main-comment-line' in d:
            try:
                if d['main-comment-line'][0] == '':
                    raise DataError
                new_comment = SuperPostComment.objects.create(post=post, user=request.user, comment=d["main-comment-line"][0])
                date = date_ago(new_comment.created_at, new_comment.is_changed)
                context['new_comment'] = {'username': request.user.username, 'comment': linebreaks(d["main-comment-line"][0]),
                                          'created_at': date, 'id': new_comment.id,
                                          'user_url': new_comment.user.get_absolute_url(),
                                          'avatar_url': new_comment.user.avatar.url}
            except (DataError, IntegrityError):
                return JsonResponse(data={'ex': 'Комментарий не должен превышать длину в 500 символов и должен содержать хотя бы 1 символ'}, status=400)
        elif 's-comment-line' in d:
            try:
                if f"{d['s-comment-line'][0].rstrip(' ')}" == f"{d['s-username'][0]}" or d['s-comment-line'][0] == '':
                    raise DataError
                s_comment = PostComment.objects.get(id=d['super-id'][0])
                if s_comment.super_comment != None:
                    super_comment = s_comment.super_comment
                else:
                    super_comment = s_comment
                comment = d['s-comment-line'][0]
                if '@' in d['s-comment-line'][0]:
                    comment = ' '.join([f'<a href="/user/{d["s-username"][0][1:].lower()}" class="nametag">{x}</a>' if x.startswith('@') else x for x in d['s-comment-line'][0].split(' ')])
                new_comment = SubPostComment.objects.create(post=post, user=request.user, comment=comment, super_comment=super_comment)
                date = date_ago(new_comment.created_at, new_comment.is_changed)
                context['new_comment'] = {'username': request.user.username,
                            'comment': linebreaks(comment),
                            'created_at': date, 'id': new_comment.id,
                            'user_url': new_comment.user.get_absolute_url(),
                            'avatar_url': new_comment.user.avatar.url,
                            'super_id': new_comment.super_comment.id,}

            except (DataError, IntegrityError):
                return JsonResponse(data={'ex': 'Комментарий не должен превышать длину в 500 символов и должен содержать хотя бы 1 символ'}, status=400)

        elif 'id' in d:
            try:
                if d['data'][0] == 'like' and d['c_status'][0] == 'append':
                    comment = PostComment.objects.get(id=d['id'][0])
                    m_dislike = CommentDisLike.objects.filter(comment=comment, user=request.user)
                    if m_dislike.exists():
                        m_dislike.delete()
                    CommentLike.objects.create(comment=comment, user=request.user)
                elif d['data'][0] == 'dislike' and d['c_status'][0] == 'append':
                    comment = PostComment.objects.get(id=d['id'][0])
                    m_like = CommentLike.objects.filter(comment=comment, user=request.user)
                    if m_like.exists():
                        m_like.delete()
                    CommentDisLike.objects.create(comment=comment, user=request.user)
                elif d['data'][0] == 'like' and d['c_status'][0] == 'delete':
                    comment = PostComment.objects.get(id=d['id'][0])
                    like = CommentLike.objects.get(comment=comment, user=request.user)
                    like.delete()
                elif d['data'][0] == 'dislike' and d['c_status'][0] == 'delete':
                    comment = PostComment.objects.get(id=d['id'][0])
                    dislike = CommentDisLike.objects.get(comment=comment, user=request.user)
                    dislike.delete()
            except Exception as ex:
                return JsonResponse(data={'ex': 'Неверные данные'}, status=400)
        elif 'main' in d:
            try:
                if d['data'][0] == 'post_like' and d['status'][0] == 'append':
                    m_dislike = PostDisLike.objects.filter(post=post, user=request.user)
                    if m_dislike.exists():
                        m_dislike.delete()
                    PostLike.objects.create(post=post, user=request.user)
                elif d['data'][0] == 'post_dislike' and d['status'][0] == 'append':
                    m_like = PostLike.objects.filter(post=post, user=request.user)
                    if m_like.exists():
                        m_like.delete()
                    PostDisLike.objects.create(post=post, user=request.user)
                elif d['data'][0] == 'favourite' and d['status'][0] == 'append':
                    PostFavourite.objects.create(post=post, user=request.user)
                elif d['data'][0] == 'post_like' and d['status'][0] == 'delete':
                    like = PostLike.objects.get(post=post, user=request.user)
                    like.delete()
                elif d['data'][0] == 'post_dislike' and d['status'][0] == 'delete':
                    dislike = PostDisLike.objects.get(post=post, user=request.user)
                    dislike.delete()
                elif d['data'][0] == 'favourite' and d['status'][0] == 'delete':
                    fav = PostFavourite.objects.get(post=post, user=request.user)
                    fav.delete()
            except Exception as ex:
                return JsonResponse(data={'ex': 'Неверные данные post'}, status=400)

        elif 'load_comments' in d:
            try:
                # print(d['filter'][0], d['start_comment'][0], d['end_comment'][0])
                if d['filter'][0] == 'popular':
                    sups = SuperPostComment.objects.filter(post=post)\
                        .annotate(num_likes=Count('commentlike'), answ_count=Count('postcomment__super_comment'))\
                        .order_by('-num_likes', '-answ_count')\
                        [int(d['start_comment'][0]):int(d['end_comment'][0])]
                elif d['filter'][0] == 'new':
                    sups = SuperPostComment.objects.filter(post=post) \
                               .order_by('-created_at') \
                        [int(d['start_comment'][0]):int(d['end_comment'][0])]
                elif d['filter'][0] == 'old':
                    sups = SuperPostComment.objects.filter(post=post) \
                               .order_by('created_at') \
                        [int(d['start_comment'][0]):int(d['end_comment'][0])]
                elif d['filter'][0] == 'my':
                    sups = SuperPostComment.objects.filter(post=post, user=request.user) \
                        [int(d['start_comment'][0]):int(d['end_comment'][0])]

                context['sups'] = []
                if sups:
                    for i in sups:
                        date = date_ago(i.created_at, i.is_changed)
                        ccount = key(SubPostComment.objects.filter(super_comment=i.id).count())
                        if is_full(i.commentlike_set, request.user.id):
                            like = 'likes_mini_white_full.png'
                            dislike = 'dislikes_mini_white.png'
                        elif is_full(i.commentdislike_set, request.user.id):
                            like = 'likes_mini_white.png'
                            dislike = 'dislikes_mini_white_full.png'
                        else:
                            like = 'likes_mini_white.png'
                            dislike = 'dislikes_mini_white.png'

                        report = i.user.id == request.user.id

                        context['sups'].append({
                                'username': i.user.username,
                                'comment': linebreaks(i.comment),
                                'created_at': date, 'id': i.id,
                                'user_url': i.user.get_absolute_url(),
                                'avatar_url': i.user.avatar.url,
                                'ans_count': ccount,
                                'likes': likes_dislikes(i.commentlike_set.count()),
                                'dislikes': likes_dislikes(i.commentdislike_set.count()),
                                'like': like,
                                'dislike': dislike,
                                'report': report,
                        })
                        if report == False:
                            context['sups'][-1]['report_url'] = f'/report/{i.post.slug}/comment/{i.id}'
            except Exception as ex:
                return JsonResponse(data={'ex': f'Неверные данные, {ex}'}, status=400)

        elif 'load_rec' in d:
            try:
                ids = d['ids'][0][1:-1].replace('"', '').split(',')
                if ids[0] == '':
                    ids = []
                ids.append(post.id)
                context['recs'] = []
                tags = post.tag.all()
                recs = Post.objects.filter(is_active=True, tag__in=tags).distinct() \
                           .exclude(id__in=ids)[0:10]
                if len(recs) < 10:
                    recs = recs.union(Post.objects.filter(is_active=True).order_by('-created_at') \
                               .distinct().exclude(id__in=ids)[0:9-len(recs)])

                if recs:
                    for i in recs:
                        date = date_ago(i.created_at)
                        report = i.author.id == request.user.id

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

                        if report == False:
                            context['recs'][-1]['report_url'] = f'/report/{i.slug}/post/'
                        else:
                            context['recs'][-1]['update_url'] = f'/post/update/{i.slug}/'

            except Exception as ex:
                return JsonResponse(data={'ex': f'Неверные данные, {ex}'}, status=400)

        elif 'more_comments' in d:
            try:
                subcomments = SubPostComment.objects.filter(super_comment=d['super_id'][0]).order_by('created_at')[int(d['start_scomment'][0]):int(d['end_scomment'][0])]
                context['subs'] = []
                if subcomments:
                    for sub in subcomments:
                        if is_full(sub.commentlike_set, request.user.id):
                            like = 'likes_mini_white_full.png'
                            dislike = 'dislikes_mini_white.png'
                        elif is_full(sub.commentdislike_set, request.user.id):
                            like = 'likes_mini_white.png'
                            dislike = 'dislikes_mini_white_full.png'
                        else:
                            like = 'likes_mini_white.png'
                            dislike = 'dislikes_mini_white.png'
                        report = sub.user.id == request.user.id
                        context['subs'].append({
                            'username': sub.user.username,
                            'comment': linebreaks(sub.comment),
                            'created_at': date_ago(sub.created_at, sub.is_changed), 'id': sub.id,
                            'user_url': sub.user.get_absolute_url(),
                            'avatar_url': sub.user.avatar.url,
                            'likes': likes_dislikes(sub.commentlike_set.count()),
                            'dislikes': likes_dislikes(sub.commentdislike_set.count()),
                            'super_id': sub.super_comment.id,
                            'like': like,
                            'dislike': dislike,
                            'report': report,
                        })

                        if report == False:
                            context['subs'][-1]['report_url'] = f'/report/{sub.post.slug}/comment/{sub.id}'
            except Exception as ex:
                return JsonResponse(data={'ex': f'Неверные данные, {ex}'}, status=400)

        elif 'change_comment' in d:
            try:
                comment = PostComment.objects.get(id=d['с_id'][0])
                comment.comment = d['change-comment-line'][0]
                comment.is_changed = True
                comment.save()
                context['new_comment'] = {
                    'comment': comment.comment,
                }
                print(context)
            except (DataError, IntegrityError):
                return JsonResponse(data={'ex': 'Комментарий не должен '
                    'превышать длину в 500 символов и должен содержать '
                    'хотя бы 1 символ, а также не должен содержать          '
                    'запрещённые символы'}, status=400)

        elif 'delete_comment' in d:
            try:
                comment = PostComment.objects.get(id=d['c_id'][0])
                comment.delete()
            except Exception as ex:
                return JsonResponse(data={'ex': 'Ошибка при '
                        f'удалении комментария {ex}'}, status=400)

        elif 'subscribe' in d:
            try:
                author = post.author
                if d['subscribe'][0] == 'false':
                    author.subscriptions.remove(request.user)
                elif d['subscribe'][0] == 'true':
                    author.subscriptions.add(request.user)
                    user_subsript.send(AdvUser, instance=request.user, user=author)
            except Exception as ex:
                return JsonResponse(data={'ex': 'Ошибка при '
                        f'подписке/отписке {ex}'}, status=400)

        return JsonResponse(data=context, status=200)

class BlogMixin:
    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['subscriptions'] = AdvUser.objects.filter(subscriptions=self.request.user)
        context['rubrics'] = SubRubric.objects.all()
        context['csrf_token'] = get_token(self.request)
        context['filter_url'] = ''
        return context

    def post(self, request):
        d = dict(request.POST)
        if 'favourite' in d:
            post = Post.objects.get(id=d['p_id'][0])
            if d['status'][0] == 'append':
                PostFavourite.objects.create(post=post, user=request.user)
            elif d['status'][0] == 'delete':
                fav = PostFavourite.objects.get(post=post, user=request.user)
                fav.delete()
        return JsonResponse({}, status=200)

class NotificationCheckMixin:
    '''Миксин для добавление в контекст'''
    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        notification = Notification.objects.filter(user=self.request.user,
                                                   is_read=False).exists()
        context['notif_index'] = notification
        return context