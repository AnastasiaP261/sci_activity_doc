# Generated by Django 4.2 on 2023-06-08 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('latex2html', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='remakeitem',
            name='is_head',
            field=models.BooleanField(default=True, help_text='Это значение равно True только у самостоятельных тегов, например, у тега itemize, но не у тега item'),
            preserve_default=False,
        ),
    ]
