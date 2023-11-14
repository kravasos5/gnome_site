from django.utils.datetime_safe import datetime
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, \
    ListAPIView, UpdateAPIView, DestroyAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from gnome_main.mixins import BlogFilterMixin, BlogSearchMixin
from gnome_main.models import PostFavourite, PostLike, PostViewCount, PostDisLike, SuperPostComment, SubPostComment
from gnome_main.permissions import IsAuthor, IsCommentAuthor
from gnome_main.serializers import *

##########################################################################
# Account Views

class UserBase:
    '''Базовый класс для представлений пользователя'''
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        '''Объект - текущий пользователь'''
        return self.request.user

class UserChangeInfoAPIView(UserBase, RetrieveUpdateDestroyAPIView):
    '''Представление просмотра, изменения, удаления пользовательских данных (GET, PUT, PATCH, DELETE)'''

class UserLogoutAPIView(APIView):
    '''Представление выхода из аккаунта'''
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        '''Выход из аккаунта'''
        serializer = self.serializer_class(data=request.data)
        # валидация
        serializer.is_valid(raise_exception=True)
        # вызов метода save сериализатора LogoutSerializer, там refresh_token добавляется
        # в blacklist
        serializer.save()
        # возврат ответа
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserCreateAPIView(CreateAPIView):
    '''Регистрация пользователя'''
    queryset = AdvUser.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)

##########################################################################
# Rubric Views

class RubricBase:
    '''Базовый класс для представлений рубрик'''
    serializer_class = RubricSerializer
    permission_classes = (AllowAny,)
    queryset = Rubric.objects.all()

class RubricListAPIView(RubricBase, ListAPIView):
    '''Представление списка рубрик (GET)'''

class RubricAPIView(RubricBase, RetrieveAPIView):
    '''Представление одной рубрики (GET)'''

##########################################################################
# Post Views

class PostAPIViewBase:
    '''Базовый класс для представлений записей'''
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)
    queryset = Post.objects.all()

class PostPagination(PageNumberPagination):
    '''Базовый класс с пагинацией для представлений с постами'''
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 1000

class PostPaginationAPIViewBase(PostAPIViewBase):
    pagination_class = PostPagination

class PostListCreateAPIView(PostPaginationAPIViewBase, ListCreateAPIView):
    '''Получение всех постов и создание поста (GET, POST)'''
    def get_permissions(self):
        if self.request.method == 'GET':
            # Разрешить доступ всем для GET-запросов
            return (AllowAny(),)
        else:
            # Разрешить доступ только авторизованным пользователям для остальных методов
            return (IsAuthenticated(),)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            # PostSerializer для GET-запросов
            return PostSerializer
        elif self.request.method == 'POST':
            # если не GET-запрос
            return PostUpdateSerializer

    def perform_create(self, serializer):
        # этот метод вызывается только при создании нового поста
        # тут автоматически назначается автор
        serializer.save(author=self.request.user)

class PostFilterAPIView(BlogFilterMixin, PostPaginationAPIViewBase, ListAPIView):
    '''Получение всех постов согласно фильтру (GET)'''

    def get_queryset(self):
        '''Фильтрую записи'''
        queryset = Post.objects.all()
        # извлекаю данные фильтрации
        date_from = self.request.data.get('date-from') or ''
        date_to = self.request.data.get('date-to') or ''
        author = self.request.data.get('author') or ''
        rubrics = self.request.data.get('rubric') or []
        radio = self.request.data.get('radio-filters') or ''
        # проверяю переданные данные
        if not isinstance(rubrics, list):
            raise ValidationError({"error": "rubrics must transfer as array of rubric, for example, ['rubric1', 'rubric2']"})
        elif not isinstance(author, str):
            raise ValidationError({"error": "authorname must be string type"})
        elif date_from != '':
            try:
                datetime.strptime(date_from, '%Y-%m-%d')
            except Exception as ex:
                raise ValidationError({"error": f"{str(ex)}. date-from must be string type, for example, '2023-07-26'. Make sure that the month from 1 to 12 and the day from 1 to 31"})
        elif date_to != '':
            try:
                datetime.strptime(date_to, '%Y-%m-%d')
            except Exception as ex:
                raise ValidationError({"error": f"{str(ex)}. date-to must be string type, for example, '2023-07-26'. Make sure that the month from 1 to 12 and the day from 1 to 31"})
        elif not isinstance(radio, str):
            raise ValidationError({"error": "radio must be string type, for example 'popular'"})
        # применяю метод filter из BlogFilterMixin
        queryset = self.filter(queryset, date_from, date_to, author, rubrics, radio)
        return queryset

