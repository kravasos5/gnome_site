from django.template import loader, RequestContext
from rest_framework import serializers
from .models import PostComment, AdvUser
from .templatetags.profile_extras import date_ago

class UserSerializer(serializers.ModelSerializer):
    profile_url = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = AdvUser
        fields = ['username', 'avatar_url', 'profile_url']

    def get_profile_url(self, obj):
        profile_url = obj.get_absolute_url()
        return profile_url

    def get_avatar_url(self, obj):
        avatar_url = obj.avatar.url
        return avatar_url

# class PostCommentSerializer(serializers.ModelSerializer):
#     created_at = serializers.SerializerMethodField()
#     user = UserSerializer(source=None)
#
#     class Meta:
#         model = PostComment
#         fields = ('id', 'post', 'user', 'comment',
#                   'created_at', 'is_changed', 'super_comment')
#
#     def get_created_at(self, obj):
#         updated_created_at = date_ago(obj.created_at)
#         return updated_created_at

class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = ('id', 'post', 'user', 'comment',
                  'created_at', 'is_changed', 'super_comment')