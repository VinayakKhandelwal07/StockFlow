# Generated by Django 5.2.1 on 2025-06-03 20:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_alter_staff_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_number',
        ),
        migrations.RemoveField(
            model_name='orderproduct',
            name='price_at_time',
        ),
    ]
