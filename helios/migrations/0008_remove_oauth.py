# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helios', '0007_remove_shibboleth'),
    ]

    operations = [
        migrations.RemoveField(model_name='poll', name='oauth2_thirdparty'),
        migrations.RemoveField(model_name='poll', name='oauth2_type'),
        migrations.RemoveField(model_name='poll', name='oauth2_client_type'),
        migrations.RemoveField(model_name='poll', name='oauth2_client_id'),
        migrations.RemoveField(model_name='poll', name='oauth2_client_secret'),
        migrations.RemoveField(model_name='poll', name='oauth2_code_url'),
        migrations.RemoveField(model_name='poll', name='oauth2_exchange_url'),
        migrations.RemoveField(model_name='poll', name='oauth2_confirmation_url'),
        migrations.RemoveField(model_name='poll', name='oauth2_extra'),
    ]
