from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):
    '''Проверяет автор поста или нет'''

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class IsCommentAuthor(BasePermission):
    '''Проверяет автор комментария или нет'''

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user