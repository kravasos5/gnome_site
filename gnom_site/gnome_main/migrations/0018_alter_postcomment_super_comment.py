# Generated by Django 4.2.3 on 2023-09-06 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gnome_main', '0017_postcomment_is_changed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcomment',
            name='super_comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gnome_main.superpostcomment', verbose_name='Надкомментарий'),
        ),
    ]