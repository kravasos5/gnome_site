from django.http import JsonResponse
from django.db.utils import DataError, IntegrityError
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from .templatetags.profile_extras import date_ago, key, likes_dislikes
from django.template.defaultfilters import linebreaks

from .models import PostViewCount, SuperPostComment, SubPostComment, PostComment, CommentLike, CommentDisLike, PostLike, PostDisLike, PostFavourite
from .utilities import get_client_ip

class PostViewCountMixin:

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
        ccount_dict = {}
        c_dict = {}
        sups = SuperPostComment.objects.all()[0:1]
        for i in sups:
            ccount_dict[i.id] = SubPostComment.objects.filter(super_comment=i.id).count()
            c_dict[i] = SubPostComment.objects.filter(super_comment=i.id)[:10]
        context['comments_count'] = ccount_dict
        context['comments'] = c_dict
        csrf_token = get_token(self.request)
        context['comment-csrf'] = csrf_token
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
                date = date_ago(new_comment.created_at)
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
                date = date_ago(new_comment.created_at)
                context['new_comment'] = {'username': request.user.username,
                                          'comment': linebreaks(comment),
                                          'created_at': date, 'id': new_comment.id,
                                          'user_url': new_comment.user.get_absolute_url(),
                                          'avatar_url': new_comment.user.avatar.url,
                                          'super_id': new_comment.super_comment.id}

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
                    like = PostFavourite.objects.get(post=post, user=request.user)
                    like.delete()
            except Exception as ex:
                return JsonResponse(data={'ex': 'Неверные данные post'}, status=400)

        elif 'load_comments' in d:
            try:
                sups = SuperPostComment.objects.all()[int(d['start_comment'][0]):int(d['end_comment'][0])]
                context['sups'] = []
                if sups:
                    for i in sups:
                        subs = []
                        date = date_ago(i.created_at)
                        ccount = key(SubPostComment.objects.filter(super_comment=i.id).count())
                        for sub in SubPostComment.objects.filter(super_comment=i.id)[:10]:
                            subs.append({
                                'username': sub.user.username,
                                'comment': linebreaks(sub.comment),
                                'created_at': date, 'id': sub.id,
                                'user_url': sub.user.get_absolute_url(),
                                'avatar_url': sub.user.avatar.url,
                                'ans_count': ccount,
                                'likes': likes_dislikes(sub.commentlike_set.count()),
                                'dislikes': likes_dislikes(sub.commentlike_set.count()),
                                'super_id': i.id
                            })
                        context['sups'].append({
                                'username': i.user.username,
                                'comment': linebreaks(i.comment),
                                'created_at': date, 'id': i.id,
                                'user_url': i.user.get_absolute_url(),
                                'avatar_url': i.user.avatar.url,
                                'ans_count': ccount,
                                'likes': likes_dislikes(i.commentlike_set.count()),
                                'dislikes': likes_dislikes(i.commentlike_set.count()),
                                'subs': subs
                        })
                    print(context)
            except Exception as ex:
                return JsonResponse(data={'ex': f'Неверные данные, {ex}'}, status=400)

        elif 'more_comments' in d:
            try:
                subcomments = SubPostComment.objects.filter(super_comment=d['super_id[]'][0])[int(d['start_scomment'][0]):int(d['end_scomment'][0])]
                context['subs'] = []
                print(subcomments)
                if subcomments:
                    for sub in subcomments:
                        context['subs'].append({
                            'username': sub.user.username,
                            'comment': linebreaks(sub.comment),
                            'created_at': date_ago(sub.created_at), 'id': sub.id,
                            'user_url': sub.user.get_absolute_url(),
                            'avatar_url': sub.user.avatar.url,
                            'likes': likes_dislikes(sub.commentlike_set.count()),
                            'dislikes': likes_dislikes(sub.commentlike_set.count()),
                            'super_id': sub.super_comment.id
                        })
            except Exception as ex:
                return JsonResponse(data={'ex': f'Неверные данные, {ex}'}, status=400)

        return JsonResponse(data=context, status=200)