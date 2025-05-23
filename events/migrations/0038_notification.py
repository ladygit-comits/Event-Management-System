# Generated by Django 4.2.20 on 2025-03-25 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0037_alter_vendor_email_alter_vendor_groups_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
