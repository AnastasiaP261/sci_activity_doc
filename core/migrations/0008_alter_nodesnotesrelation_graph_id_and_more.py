# Generated by Django 4.2 on 2023-05-20 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_nodesnotesrelation_graph_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nodesnotesrelation',
            name='graph_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.graph'),
        ),
        migrations.AlterField(
            model_name='nodesnotesrelation',
            name='note_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.note'),
        ),
    ]
