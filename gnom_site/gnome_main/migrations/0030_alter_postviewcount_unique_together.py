# Generated by Django 4.2.3 on 2023-11-20 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gnome_main', '0029_alter_post_slug_alter_postviewcount_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='postviewcount',
            unique_together={('post', 'user', 'ip_address')},
        ),
    ]
