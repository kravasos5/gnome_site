from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

# from .apps import user_registered
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
    super_rubric = forms.ModelChoiceField(
        queryset=SuperRubric.objects.all(), empty_label=None,
        label='Надрубрика', required=True)

    class Meta:
        model = SubRubric
        fields = '__all__'

class SubPostCommentForm(forms.ModelForm):
    super_comment = forms.ModelChoiceField(
        queryset=SuperPostComment.objects.all(), empty_label=None,
        label='Надрубрика', required=True)

    class Meta:
        model = SubPostComment
        fields = '__all__'