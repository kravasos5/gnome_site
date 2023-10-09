from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.text import slugify
from .utilities import get_image_path_post, get_image_path_post_ai, random_key

class AdvUser(AbstractUser):
    def get_profile_image_path(instance, filename):
        username = instance.username
        return f'photos/{username}/{filename}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.username}')#-{"".join(random.choices(string.ascii_lowercase, k=10))}')[:200]
        super().save(*args, **kwargs)

    is_activated = models.BooleanField(default=True, db_index=True,
                                       verbose_name='Прошёл активацию?')
    send_messages = models.BooleanField(default=True,
                        verbose_name='Слать оповещения о комментариях?')
    avatar = models.ImageField(verbose_name='Аватар',
                              upload_to=get_profile_image_path,
                              null=True, db_index=True)
    profile_image = models.ImageField(verbose_name='Шапка профиля',
                              upload_to=get_profile_image_path,
                              null=True, db_index=True)
    status = models.CharField(max_length=50, null=True, blank=True,
                              db_index=True, verbose_name='Статус профиля')
    description = models.CharField(max_length=500, null=True, blank=True,
                              db_index=True, verbose_name='Описание профиля')
    subscriptions = models.ManyToManyField('self', blank=True, symmetrical=False, verbose_name='Подписчики')
    slug = models.SlugField(max_length=200, unique=True, db_index=True,
                            verbose_name='Слаг')

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'<{self.username}>'

    def get_absolute_url(self):
        return reverse('gnome_main:user-profile', kwargs={'slug': self.slug})

    def delete(self, *args, **kwargs):
        for post in self.post_set.all():
            post.delete()
        super().delete(*args, **kwargs)


class Rubric(models.Model):
    '''Модель рубрик'''
    name = models.CharField(max_length=30, db_index=True, unique=True,
                            verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True,
                                     verbose_name='Порядок')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT,
                                     null=True, blank=True,
                                     verbose_name='Надрубрика')

class SuperRubricManager(models.Manager):
    '''Менеджер надрубрик'''
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)

class SuperRubric(Rubric):
    '''Модель надрубрики'''
    objects = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'

class SubRubricManager(models.Manager):
    '''Менеджер подрубрики'''
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)

class SubRubric(Rubric):
    '''Модель подрубрик'''
    objects = SubRubricManager()

    def __str__(self):
        return '%s - %s' % (self.super_rubric.name, self.name)

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name',
                    'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'

@deconstructible
class WordCountValidator(object):
    def __init__(self, count):
        self.count = count

    def __call__(self, val):
        if len(str(val).split(' ')) < self.count :
            raise ValidationError('Контент должен содержать как ' +
                        'минимум %(count)s слов',
                        code='not_enough_words',
                        params={'count': self.count})

    def __eq__(self, other):
        return self.count == other.count

class PostManager(models.Manager):
    '''Менеджер записей'''
    def get_queryset(self):
        return super().get_queryset()\
            .select_related('rubric', 'author')\
            .prefetch_related('postadditionalimage_set',
                              'postviewcount_set',
                              'postlike_set',
                              'postdislike_set',
                              'postcomment_set')\
            .filter(is_active=True)

