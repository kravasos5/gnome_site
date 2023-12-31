# Generated by Django 4.2.3 on 2023-11-17 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gnome_main', '0028_alter_postdislike_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Слаг'),
        ),
        migrations.AlterUniqueTogether(
            name='postviewcount',
            unique_together={('post', 'ip_address'), ('post', 'user', 'ip_address')},
        ),
    ]
