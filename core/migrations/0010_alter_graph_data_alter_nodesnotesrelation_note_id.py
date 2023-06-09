# Generated by Django 4.2 on 2023-05-30 18:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_nodesnotesrelation_graph_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graph',
            name='data',
            field=models.TextField(default='digraph{A;B;A->B;}', verbose_name='data'),
        ),
        migrations.AlterField(
            model_name='nodesnotesrelation',
            name='note_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.note'),
        ),
    ]
