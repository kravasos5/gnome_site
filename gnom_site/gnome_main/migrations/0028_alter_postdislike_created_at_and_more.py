# Generated by Django 4.2.3 on 2023-11-09 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gnome_main', '0027_postdislike_created_at_postfavourite_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postdislike',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата добавления'),
        ),
        migrations.AlterField(
            model_name='postfavourite',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата добавления'),
        ),
        migrations.AlterField(
            model_name='postlike',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата добавления'),
        ),
    ]
