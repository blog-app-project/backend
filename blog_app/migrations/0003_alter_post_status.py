# Generated by Django 4.2.6 on 2023-11-20 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0002_alter_post_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.CharField(choices=[('DF', 'Draft'), ('MD', 'Moderated'), ('PB', 'Published')], default='DF', max_length=2),
        ),
    ]