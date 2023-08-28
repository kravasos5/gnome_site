from django.http import JsonResponse
from django.db.utils import DataError, IntegrityError
from django.middleware.csrf import get_token

from .templatetags.profile_extras import date_ago
from django.template.defaultfilters import linebreaks

from .models import PostViewCount, SuperPostComment, SubPostComment, PostComment
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

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        d = dict(request.POST)
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

        return JsonResponse(data=context, status=200)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        csrf_token = get_token(self.request)
        context['comment-csrf'] = csrf_token
        return context