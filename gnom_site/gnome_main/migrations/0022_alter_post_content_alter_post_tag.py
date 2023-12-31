# Generated by Django 4.2.3 on 2023-10-02 04:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gnome_main', '0021_alter_post_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(validators=[django.core.validators.MinLengthValidator(100, 'Содержание должно быть длинной минимум в 100 символов'), django.core.validators.MinLengthValidator(limit_value=10, message='Содержание должно содержать как минимум 10 слов')], verbose_name='Содержание'),
        ),
        migrations.AlterField(
            model_name='post',
            name='tag',
            field=models.ManyToManyField(to='gnome_main.posttag', verbose_name='Тэг'),
        ),
    ]
