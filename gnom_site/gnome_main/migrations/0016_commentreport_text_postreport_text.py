# Generated by Django 4.2.3 on 2023-09-03 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gnome_main', '0015_postreport_commentreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentreport',
            name='text',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='postreport',
            name='text',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]