# Generated by Django 4.2.3 on 2023-09-08 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gnome_main', '0018_alter_postcomment_super_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=50, verbose_name='Тэг')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
            },
        ),
        migrations.AddField(
            model_name='post',
            name='tag',
            field=models.ManyToManyField(blank=True, null=True, to='gnome_main.posttag', verbose_name='Тэг'),
        ),
    ]
