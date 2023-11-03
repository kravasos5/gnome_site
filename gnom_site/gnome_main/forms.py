from captcha.fields import CaptchaField
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth import password_validation

# from .apps import user_registered
from django.forms import inlineformset_factory

from .apps import user_registered
from .models import *

class RegisterUserForm(forms.ModelForm):
    '''форма для регистрации пользователя'''
    email = forms.EmailField(required=True,
                             label='Адрес электронный почты')
    password1 = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Введите пароль повторно',
                                widget=forms.PasswordInput)
    captcha = CaptchaField(label='Каптча')

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введённые пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'send_messages')

class CustomClearableFileInputCU(forms.ClearableFileInput):
    initial_text = ''
    template_name = 'widget/customImageFieldTemplate.html'

class ChangeUserInfoForm(forms.ModelForm):
    '''форма для обновления пользовательских данных'''
    email = forms.EmailField(required=True,
                             label='Адресс электронной почты')
    status = forms.CharField(required=False,
                             label='Статус профиля (максимум 50 символов)')
    description = forms.CharField(required=False,
                             label='Описание профиля (максимум 500 символов)',
                             widget=forms.Textarea)
    avatar = forms.ImageField(label='Аватар (рекомендуемый размер 200x200 px)',
                              widget=CustomClearableFileInputCU(attrs={'id': 'id_avatar'}))
    profile_image = forms.ImageField(label='Шапка профиля (рекомендуемый размер 1920x300 px)',
                        widget=CustomClearableFileInputCU(attrs={'id': 'id_profile_image'}))

    class Meta:
        model = AdvUser
        fields = ('avatar', 'profile_image',
                  'username', 'email', 'status', 'description','first_name', 'last_name',
                  'send_messages')

class DeleteUserForm(forms.Form):
    '''форма для удаления пользователя'''
    username = forms.CharField(required=True, label='Логин')
    password = forms.CharField(required=True, label='Пароль',
                                widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    class Meta:
        fields = ('username', 'password')

class SubRubricForm(forms.ModelForm):
    '''Форма подрубрики'''
    super_rubric = forms.ModelChoiceField(
        queryset=SuperRubric.objects.all(), empty_label=None,
        label='Надрубрика', required=True)

    class Meta:
        model = SubRubric
        fields = '__all__'

class SubPostCommentForm(forms.ModelForm):
    '''Форма подкомментария'''
    super_comment = forms.ModelChoiceField(
        queryset=SuperPostComment.objects.all(), empty_label=None,
        label='Надрубрика', required=True)

    class Meta:
        model = SubPostComment
        fields = '__all__'

class PostReportForm(forms.ModelForm):
    '''Форма жалобы на пост'''
    type_choices = [
        ('Дискриминация', 'Дискриминация'),
        ('Контент сексуального характера', 'Контент сексуального характера'),
        ('Нежелательный контент', 'Нежелательный контент'),
        ('Пропаганда наркотиков, алкоголя, табачной продукции', 'Пропаганда наркотиков, алкоголя, табачной продукции'),
        ('Демонстрация насилия', 'Демонстрация насилия')
    ]

    text = forms.CharField(label='Дополнительная информация (макс. 300 символов)',
                           widget=forms.Textarea)
    type = forms.ChoiceField(label='Тип жалобы', choices=type_choices)

    class Meta:
        model = PostReport
        fields = '__all__'
        exclude = ['created_at', 'post', 'user']

class CommentReportForm(forms.ModelForm):
    '''Форма жалобы на комментарий'''
    type_choices = [
        ('Дискриминация', 'Дискриминация'),
        ('Контент сексуального характера', 'Контент сексуального характера'),
        ('Нежелательный контент', 'Нежелательный контент'),
        ('Пропаганда наркотиков, алкоголя, табачной продукции', 'Пропаганда наркотиков, алкоголя, табачной продукции'),
        ('Демонстрация насилия', 'Демонстрация насилия')
    ]

    text = forms.CharField(label='Дополнительная информация (макс. 300 символов)',
                           widget=forms.Textarea)
    type = forms.ChoiceField(label='Тип жалобы', choices=type_choices)

    class Meta:
        model = CommentReport
        fields = '__all__'
        exclude = ['created_at', 'comment', 'user']

class PostAIForm(forms.ModelForm):
    class Meta:
        model = PostAdditionalImage
        fields = '__all__'

class CustomClearableFileInputPT(forms.ClearableFileInput):
    initial_text = ''
    template_name = 'widget/customImageFieldPost.html'

class PostCreationForm(forms.ModelForm):
    title = forms.CharField(label='Название (максимум 80 символов)')
    content = forms.CharField(widget=CKEditorWidget(), label='Содержание')
    preview = forms.ImageField(label='Превью',
            widget=CustomClearableFileInputPT(attrs={'id': 'preview'}))
    tag = forms.CharField(label='Тэги (макс 500 символов)', required=False, widget=forms.Textarea)

    is_active = forms.BooleanField(label='Открыть доступ к записи?', required=False)

    class Meta:
        model = Post
        fields = ('title', 'rubric', 'content', 'preview', 'tag', 'is_active')
        widgets = {'author': forms.HiddenInput, 'slug': forms.HiddenInput}

    def save(self, commit=True):
        instance = super().save(commit=False)
        tag_list = self.cleaned_data.get('tag', '').split(' ')

        if commit:
            instance.save()

        instance.tag.clear()

        for tag_name in list(set(tag_list)):
            tag, created = PostTag.objects.get_or_create(tag=tag_name)
            instance.tag.add(tag)

        if commit:
            instance.save()

        return instance

    def clean(self):
        super().clean()
        errors = {}
        if len(self.cleaned_data.get('tag', '').replace(' ', '')) > 500:
            errors['tag'] = ValidationError('Длина тегов не должна превышать ' +
                                            '500 символов')
        if errors:
            raise ValidationError(errors)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        print(context)
        context['tag_list'] = ' '.join(self.object.tag.values_list('tag', flat=True))
        return context

AIFormSet = inlineformset_factory(Post, PostAdditionalImage,
                                  PostAIForm, can_delete=True,
                                  extra=1, can_delete_extra=True)