class PostSearchAPIView(BlogSearchMixin, PostPaginationAPIViewBase, ListAPIView):
    '''Получение всех постов по поиску (GET)'''

    def get_queryset(self):
        '''Фильтрация согласно поиску'''
        queryset = Post.objects.all()
        # извлекаю данные фильтрации
        find_text = self.request.data.get('text-find')
        # проверяю find_text на валидность
        if not isinstance(find_text, str):
            raise ValidationError({"error": "Indicate text-find or make sure that text-find is string type"})
        # применяю метод search из BlogSearchMixin
        queryset = self.search(queryset, find_text)
        return queryset

class PostFavouriteAPIView(PostPaginationAPIViewBase, ListAPIView):
    '''Получение всех избранных постов (GET)'''
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        '''Фильтрация постов'''
        posts_favourite = PostFavourite.objects.select_related('post').filter(user=self.request.user).order_by(
            '-created_at')
        queryset = [x.post for x in posts_favourite]
        return queryset

class PostLikedAPIView(PostPaginationAPIViewBase, ListAPIView):
    '''Получение всех понравившихся постов (GET)'''
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        '''Фильтрация постов'''
        # нахожу все посты, на которые пользователь поставил лайк
        posts_liked = PostLike.objects.select_related('post').filter(user=self.request.user).order_by('-created_at')
        queryset = [x.post for x in posts_liked]
        return queryset

class PostHistoryAPIView(PostPaginationAPIViewBase, ListAPIView):
    '''Получение истории просмотра постов (GET)'''
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        '''Фильтрация постов'''
        # нахожу все посты, которые пользователь добавил в избранное
        posts_views = PostViewCount.objects.select_related('post').filter(user=self.request.user).order_by('-viewed_on')
        queryset = [x.post for x in posts_views]
        return queryset

