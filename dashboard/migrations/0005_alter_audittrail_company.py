# Generated by Django 5.2.1 on 2025-07-10 09:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_product_added_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audittrail',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.company'),
        ),
    ]
