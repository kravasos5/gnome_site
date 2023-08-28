from django import template
from django.utils import timezone

register = template.Library()

@register.filter(name='sub_pluralize')
def sub_pluralize(value):
    new_value = str(value)
    if value == 0 or value >= 5:
        new_value += ' подписчиков'
    elif value == 1:
        new_value += ' подписчик'
    else:
        new_value += ' подписчика'
    return new_value

@register.filter(name='post_pluralize')
def post_pluralize(value):
    new_value = str(value)
    if value == 0 or value >= 5:
        new_value += ' записей'
    elif value == 1:
        new_value += ' запись'
    else:
        new_value += ' записи'
    return new_value

@register.filter(name='comment_pluralize')
def post_pluralize(value):
    new_value = str(value)
    if int(str(value)[-1]) == 0 or int(str(value)[-1]) >= 5:
        new_value += ' комментариев'
    elif int(str(value)[-1]) == 1 and value != 11:
        new_value += ' комментарий'
    elif 2 <= int(str(value)[-1]) <= 4:
        new_value += ' комментария'
    return new_value

@register.filter(name='post_views')
def post_views(value):
    new_value = str(value)
    len_v = len(str(value))
    if len_v <= 3:
        pass
    elif 4 <= len_v < 6:
        new_value += 'тыс.'
    elif 6 <= len_v <= 9:
        new_value += 'млн.'
    elif 9 < len_v <= 12:
        new_value += 'трлн.'
    return new_value

@register.filter(name='date_ago')
def date_ago(value):
    new_value = ''
    now = timezone.now()
    diff = (now - value).days
    diff_t = (now - value).total_seconds()
    # секунды
    if diff_t // 60 == 0:
        if str(int(diff_t))[-1] in ('2', '3', '4'):
            new_value += f'{int(diff_t)} секунды назад'
        elif str(int(diff_t // 60))[-1] == '1':
            new_value += f'{int(diff_t)} секунду назад'
        elif 5 <= int(diff_t) <= 20 or 5 <= int(str(int(diff_t))[-1]) <= 9:
            new_value += f'{int(diff_t)} секунд назад'
        elif int(diff_t) == 0:
            new_value += f'только что'
    # минуты
    elif diff_t // 60 < 60:
        if str(int(diff_t // 60))[-1] in ('2', '3', '4') and int(diff_t // 60) > 20:
            new_value += f'{int(diff_t // 60)} минуты назад'
        elif str(int(diff_t // 60)) in ('2', '3', '4'):
            new_value += f'{int(diff_t // 60)} минуты назад'
        elif str(int(diff_t // 60))[-1] == '1' and int(diff_t // 60) != 11:
            new_value += f'{int(diff_t // 60)} минуту назад'
        elif 10 <= int(diff_t // 60) <= 20:
            new_value += f'{int(diff_t // 60)} минут назад'
        else:
            new_value += f'{int(diff_t // 60)} минут назад'
    # часы
    elif 0 < diff_t // 3600 < 24:
        if diff_t // 3600 == 1:
            new_value += f'{int(diff_t // 3600)} час назад'
        elif 1 < diff_t // 3600 < 5:
            new_value += f'{int(diff_t // 3600)} часа назад'
        elif 4 < diff_t // 3600:
            new_value += f'{int(diff_t // 3600)} часов назад'
    # дни
    elif 0 < diff < 7:
        if diff == 1:
            new_value += f'{diff} день назад'
        elif 2 <= diff <= 4:
            new_value += f'{diff} дня назад'
        elif 5 <= diff <= 6:
            new_value += f'{diff} дней назад'
    # недели
    elif 7 <= diff <= 30:
        if diff // 7 == 1:
            new_value += f'{diff // 7} неделю назад'
        elif 2 <= diff // 7 <= 5:
            new_value += f'{diff // 7} недели назад'
    # месяцы
    elif 30 < diff <= 360:
        if diff // 30 == 1:
            new_value += f'{diff // 30} месяц назад'
        elif 2 <= diff // 30 <= 11:
            new_value += f'{diff // 30} месяцев назад'
    # года
    elif diff // 360 == 1:
        if diff // 360 == 1:
            new_value += f'1 год назад'
        elif 2 <= diff // 360 <= 4:
            new_value += f'{diff // 360} года назад'
        elif 5 <= diff // 360:
            new_value += f'{diff // 360} лет назад'
    return new_value

@register.filter(name='is_video_preview')
def is_video_preview(value):
    if str(value).split('.')[1].lower() in ['mp4', 'mov',
                                        'wmv', 'avi',
                                        'avchd', 'flv'
                                        'f4v', 'sfw',
                                        'mkv', 'webm',
                                        'html5', 'mpeg-2']:
        return '/static/gnome_main/css/images/video-preview.jpg'
    else: return False

@register.filter(name='key')
def key(value, key):
    answer_count = ''
    i = value[key]
    if 10 <= int(str(i)[-2:]) <= 20 or 5 <= int(str(i)[-1]) <= 9 or i == 0:
        answer_count = 'Ответов'
    elif int(str(i)[-1]) == 1 and i != 11:
        answer_count = 'Ответ'
    elif 2 <= int(str(i)[-1]) <= 4:
        answer_count = 'Ответа'

    return f'{value[key]} {answer_count}'

@register.filter(name='comment_zero')
def comment_zero(value, key):
    i = value[key]
    if i == 0:
        return True
    else:
        return False

@register.filter(name='subcomment')
def subcomment(value, key):
    return value[key]