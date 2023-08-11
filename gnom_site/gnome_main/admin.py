from django.contrib import admin

from .forms import SubRubricForm
from .models import *
from .utilities import send_activation_notification
import datetime

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

admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(SubRubric, SubRubricAdmin)

