# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helios', '0009_remove_sms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='department_limit',
            field=models.CharField(max_length=500),
        )
    ]
