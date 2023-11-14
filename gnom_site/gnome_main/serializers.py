from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .apps import user_registered
from .models import PostComment, AdvUser, Rubric, Post, PostAdditionalImage, PostTag, SubRubric, PostViewCount, \
    PostLike, PostDisLike, PostFavourite, CommentLike, CommentDisLike, PostReport, CommentReport, Notification

##########################################################################
# Account Serializers
from .templatetags.profile_extras import date_ago


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор пользователя'''
    account_url = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = AdvUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'status', 'description', 'slug', 'avatar_url',
                  'profile_image_url', 'account_url')

    def get_account_url(self, obj):
        '''Получение ссылки на профиль пользователя'''
        account_url = obj.get_absolute_url()
        return account_url

    def get_avatar_url(self, obj):
        '''Получение аватара пользователя'''
        avatar_url = obj.avatar.url
        return avatar_url

    def get_profile_image_url(self, obj):
        '''Получение шапки профиля пользователя'''
        profile_image_url = obj.profile_image.url
        return profile_image_url

class UserCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор создания пользователя'''
    # поле пароля
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        '''Метод, отрабатывающий при создании пользователя'''
        user = AdvUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.is_active = False
        user.is_activated = False
        user.save()
        # отправка письма с просьбой активировать аккаунт
        user_registered.send(UserCreateSerializer, instance=user)
        return user

class LogoutSerializer(serializers.Serializer):
    '''Сериализатор выхода'''
    refresh = serializers.CharField()

    def validate(self, attrs):
        '''Валидация'''
        # присваиваю токен
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            # добавляю токен в чёрный список
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('Bad token')

##########################################################################
# Rubric Serializers

class RubricSerializer(serializers.ModelSerializer):
    '''Сериализатор рубрики'''
    class Meta:
        model = Rubric
        fields = ('id', 'name', 'super_rubric')

##########################################################################
# Post Serializers

class PostAdditionalImageSerializer(serializers.ModelSerializer):
    '''Сериализатор дополнительного медиа'''
    class Meta:
        model = PostAdditionalImage
        fields = ('media',)

class PostTagSerializer(serializers.ModelSerializer):
    '''Сериализатор тэга поста'''
    class Meta:
        model = PostTag
        fields = ('tag',)

class PostSerializer(serializers.ModelSerializer):
    '''Сериализатор записей'''
    author = UserSerializer(source=None)
    rubric = RubricSerializer(source=None)
    preview = serializers.SerializerMethodField()
    additional_media = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'content', 'rubric', 'preview',
                  'author', 'is_active', 'tags', 'created_at', 'additional_media')

    def get_preview(self, obj):
        '''Получаю превью записи'''
        return obj.preview.url

    def get_tags(self, obj):
        '''Получаю все тэги'''
        return [i.tag for i in obj.get_posttags()]

    def get_additional_media(self, obj):
        '''Получаю дополнительные медиа'''
        return [i['media'] for i in PostAdditionalImage.objects.filter(post=obj).values()]

