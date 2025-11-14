# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helios', '0006_remove_jwt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poll',
            name='shibboleth_auth'
        ),
        migrations.RemoveField(
            model_name='poll',
            name='shibboleth_constraints'
        ),
    ]
