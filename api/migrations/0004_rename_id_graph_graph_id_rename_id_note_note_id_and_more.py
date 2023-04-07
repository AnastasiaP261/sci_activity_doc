# Generated by Django 4.1.7 on 2023-04-07 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_note_graph'),
    ]

    operations = [
        migrations.RenameField(
            model_name='graph',
            old_name='id',
            new_name='graph_id',
        ),
        migrations.RenameField(
            model_name='note',
            old_name='id',
            new_name='note_id',
        ),
        migrations.RenameField(
            model_name='note',
            old_name='type',
            new_name='note_type',
        ),
        migrations.RenameField(
            model_name='research',
            old_name='id',
            new_name='rsrch_id',
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=150, verbose_name='first_name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=150, verbose_name='last_name'),
        ),
    ]