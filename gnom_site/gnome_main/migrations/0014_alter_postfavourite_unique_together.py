# Generated by Django 4.2.3 on 2023-08-30 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gnome_main', '0013_alter_postdislike_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='postfavourite',
            unique_together={('post', 'user')},
        ),
    ]