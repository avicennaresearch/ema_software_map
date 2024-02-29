# Generated by Django 5.0.2 on 2024-03-15 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparison', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='url',
            name='ai_summary',
            field=models.TextField(blank=True, editable=False, help_text='Content Summary (AI-Generated)', null=True),
        ),
        migrations.AddField(
            model_name='url',
            name='human_summary',
            field=models.TextField(blank=True, help_text='Content Summary (Human Generated)', null=True),
        ),
        migrations.AddField(
            model_name='url',
            name='name',
            field=models.CharField(default=None, max_length=2000, verbose_name='Resource URL'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='url',
            name='url',
            field=models.CharField(max_length=2000, verbose_name='Resource URL'),
        ),
    ]