class Post(models.Model):
    '''Модель постов'''
    objects = PostManager()

    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT,
                               verbose_name='Рубрика')
    title = models.CharField(max_length=80, db_index=True,
                             verbose_name='Название')
    slug = models.CharField(max_length=50, null=True, blank=True,
                            verbose_name='Слаг')
    content = models.TextField(verbose_name='Содержание',
                               validators=[MinLengthValidator(100, 'Содержание должно быть длинной минимум в 100 символов'),
                                           WordCountValidator(10)])
    preview = models.ImageField(null=True, blank=True,
                                upload_to=get_image_path_post,
                                verbose_name='Превью')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                               verbose_name='Автор')
    is_active = models.BooleanField(default=True,
                                    db_index=True,
                                    verbose_name='Активна')
    tag = models.ManyToManyField('PostTag', verbose_name='Тэг')
    created_at = models.DateTimeField(auto_now_add=True,
                                      db_index=True,
                                      verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-created_at']

    def delete(self, *args, **kwargs):
        for ai in self.postadditionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.slug:
            key = random_key(20)
            self.slug = f'{self.author.username}-{key}'[:50]
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} - {self.author.username} - {self.created_at}'

    def get_absolute_url(self):
        return reverse('gnome_main:show-post', kwargs={'slug': self.slug})

    def get_view_count(self):
        '''Возвращает количество просмотров записи'''
        return self.postviewcount_set.count()

    def get_like_count(self):
        '''Возвращает количество лайков записи'''
        return self.postlike_set.count()

    def get_dislike_count(self):
        '''Возвращает количество дизлайков записи'''
        return self.postdislike_set.count()

    def get_comment_count(self):
        '''Возвращает количество комментариев записи'''
        return self.postcomment_set.count()

    def get_posttags(self):
        '''Возвращает все связанные с постом тэги'''
        return self.tag.all()


class PostAdditionalImage(models.Model):
    '''Модель дополнительных изображений'''
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Пост')
    media = models.FileField(upload_to=get_image_path_post_ai,
                             verbose_name='Медиа')

    class Meta:
        verbose_name = 'Медиа-файл'
        verbose_name_plural = 'Медиа-файл'

    def __str__(self):
        return f'{self.post.id}-{self.media.url}'

class PostViewCount(models.Model):
    '''Модель просмотра'''
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Пост')
    ip_address = models.GenericIPAddressField(verbose_name='Ip адрес')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                             null=True, blank=True,
                             verbose_name='Просмотревший пользователь')
    viewed_on = models.DateTimeField(auto_now_add=True,
                                     db_index=True,
                                     verbose_name='Дата просмотра')

    class Meta:
        ordering = ('-viewed_on',)
        verbose_name = 'Просмотр'
        verbose_name_plural = 'Просмотры'

    def __str__(self):
        return f'Просмотр. Пост: {self.post.id} - дата: {self.viewed_on}'

class PostLike(models.Model):
    '''Модель лайков поста'''
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Пост')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ['post', 'user']

    def __str__(self):
        return f'Лайк. Пост:{self.post.id} - пользователь{self.user.id}'

class PostDisLike(models.Model):
    '''Модель дизлайков поста'''
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Пост')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Дизлайк'
        verbose_name_plural = 'Дизлайки'
        unique_together = ['post', 'user']

    def __str__(self):
        return f'Дизлайк. Пост:{self.post.id} - пользователь{self.user.id}'

class PostFavourite(models.Model):
    '''Модель избранных постов пользователя'''
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Пост')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['post', 'user']

    def __str__(self):
        return f'Избранное. Пост:{self.post.id} - пользователь{self.user.id}'

class PostComment(models.Model):
    '''Модель комментариев поста'''
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Пост')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    comment = models.CharField(max_length=500,
                               validators=[MinLengthValidator(1, 'Минимальная длина комментария 1 символ')],
                               verbose_name='Текст комментария',
                               blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True,
                                      db_index = True,
                                      verbose_name='Дата создания')
    is_changed = models.BooleanField(default=False, null=True,
                                     verbose_name='Изменён ли')
    super_comment = models.ForeignKey('SuperPostComment', on_delete=models.CASCADE,
                                     null=True, blank=True,
                                     verbose_name='Надкомментарий')

class SuperPostCommentManager(models.Manager):
    '''Менеджер надкомментария'''
    def get_queryset(self):
        return super().get_queryset()\
            .filter(super_comment__isnull=True)
            # .select_related('CommentLike', 'CommentDisLike')\

class SuperPostComment(PostComment):
    '''Надкомментарий, у которого будут ответы'''
    objects = SuperPostCommentManager()

    class Meta:
        proxy = True
        verbose_name = 'Надкомментарий'
        verbose_name_plural = 'Надкомментарии'

    def __str__(self):
        return f'Надкомментарий: {self.id}'

    def get_subcomments_count(self):
        return f'{self.subpostcomment_set.count()}'