class PostRUDAPIView(PostAPIViewBase, RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    '''
    Представление получения записи по id, обновления и удаления
    поста (PUT, PATCH, DELETE)
    '''
    # permission_classes = (IsAuthenticated, IsAuthor)

    def get_permissions(self):
        if self.request.method == 'GET':
            # Разрешить доступ всем для GET-запросов
            return (AllowAny(),)
        else:
            # Разрешить доступ только авторизованным пользователям для остальных методов
            return (IsAuthenticated(), IsAuthor())

    def get_serializer_class(self):
        if self.request.method == 'GET':
            # PostSerializer для GET-запросов
            return PostSerializer
        else:
            # если не GET-запрос
            return PostUpdateSerializer

##########################################################################
# PostViewCount Views

class PostViewBase:
    '''Базовый класс для представлений PostViewCount'''
    serializer_class = PostViewCountSerializer
    permission_classes = (IsAuthenticated,)
    queryset = PostViewCount.objects.all()

class PostViewAPIView(PostViewBase, CreateAPIView):
    '''Представление создания просмотра (POST, DELETE)'''

    def perform_create(self, serializer):
        # этот метод вызывается только при создании нового просмотра
        # тут автоматически назначается пользователь
        if self.request.user:
            serializer.save(user=self.request.user)

class PostViewDeleteAPIView(PostViewBase, DestroyAPIView):
    '''Представление удаления просмотра (DELETE)'''

##########################################################################
# PostLike Views

class PostLDAPIVIewMixin:
    '''
    Миксин для представлений лайков и дизлайков и избранного.
    Добавляет пользователя в data перед передачей сериализатору
    '''

    def post(self, request, *args, **kwargs):
        '''Обработка создания лайка или дизлайка'''
        data = request.data
        # Добавляем пользователя к данным
        data['user'] = request.user.id
        # Передаем данные в сериализатор для валидации и сохранения
        serializer = self.serializer_class(data=data)
        # Проверка валидности данных
        if serializer.is_valid():
            # Сохранение данных
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostLikeBase:
    '''Базовый класс для представление PostLike'''
    serializer_class = PostLikeSerializer
    permission_classes = (IsAuthenticated,)
    queryset = PostLike.objects.all()

class PostLikeCreate(PostLikeBase, PostLDAPIVIewMixin, APIView):
    '''Представлние создания лайка'''

class PostLikeDelete(PostLikeBase, DestroyAPIView):
    '''Представлние удаления лайка'''

##########################################################################
# PostDisLike Views

class PostDisLikeBase:
    '''Базовый класс для представление PostDisLike'''
    serializer_class = PostDisLikeSerializer
    permission_classes = (IsAuthenticated,)
    queryset = PostDisLike.objects.all()

class PostDisLikeCreate(PostDisLikeBase, PostLDAPIVIewMixin, APIView):
    '''Представлние создания дизлайка'''

class PostDisLikeDelete(PostDisLikeBase, DestroyAPIView):
    '''Представлние удаление дизлайка'''

##########################################################################
# PostFavourite Views

class PostFavouriteBase:
    '''Базовый класс для представление PostFavourite'''
    serializer_class = PostFavouriteSerializer
    permission_classes = (IsAuthenticated,)
    queryset = PostFavourite.objects.all()

class PostFavouriteCreate(PostFavouriteBase, PostLDAPIVIewMixin, APIView):
    '''Представлние добавления в избранное'''

class PostFavouriteDelete(PostFavouriteBase, DestroyAPIView):
    '''Представлние удаления из избранного'''

##########################################################################
# PostComment Views

class PostCommentAPIViewMixin:
    '''Миксин для представлений комментариев'''
    def get_serializer_class(self):
        '''Получение сериалайзера'''
        if self.request.method == 'GET':
            return PostCommentSerializer
        elif self.request.method in ('POST', 'DELETE'):
            return PostCommentCreateSerializer
        elif self.request.method in ('PATCH', 'PUT'):
            return PostCommentUpdateSerializer

    def get_permissions(self):
        '''Получение доступа в зависимости от HTTP-метода'''
        if self.request.method == 'GET':
            return (AllowAny(),)
        elif self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return (IsAuthenticated(), IsCommentAuthor())

class PostSuperCommentAPIView(PostCommentAPIViewMixin, ListAPIView):
    '''Представление списка или создания НАДкомментариев (GET, POST)'''
    model = SuperPostComment

    def get_queryset(self):
        '''Получение queryset'''
        if self.request.method == 'GET':
            queryset = self.model.objects.filter(post=self.post)[:self.count]
            return queryset
        elif self.request.method == 'POST':
            return self.model.objects.all()

    def get(self, request, *args, **kwargs):
        '''Получение всех НАДкомментариев'''
        self.count = request.data.get('count', None)
        self.post = request.data.get('post', None)
        # валидация id поста
        if not isinstance(self.post, int) or not Post.objects.filter(id=self.post).exists() or self.post == None:
            raise ValidationError({'error': 'Поста с таким id не существует. Укажите post корректно'})
        # валидация количества запрашиваемых комментариев
        if not isinstance(self.count, int) or self.count < 1 or self.count == None:
            raise ValidationError({'error': 'Количество запрашиваемых комментариев (count) должно быть больше либо равно 1. Укажите count корректно'})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        '''Метод создания НАДкомментария'''
        # получаю data и записываю параметр is_changed = False,
        # так как коммент только создан
        data = request.data
        data['is_changed'] = False
        # это НАДкомментарий
        data['super_comment'] = None
        # назначаю автора комментария
        data['user'] = request.user.id
        # сериализация
        serializer = self.get_serializer_class()(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # формирование ответа
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PostSubCommentAPIView(PostCommentAPIViewMixin, ListAPIView):
    '''Представление списка ПОДкомментариев (GET)'''
    model = SubPostComment

    def get_queryset(self):
        '''Получение queryset'''
        if self.request.method == 'GET':
            queryset = self.model.objects.filter(super_comment=self.super_id)[:self.count]
            return queryset
        else:
            return self.model.objects.all()

    def get(self, request, *args, **kwargs):
        '''Получение всех ПОДкомментариев'''
        self.count = request.data.get('count', None)
        self.super_id = request.data.get('super_id', None)
        # валидация id поста
        if not isinstance(self.super_id, int) or not SuperPostComment.objects.filter(id=self.super_id).exists() or self.super_id == None:
            raise ValidationError({'error': 'НАДкомментария с таким id не существует. Укажите super_id корректно'})
        # валидация количества запрашиваемых комментариев
        if not isinstance(self.count, int) or self.count < 1 or self.count == None:
            raise ValidationError({'error': 'Количество запрашиваемых комментариев (count) должно быть больше либо равно 1. Укажите count корректно'})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        '''Метод создания ПОДкомментария'''
        # получаю data и записываю параметр is_changed = False,
        # так как коммент только создан
        data = request.data
        data['is_changed'] = False
        # назначаю автора комментария
        data['user'] = request.user.id
        # проверяю есть ли super_comment в data
        super_comment = data.get('super_comment', None)
        # валидация super_comment
        if super_comment == None or not isinstance(super_comment, int) or not SuperPostComment.objects.filter(id=super_comment).exists():
            raise ValidationError({'error': 'Укажите supper_comment корректно. Это должно быть число. Либо указанного SuperComment не существует.'})
        # назначаю пост такой же, как и у НАДкомментария
        data['post'] = SuperPostComment.objects.get(id=super_comment).post.id
        # сериализация
        serializer = self.get_serializer_class()(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # формирование ответа
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PostCommentUpdateDelete(PostCommentAPIViewMixin, UpdateAPIView, DestroyAPIView):
    '''Обновление и удаление комментариев (PUT, PATCH, DELETE)'''
    queryset = PostComment.objects.all()

    def put(self, request, *args, **kwargs):
        '''Изменение комментария PUT'''
        serializer = self.update_serializer(request.data)
        # формирование ответа
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        '''Изменение комментария PATCH'''
        serializer = self.update_serializer(request.data)
        # формирование ответа
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update_serializer(self, data):
        '''Добавляет необходимую информацию в data при обновлении коммента'''
        # назначаю is_cahnged = True, так как комментарий изменили
        data['is_changed'] = True
        # получаем экземпляр комментария
        instance = self.get_object()
        # сериализация
        serializer = self.get_serializer_class()(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.validated_data)
        # возвращаю сериализатор
        return serializer

##########################################################################
# PostCommentLike Views

class CommentLikeAPIViewMixin:
    '''Миксин для представлений лайков на комментарий'''
    queryset = CommentLike.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentLikeSerializer

class CommentLDCreateMixin:
    '''Миксин, добавляющий методы создания лайка и дизлайка на комментарии'''

    def post(self, request, *args, **kwargs):
        '''Метод обрабатывающий создание лайка/дизлайка на коммент'''
        data = request.data
        # добавляю user в дату
        data['user'] = request.user.id
        # Передаем данные в сериализатор для валидации и сохранения
        serializer = self.serializer_class(data=data)
        # Проверка валидности данных
        if serializer.is_valid():
            # Сохранение данных
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentLikeCreateAPIView(CommentLikeAPIViewMixin, CommentLDCreateMixin, APIView):
    '''Представление для создания лайка на комментарий (GET)'''

class CommentLikeDeleteAPIView(CommentLikeAPIViewMixin, DestroyAPIView):
    '''Представление, удаляющее лайк с комментария'''

##########################################################################
# PostCommentDisLike Views

class CommentDisLikeAPIViewMixin:
    '''Миксин для представлений дизлайков на комментарий'''
    queryset = CommentDisLike.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentDisLikeSerializer

class CommentDisLikeCreateAPIView(CommentDisLikeAPIViewMixin, CommentLDCreateMixin, APIView):
    '''Представление для создания дизлайка на комментарий (GET)'''

class CommentDisLikeDeleteAPIView(CommentDisLikeAPIViewMixin, DestroyAPIView):
    '''Представление, удаляющее дизлайк с комментария'''

##########################################################################
# PostReport Views

class ReportAPIViewMixin:
    '''Метод, подмешивающий метод post для представлений жалоб'''

    def post(self, request, *args, **kwargs):
        '''Метод, создающий жалобу на пост'''
        # извлекаю data
        data = request.data
        # добавляю пользователя в data
        data['user'] = request.user.id
        # проверка, что пост из запроса не создан пользователем
        if 'post' in self.__class__.__name__.lower():
            post_id = data.get('post', None)
            # валидация поста
            # правильно ли задан post в запросе
            if post_id == None or not isinstance(post_id, int) or post_id < 0:
                raise ValidationError({'error': 'post не задан или задан в неправильном формате - правильный формат integer.'})
            # существует ли пост с таким post_id
            if not Post.objects.filter(id=post_id).exists():
                raise ValidationError({'error': 'поста с таким id не существует'})
            # проверка является ли пользователь автором поста
            if Post.objects.get(id=post_id).author == request.user:
                raise ValidationError({'error': 'Нельзя написать жалобу на свой пост'})
        else:
            comment_id = data.get('comment', None)
            # валидация комментария
            # правильно ли задан post в запросе
            if comment_id == None or not isinstance(comment_id, int) or comment_id < 0:
                raise ValidationError(
                    {'error': 'comment не задан или задан в неправильном формате - правильный формат integer.'})
            # существует ли пост с таким comment_id
            if not PostComment.objects.filter(id=comment_id).exists():
                raise ValidationError({'error': 'комментария с таким id не существует'})
            # проверка является ли пользователь автором комментария
            if PostComment.objects.get(id=comment_id).user == request.user:
                raise ValidationError({'error': 'Нельзя написать жалобу на свой комментарий'})
        # извлекаю type жалобы и провожу валидацию
        type = data.get('type', None)
        if type == None or not isinstance(type, str):
            raise ValidationError({'error': 'type обязательное поле. type должен быть string type'})
        elif type not in self.type_choices:
            raise ValidationError({'error': f'Такого типа жалоб не существует. Жалобы бывают следующих типов: {self.type_choices}'})
        serializer = self.serializer_class(data=data)
        # валидация
        serializer.is_valid(raise_exception=True)
        # сохраняю жалобу
        serializer.save()
        # формирование ответа
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PostReportAPIView(ListAPIView, ReportAPIViewMixin):
    '''Представление жалобы на пост'''
    permission_classes = (IsAuthenticated,)
    serializer_class = PostReportSerializer
    # варианты выбора типов жалоб для проверки
    type_choices = [x[0] for x in PostReport.type_choices]

    def get_serializer_class(self):
        '''Метод, возвращающий сериализатор'''
        if self.request.method == 'GET':
            return PostReportSerializer
        else:
            return PostReportCreateSerializer

    def get_queryset(self):
        '''Метод возвращающий queryset'''
        if self.request.method == 'GET':
            # Если GET метод, то нужно вернуть список жалоб на посты
            # пользователя self.reported_user
            return PostReport.objects.filter(post__author=self.reported_user)
        else:
            return PostReport.objects.all()

    def get(self, request, *args, **kwargs):
        '''Метод, выводящий список жалоб'''
        # получаю пользователя для которого нужно вывести список жалоб
        self.reported_user = request.user
        return super().get(request, *args, **kwargs)

##########################################################################
# CommentReport Views

class CommentReportAPIView(ListAPIView, ReportAPIViewMixin):
    '''Представление жалобы на пост'''
    permission_classes = (IsAuthenticated,)
    # варианты выбора типов жалоб для проверки
    type_choices = [x[0] for x in CommentReport.type_choices]

    def get_serializer_class(self):
        '''Метод, возвращающий сериализатор'''
        if self.request.method == 'GET':
            return CommentReportSerializer
        else:
            return CommentReportCreateSerializer

    def get_queryset(self):
        '''Метод возвращающий queryset'''
        if self.request.method == 'GET':
            # Если GET метод, то нужно вернуть список жалоб на посты
            # пользователя self.reported_user
            return CommentReport.objects.filter(comment__user=self.reported_user)
        else:
            return CommentReport.objects.all()

    def get(self, request, *args, **kwargs):
        '''Метод, выводящий список жалоб'''
        # получаю пользователя для которого нужно вывести список жалоб
        self.reported_user = request.user
        return super().get(request, *args, **kwargs)

##########################################################################
# Notification Views

class NotificationAPIView(ListAPIView):
    '''Представление, возвращающее список уведомлений (GET)'''
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        '''Метод возвращающий queryset'''
        if self.request.method == 'GET':
            # Если GET метод, то нужно вернуть список жалоб на посты
            # пользователя self.reported_user
            return Notification.objects.filter(user=self.user_id)
        else:
            return Notification.objects.all()

    def get(self, request, *args, **kwargs):
        '''Метод, выводящий список уведомлений'''
        # получаю id user
        self.user_id = request.user.id
        return super().get(request, *args, **kwargs)

##########################################################################
# AdminUser Views

class AdminPermissionBase:
    '''Базовый класс для админ-представлений'''
    permission_classes = (IsAuthenticated, IsAdminUser)

class AdminListStartCountBase:
    '''
    Базовый класс для админ-классов, где нужно выводить список от start
    и где есть count
    '''
    def get_queryset(self):
        '''
        Если метод GET, то выбираю от start до count + start,
        иначе выбираю все записи
        '''
        if self.request.method == 'GET':
            queryset = self.model.objects.all().order_by('id')[self.start:self.start+self.count]
            return queryset
        else:
            return self.model.objects.all()

    def get(self, request, *args, **kwargs):
        self.start = request.data.get('start')
        self.count = request.data.get('count')
        if not isinstance(self.count, int) or self.count < 1 or not isinstance(self.start, int):
            return Response({'message': 'Не указан start или count или они указаны в неверном формате'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

class AdminAllUsersAPIView(AdminListStartCountBase, AdminPermissionBase, ListCreateAPIView):
    '''Получение всех аккаунтов'''
    model = AdvUser

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminUserSerializer
        else:
            return AdminUserCreateSerializer

class AdminUserRUDAPIView(AdminPermissionBase, RetrieveUpdateDestroyAPIView):
    '''
    Представление получения (GET), обновления (PUT, PATCH) и
    удаления (DELETE) пользователя админом
    '''
    queryset = AdvUser.objects.all()
    serializer_class = AdminUserChangeSerializer

##########################################################################
# AdminRubric Views

class AdminRubricListAPIView(AdminListStartCountBase, AdminPermissionBase, ListCreateAPIView):
    '''Представление, выводящее список рубрик и создающее новую рубрику (GET, POST)'''
    model = Rubric

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminRubricSerializer
        else:
            return AdminRubricCreateChangeSerializer

class AdminRubricRUDAPIView(AdminPermissionBase, RetrieveUpdateDestroyAPIView):
    '''
    Представление получения (GET), обновления (PUT, PATCH) и
    удаления (DELETE) рубрики админом
    '''
    queryset = Rubric.objects.all()
    serializer_class = AdminRubricCreateChangeSerializer

##########################################################################
# AdminPost Views

class AdminPostListCreateAPIView(AdminListStartCountBase, AdminPermissionBase, ListCreateAPIView):
    '''Получение всех постов и создание поста (GET, POST)'''
    model = Post

    def get_serializer_class(self):
        if self.request.method == 'GET':
            # PostSerializer для GET-запросов
            return PostSerializer
        elif self.request.method == 'POST':
            # если не GET-запрос
            return AdminPostUpdateSerializer

class AdminPostRUDAPIView(AdminPermissionBase, RetrieveUpdateDestroyAPIView):
    '''
    Представление получения (GET), обновления (PUT, PATCH) и
    удаления (DELETE) поста админом
    '''
    queryset = Post.objects.all()
    serializer_class = AdminPostUpdateSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            # PostSerializer для GET-запросов
            return PostSerializer
        elif self.request.method in ('PUT', 'PATCH', 'DELETE'):
            # если не GET-запрос
            return AdminPostUpdateSerializer

##########################################################################
# AdminPostViewCount Views

class AdminPostViewBase:
    '''Базовый класс для представлений PostViewCount'''
    serializer_class = PostViewCountSerializer
    queryset = PostViewCount.objects.all()

class AdminPostViewAPIView(AdminPermissionBase, AdminPostViewBase, CreateAPIView):
    '''Админ представление создания просмотра (POST, DELETE)'''

class AdminPostViewDeleteAPIView(AdminPermissionBase, AdminPostViewBase, DestroyAPIView):
    '''Админ представление удаления просмотра (DELETE)'''

##########################################################################
# AdminPostLike Views

class AdminPostLikeBase:
    '''Базовый класс для представление PostLike'''
    serializer_class = PostLikeSerializer
    queryset = PostLike.objects.all()

class AdminPostLikeCreate(AdminPermissionBase, PostLikeBase, CreateAPIView):
    '''Админ представлние создания лайка'''

class AdminPostLikeDelete(AdminPermissionBase, PostLikeBase, DestroyAPIView):
    '''Админ представлние удаления лайка'''

##########################################################################
# AdminPostDisLike Views

class AdminPostDisLikeBase:
    '''Базовый класс для представление PostDisLike'''
    serializer_class = PostDisLikeSerializer
    queryset = PostDisLike.objects.all()

class AdminPostDisLikeCreate(AdminPermissionBase, PostDisLikeBase, CreateAPIView):
    '''Админ представлние создания лайка'''

class AdminPostDisLikeDelete(AdminPermissionBase, PostDisLikeBase, DestroyAPIView):
    '''Админ представлние удаления лайка'''

##########################################################################
# AdminPostFavourite Views

class AdminPostFavouriteBase:
    '''Базовый класс для представление PostFavourite'''
    serializer_class = PostFavouriteSerializer
    queryset = PostFavourite.objects.all()

class AdminPostFavouriteCreate(AdminPermissionBase, AdminPostFavouriteBase, CreateAPIView):
    '''Админ представление добавления в избранное'''

class AdminPostFavouriteDelete(AdminPermissionBase, AdminPostFavouriteBase, DestroyAPIView):
    '''Админ представление удаления из избранного'''

##########################################################################
# AdminComment Views

class AdminPostCommentAPIViewMixin:
    '''Миксин для представлений комментариев'''
    def get_serializer_class(self):
        '''Получение сериалайзера'''
        if self.request.method == 'GET':
            return PostCommentSerializer
        elif self.request.method in ('POST', 'DELETE'):
            return PostCommentCreateSerializer
        elif self.request.method in ('PATCH', 'PUT'):
            return PostCommentUpdateSerializer

class AdminPostCommentListCreateAPIView(AdminPermissionBase, AdminPostCommentAPIViewMixin, AdminListStartCountBase, ListCreateAPIView):
    '''Получение списка комментариев и создание нового комментария (GET, POST)'''
    model = PostComment

class AdminPostCommentUpdateAPIView(AdminPermissionBase, AdminPostCommentAPIViewMixin, RetrieveUpdateDestroyAPIView):
    '''Получение списка комментариев и создание нового комментария (PUT, PATCH, DELETE)'''
    queryset = PostComment.objects.all()

##########################################################################
# AdminCommentLike Views

class AdminCommentLikeAPIViewMixin:
    '''Миксин для админ представлений лайка на комментарий'''
    serializer_class = CommentLikeSerializer
    queryset = CommentLike.objects.all()

class AdminCommentLikeCreateAPIView(AdminPermissionBase, AdminCommentLikeAPIViewMixin, CreateAPIView):
    '''Представление для создания лайка на комментарий (GET)'''

class AdminCommentLikeDeleteAPIView(AdminPermissionBase, AdminCommentLikeAPIViewMixin, DestroyAPIView):
    '''Представление, удаляющее лайк с комментария'''

##########################################################################
# AdminCommentDisLike Views

class AdminCommentDisLikeAPIViewMixin:
    '''Миксин для админ представлений лайка на комментарий'''
    serializer_class = CommentDisLikeSerializer
    queryset = CommentDisLike.objects.all()

class AdminCommentDisLikeCreateAPIView(AdminPermissionBase, AdminCommentDisLikeAPIViewMixin, CreateAPIView):
    '''Представление для создания лайка на комментарий (GET)'''

class AdminCommentDisLikeDeleteAPIView(AdminPermissionBase, AdminCommentDisLikeAPIViewMixin, DestroyAPIView):
    '''Представление, удаляющее лайк с комментария'''

##########################################################################
# AdminPostReport Views

class AdminPostReportMixin:
    '''Миксин для админ представлений жалоб на посты'''
    serializer_class = PostReportSerializer
    queryset = PostReport.objects.all()

class AdminPostReportList(AdminPermissionBase, AdminListStartCountBase, AdminPostReportMixin, ListAPIView):
    '''Админ представление списка жалоб на пост (GET)'''
    model = PostReport

class AdminPostReport(AdminPermissionBase, AdminPostReportMixin, RetrieveDestroyAPIView):
    '''Админ представление жалобы на пост и удаления жалобы (GET, DELETE)'''

##########################################################################
# AdminCommentReport Views

class AdminCommentReportMixin:
    '''Миксин для админ представлений жалоб на комментарии'''
    serializer_class = CommentReportSerializer
    queryset = CommentReport.objects.all()

class AdminCommentReportList(AdminPermissionBase, AdminListStartCountBase, AdminCommentReportMixin, ListAPIView):
    '''Админ представление списка жалоб на комментарий (GET)'''
    model = CommentReport

class AdminCommentReport(AdminPermissionBase, AdminCommentReportMixin, RetrieveDestroyAPIView):
    '''Админ представление жалобы на комментарий и удаления жалобы (GET, DELETE)'''

##########################################################################
# AdminNotification Views

class AdminNotificationListCreateAPIView(AdminPermissionBase, AdminListStartCountBase, ListCreateAPIView):
    '''
    Админ представление создания уведомления и получения списка уведомлений
    (GET, POST)
    '''
    model = Notification
    serializer_class = AdminNotificationSerializer
    queryset = Notification.objects.all()

class AdminNotificationRUDAPIView(AdminPermissionBase, RetrieveUpdateDestroyAPIView):
    '''
    Админ представление для изменения, удаления и получения уведомления
    (GET, PUT, PATCH, DELETE)
    '''
    serializer_class = AdminNotificationUpdateSerializer
    queryset = Notification.objects.all()