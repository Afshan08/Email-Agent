# Generated by Django 5.2.3 on 2025-07-05 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_googleaccount_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='googleaccount',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
