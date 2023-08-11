from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.text import slugify
from .utilities import get_image_path_post

class AdvUser(AbstractUser):
    def get_profile_image_path(self, filename):
        username = self.username
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

class PostManager(models.Manager):
    '''Менеджер записей'''
    # Тут прописать методы, чтобы использовался select_related
    # для rubric и author. А ткаже prefetch_related для view,
    # likes, dislikes, comments, если я всё правильно понял
    # + зарегистрировать все новые модели в админке

class Post(models.Model):
    '''Модель постов'''
    # select_related и prefetch_related
    # https://proghunter.ru/articles/django-base-2023-unique-views-count-for-posts#%D0%BC%D0%BE%D0%B4%D0%B5%D0%BB%D1%8C-%D0%B4%D0%BB%D1%8F-%D1%81%D1%87%D0%B5%D1%82%D1%87%D0%B8%D0%BA%D0%B0-%D1%83%D0%BD%D0%B8%D0%BA%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D1%85-%D0%BF%D1%80%D0%BE%D1%81%D0%BC%D0%BE%D1%82%D1%80%D0%BE%D0%B2-%D0%B2-django
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT,
                               verbose_name='Рубрика')
    title = models.CharField(max_length=80, db_index=True,
                             verbose_name='Название')
    content = models.TextField(verbose_name='Содержание')
    preview = models.ImageField(null=True, blank=True, required=False,
                                upload_to=get_image_path_post,
                                verbose_name='Превью')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                               verbose_name='Автор')
    is_active = models.BooleanField(default=True,
                                    db_index=True,
                                    verbose_name='Активна')
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

    def __str__(self):
        return f'{self.title} - {self.author.name} - {self.created_at}'

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


class PostAdditionalImage(models.Model):
    '''Модель дополнительных изображений'''
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Пост')
    media = models.FileField(upload_to=get_image_path_post,
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
    ip_addres = models.GenericIPAddressField(verbose_name='Ip адрес')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                             required=False, null=True, blank=True,
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

    def __str__(self):
        return f'Избранное. Пост:{self.post.id} - пользователь{self.user.id}'

class PostComment(models.Model):
    '''Модель комментариев поста'''
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Пост')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    comment = models.CharField(max_length=400,
                               verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True,
                                      db_index = True,
                                      verbose_name='Дата создания')
    super_comment = models.ForeignKey('SuperPostComment', on_delete=models.PROTECT,
                                     null=True, blank=True,
                                     verbose_name='Надкомментарий')

class SuperPostCommentManager(models.Manager):
    '''Менеджер надкомментария'''
    def get_queryset(self):
        return super().get_queryset.filter(super_comment__isnull=True)

class SuperPostComment(PostComment):
    '''Надкомментарий, у которого будут ответы'''
    objects = SuperPostCommentManager()

    class Meta:
        proxy = True
        verbose_name = 'Надкомментарий'
        verbose_name_plural = 'Надкомментарии'

    def __str__(self):
        return f'Надкомментарий: {self.id}'

class SubPostCommentManager(models.Manager):
    '''Менеджер подкомментария'''
    def get_queryset(self):
        return super().get_queryset.filter(super_comment__isnull=False)

class SubPostComment(PostComment):
    '''Модель подкомментария'''
    objects = SubPostCommentManager()

    class Meta:
        proxy = True
        ordering = ('super_comment__name',)
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
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return f'Пост: {self.post.id}; User_id: {self.user.id}; super_comment:' \
               f'{self.comment.id}'

class CommentDisLike(models.Model):
    '''Модель дизлайков комментария'''
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE,
                             verbose_name='Надкомментарий')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Дизлайк'
        verbose_name_plural = 'Дизлайки'

    def __str__(self):
        return f'Пост: {self.post.id}; User_id: {self.user.id}; comment:' \
               f'{self.comment.id}'