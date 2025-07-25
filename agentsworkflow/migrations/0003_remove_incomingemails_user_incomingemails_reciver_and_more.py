# Generated by Django 5.2.3 on 2025-06-28 16:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agentsworkflow', '0002_users_remove_outgoingemails_recipients_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incomingemails',
            name='user',
        ),
        migrations.AddField(
            model_name='incomingemails',
            name='reciver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sendings', to='agentsworkflow.users'),
        ),
        migrations.AddField(
            model_name='incomingemails',
            name='sender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incoming_emails', to='agentsworkflow.users'),
        ),
    ]
