# Generated by Django 3.1.3 on 2021-03-30 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, verbose_name='名称')),
                ('related_parent', models.CharField(max_length=300, verbose_name='组织关系')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='self', to='team.team', verbose_name='上级部门')),
            ],
            options={
                'verbose_name': '分组',
                'verbose_name_plural': '分组',
                'ordering': ['related_parent'],
            },
        ),
    ]
