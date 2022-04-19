# Generated by Django 4.0.4 on 2022-04-19 13:17

from django.db import migrations, models
import taskman.validators


class Migration(migrations.Migration):

    dependencies = [
        ('taskman', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.CharField(blank=True, max_length=2048, null=True, validators=[taskman.validators.avatar_validator]),
        ),
    ]