# Generated by Django 3.1 on 2020-12-03 22:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('document', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='signaturestorage',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user.user', verbose_name='填写人'),
        ),
        migrations.AddField(
            model_name='docxinit',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user.user', verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='contentstorage',
            name='docx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='document.docxinit', verbose_name='模板'),
        ),
        migrations.AddField(
            model_name='contentstorage',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user.user', verbose_name='填写人'),
        ),
    ]