from django import forms
from django.contrib import admin


from .forms import SubRubricForm, SubPostCommentForm
from .models import *
from .utilities import send_activation_notification
# from image_cropping import ImageCroppingMixin
import datetime

from ckeditor_uploader.widgets import CKEditorUploadingWidget

class PostAdminForm(forms.ModelForm):
    content = forms.CharField(label='Содержание', widget=CKEditorUploadingWidget())
    class Meta:
        model = Post
        fields = '__all__'

# Рассылка писем с требованием пройти активацию
def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Письма с требованиями отправлены')
send_activation_notifications.short_description = 'Отправка писем' \
'с требованиями активации'


class NonactivatedFilter(admin.SimpleListFilter):
    '''Фильтр пользователей, прошедших активацию'''
    title = 'Прошли активацию?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return [
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли более 3 дней'),
            ('week', 'Не прошли более недели'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif self.value() == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False,
                                   date_joined__date__lt=d)
        elif self.value() == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False,
                                   date_joined__date__lt=d)


class AdvUserAdmin(admin.ModelAdmin):
    '''Редактор ползователя'''
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = [NonactivatedFilter]
    fields = (('username', 'email'), ('first_name', 'last_name'),
              ('status', 'description'), 'subscriptions',
              ('avatar', 'profile_image'),
              ('send_messages', 'is_active', 'is_activated'),
              ('is_staff', 'is_superuser'),
              'groups', 'user_permissions',
              ('last_login', 'date_joined'))
    exclude = ('slug',)
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)

class SubRubricInline(admin.TabularInline):
    '''Встроенный редактор подрубрики'''
    model = SubRubric

class SuperRubricAdmin(admin.ModelAdmin):
    '''Редактор надрубрики'''
    exclude = ('super_rubric',)
    inlines = (SubRubricInline,)

class SubRubricAdmin(admin.ModelAdmin):
    '''Редактор подрубрики'''
    form = SubRubricForm

class PostAdditionalImageInline(admin.TabularInline):
    '''Встроенный редактор дополнительных медиа-файлов'''
    model = PostAdditionalImage

class PostAdmin(admin.ModelAdmin):
    '''Редактор постов'''
    list_display = ('__str__', 'rubric', 'title', 'content', 'preview', 'author',
                    'is_active', 'created_at')
    search_fields = ('title', 'content', 'author')
    fields = ('preview', 'title', 'content', 'rubric', 'is_active',
              'created_at', 'author')
    inlines = (PostAdditionalImageInline,)
    readonly_fields = ('created_at',)
    form = PostAdminForm

class PostViewCountAdmin(admin.ModelAdmin):
    '''Редактор для просмотров'''
    list_display = ('post', 'user', 'viewed_on')
    exclude = ('ip_address',)
    search_fields = ('user', 'viewed_on')
    readonly_fields = ('viewed_on',)

class PostActivityAdmin(admin.ModelAdmin):
    '''Редактор для лайков, дизлайков, избранного'''
    list_display = ('user', 'post')
    search_fields = ('user', 'post')

class SubPostCommentInline(admin.TabularInline):
    '''Встроенный редактор для подкомментариев'''
    model = SubPostComment

class SuperPostCommentAdmin(admin.ModelAdmin):
    '''Редактор надкомментариев'''
    exclude = ('super_comment',)
    inlines = (SubPostCommentInline,)

class SubPostCommentAdmin(admin.ModelAdmin):
    '''Редактор подкомментариев'''
    form = SubPostCommentForm

class PostCommentActivityAdmin(admin.ModelAdmin):
    '''Редактор для лайков, дизлайков, избранного'''
    list_display = ('user', 'comment')
    search_fields = ('user', 'comment')

admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(SubRubric, SubRubricAdmin)

admin.site.register(Post, PostAdmin)
admin.site.register(PostViewCount, PostViewCountAdmin)
admin.site.register(PostLike, PostActivityAdmin)
admin.site.register(PostDisLike, PostActivityAdmin)
admin.site.register(PostFavourite, PostActivityAdmin)
admin.site.register(SuperPostComment, SuperPostCommentAdmin)
admin.site.register(SubPostComment, SubPostCommentAdmin)
admin.site.register(CommentLike, PostCommentActivityAdmin)
admin.site.register(CommentDisLike, PostCommentActivityAdmin)