class PostUpdateSerializer(serializers.ModelSerializer):
    '''Сериализатор для изменения записи'''
    preview = serializers.FileField(required=False)
    additional_media = serializers.ListField(child=serializers.FileField(), required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Post
        fields = ('title', 'content', 'rubric', 'preview', 'is_active',
                  'tags', 'additional_media')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        super().__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        # получаю дополнительные медиа-файлы
        additional_media_data = validated_data.pop('additional_media', [])
        # получаю тэги
        tags = validated_data.get('tags')
        # сохранение тэгов
        if tags:
            for tag_name in tags:
                tag, created = PostTag.objects.get_or_create(tag=tag_name)
                instance.tag.add(tag)
        # Обновление полей записи
        instance = super().update(instance, validated_data)
        # Сохранение дополнительных медиафайлов
        for media_data in additional_media_data:
            PostAdditionalImage.objects.create(post=instance, media=media_data)
        return instance

    def create(self, validated_data):
        # получаю тэги
        tags = validated_data.pop('tags')
        # получаю дополнительные медиа-файлы
        additional_media_data = validated_data.pop('additional_media', [])
        instance = Post(**validated_data)
        # чтобы дальше сохранить тэги и медиа посту нужен id, поэтому
        # сохраняю его сейчас
        instance.save()
        # сохранение тэгов
        for tag_name in tags:
            tag, created = PostTag.objects.get_or_create(tag=tag_name)
            instance.tag.add(tag)
        # Сохранение дополнительных медиафайлов
        for media_data in additional_media_data:
            PostAdditionalImage.objects.create(post=instance, media=media_data)
        return instance

##########################################################################
# PostViewCount Serializers

class PostViewCountSerializer(serializers.ModelSerializer):
    '''Сериализатор представления просмотра записи'''
    class Meta:
        model = PostViewCount
        fields = ('post', 'ip_address', 'user')

##########################################################################
# PostLike Serializers

class PostLikeSerializer(serializers.ModelSerializer):
    '''Сериализатор лайка на пост'''
    class Meta:
        model = PostLike
        fields = ('post', 'user')

##########################################################################
# PostDisLike Serializers

class PostDisLikeSerializer(serializers.ModelSerializer):
    '''Сериализатор дизлайка на пост'''
    class Meta:
        model = PostDisLike
        fields = ('post', 'user')

##########################################################################
# PostFavourite Serializers

class PostFavouriteSerializer(serializers.ModelSerializer):
    '''Сериализатор избранного поста'''
    class Meta:
        model = PostFavourite
        fields = ('post', 'user')

##########################################################################
# PostComment Serializers

class PostCommentSerializer(serializers.ModelSerializer):
    '''Сериализатор комментария'''
    user = UserSerializer(source=None)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ('id', 'post', 'user', 'comment', 'created_at', 'is_changed')
        read_only_fields = ('created_at',)

    def get_created_at(self, obj):
        updated_created_at = date_ago(obj.created_at)
        return updated_created_at

class PostCommentCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор создания комментария'''

    class Meta:
        model = PostComment
        fields = ('post', 'user', 'comment', 'is_changed', 'super_comment')

class PostCommentUpdateSerializer(serializers.ModelSerializer):
    '''Сериализатор изменения комментария'''

    class Meta:
        model = PostComment
        fields = ('comment', 'is_changed')

##########################################################################
# PostCommentLike Serializers

class CommentLikeSerializer(serializers.ModelSerializer):
    '''Сериализатор лайка на коммент'''

    class Meta:
        model = CommentLike
        fields = ('comment', 'user')


##########################################################################
# PostCommentDisLike Serializers

class CommentDisLikeSerializer(serializers.ModelSerializer):
    '''Сериализатор лайка на коммент'''

    class Meta:
        model = CommentDisLike
        fields = ('comment', 'user')

##########################################################################
# PostReport Serializers

class PostReportSerializer(serializers.ModelSerializer):
    '''Сериадизатор жалобы на пост'''

    class Meta:
        model = PostReport
        fields = ('id', 'post', 'user', 'type', 'text')

class PostReportCreateSerializer(serializers.ModelSerializer):
    '''Сериадизатор создания жалобы на пост'''

    class Meta:
        model = PostReport
        fields = ('post', 'user', 'type', 'text')

##########################################################################
# CommentReport Serializers

class CommentReportSerializer(serializers.ModelSerializer):
    '''Сериадизатор жалобы на пост'''

    class Meta:
        model = CommentReport
        fields = ('id', 'comment', 'user', 'type', 'text')

class CommentReportCreateSerializer(serializers.ModelSerializer):
    '''Сериадизатор жалобы на пост'''

    class Meta:
        model = CommentReport
        fields = ('comment', 'user', 'type', 'text')

##########################################################################
# Notification Serializers

class NotificationSerializer(serializers.ModelSerializer):
    '''Сериадизатор уведомления'''

    class Meta:
        model = Notification
        fields = ('id', 'user', 'title', 'message', 'is_read', 'created_at')

##########################################################################
# AdminUser serializers

class AdminUserSerializer(UserSerializer):
    '''Админ сериализатор пользователя'''

    class Meta:
        model = AdvUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'status', 'description', 'slug', 'avatar_url',
                  'profile_image_url', 'account_url', 'is_activated',
                  'send_messages')

class AdminUserChangeSerializer(UserSerializer):
    '''Админ сериализатор изменения пользователя'''

    class Meta:
        model = AdvUser
        fields = ('username', 'first_name', 'last_name', 'email',
                  'status', 'description', 'slug', 'is_activated',
                  'send_messages')

class AdminUserCreateSerializer(UserCreateSerializer):
    '''Админ сериализатор создания пользователя'''
    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password', 'is_activated', 'is_active')

    def create(self, validated_data):
        '''Метод, отрабатывающий при создании пользователя'''
        user = AdvUser(
            username=validated_data['username'],
            email=validated_data['email'],
            is_activated=validated_data['is_activated'],
            is_active=validated_data['is_active'],
        )
        user.set_password(validated_data['password'])
        user.save()
        # отправка письма с просьбой активировать аккаунт
        # но только если пользователь не активирован
        if not user.is_activated:
            user_registered.send(UserCreateSerializer, instance=user)
        return user

##########################################################################
# AdminRubric serializers

class AdminRubricCreateChangeSerializer(serializers.ModelSerializer):
    '''Админ сериализатор изменения/создания рубрики'''
    class Meta:
        model = Rubric
        fields = ('name', 'order', 'super_rubric')

class AdminRubricSerializer(serializers.ModelSerializer):
    '''Админ сериализатор рубрики'''
    class Meta:
        model = Rubric
        fields = ('id', 'name', 'order', 'super_rubric')

##########################################################################
# AdminPost serializers

class AdminPostUpdateSerializer(PostUpdateSerializer):
    '''Админ сериализатор обновления постов'''

    class Meta:
        model = Post
        fields = ('title', 'content', 'rubric', 'preview', 'is_active',
                  'tags', 'additional_media', 'author')

##########################################################################
# AdminNotification Serializers

class AdminNotificationSerializer(serializers.ModelSerializer):
    '''Админ сериадизатор уведомления GET'''

    class Meta:
        model = Notification
        fields = ('id', 'user', 'title', 'message', 'is_read', 'created_at')

class AdminNotificationUpdateSerializer(serializers.ModelSerializer):
    '''Админ сериадизатор уведомления PUT, PATCH, DELETE'''

    class Meta:
        model = Notification
        fields = ('user', 'title', 'message', 'is_read')