class SubPostCommentManager(models.Manager):
    '''Менеджер подкомментария'''
    def get_queryset(self):
        return super().get_queryset()\
            .filter(super_comment__isnull=False)
            # .select_related('CommentLike', 'CommentDisLike')\

class SubPostComment(PostComment):
    '''Модель подкомментария'''
    objects = SubPostCommentManager()

    class Meta:
        proxy = True
        ordering = ('super_comment__post', 'super_comment__user')
        verbose_name = 'Подкомментарий'
        verbose_name_plural = 'Подкомментарии'

    def __str__(self):
        return f'Надкомментарий: {self.super_comment.id} - Подкомментарий:{self.id}'

class CommentLike(models.Model):
    '''Модель лайков комментария'''
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE,
                             verbose_name='Надкомментарий')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Лайк комментария'
        verbose_name_plural = 'Лайки комментариев'
        unique_together = ['comment', 'user']

    def __str__(self):
        return f'Коммент-лайк: {self.comment.id}; User_id: {self.user.id}'

class CommentDisLike(models.Model):
    '''Модель дизлайков комментария'''
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE,
                             verbose_name='Надкомментарий')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Дизлайк комментария'
        verbose_name_plural = 'Дизлайки комментариев'
        unique_together = ['comment', 'user']

    def __str__(self):
        return f'Коммент-дизлайк: {self.comment.id}; User_id: {self.user.id}'

class PostReport(models.Model):
    '''Модель жалобы на пост'''
    type_choices = [
        ('Дискриминация', 'Дискриминация'),
        ('Контент сексуального характера', 'Контент сексуального характера'),
        ('Нежелательный контент', 'Нежелательный контент'),
        ('Пропаганда наркотиков, алкоголя, табачной продукции', 'Пропаганда наркотиков, алкоголя, табачной продукции'),
        ('Демонстрация насилия', 'Демонстрация насилия')
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Запись')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    type = models.CharField(choices=type_choices, null=False, blank=False,
                            verbose_name='Тип жалобы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    text = models.CharField(max_length=300, null=True, blank=True,
                            verbose_name='Текст жалобы')

    class Meta:
        verbose_name = 'Жалоба на запись'
        verbose_name_plural = 'Жалобы на записи'
        unique_together = ['post', 'user']

    def __str__(self):
        return f'Жалоба на пост с id - {self.post.id};' \
               f'Тип жалобы: {self.type};' \
               f'пользователь, оставивший жалобу: {self.user.username}'

class CommentReport(models.Model):
    '''Модель жалобы на пост'''
    type_choices = [
        ('Дискриминация', 'Дискриминация'),
        ('Контент сексуального характера', 'Контент сексуального характера'),
        ('Нежелательный контент', 'Нежелательный контент'),
        ('Пропаганда наркотиков, алкоголя, табачной продукции', 'Пропаганда наркотиков, алкоголя, табачной продукции'),
        ('Демонстрация насилия', 'Демонстрация насилия'),
        ('Оскорбления', 'Оскорбления')
    ]

    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE)
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE)
    type = models.CharField(choices=type_choices, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        verbose_name = 'Жалоба на комментарий'
        verbose_name_plural = 'Жалобы на комментарии'
        unique_together = ['comment', 'user']

    def __str__(self):
        return f'Жалоба на комментарий с id - {self.comment.id};' \
               f'Тип жалобы: {self.type};' \
               f'пользователь, оставивший жалобу: {self.user.username}'

class PostTag(models.Model):
    tag = models.CharField(max_length=50, verbose_name='Тэг', null=False,
                           blank=False)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.tag}'

class Notification(models.Model):
    user = models.ForeignKey(AdvUser, null=False, blank=False, verbose_name='Адресат',
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=1, choices=(
        ('r', 'На вас поступила новая жалоба'),
        ('s', 'У вас новый подписчик!'),
        ('c', 'У вас новый комментарий!')
    ), verbose_name='Сообщение')
    message = models.CharField(null=False, blank=False,
                               verbose_name='Сообщение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано автором?')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ('-created_at',)

    def __str__(self):
        return f'notification_id - {self.id}; destination - {self.user}'