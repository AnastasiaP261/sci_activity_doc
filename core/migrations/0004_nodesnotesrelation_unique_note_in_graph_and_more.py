# Generated by Django 4.2 on 2023-05-16 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_note_note_id'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='nodesnotesrelation',
            constraint=models.UniqueConstraint(fields=('note_id', 'graph_id'), name='unique note in graph'),
        ),
        migrations.AddConstraint(
            model_name='nodesnotesrelation',
            constraint=models.UniqueConstraint(fields=('note_id', 'node_id'), name='unique note in node'),
        ),
    ]
