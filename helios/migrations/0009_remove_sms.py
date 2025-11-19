# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helios', '0008_remove_oauth'),
    ]

    operations = [
        migrations.RemoveField(model_name='voter', name='last_sms_send_at'),
        migrations.RemoveField(model_name='voter', name='last_sms_code'),
        migrations.RemoveField(model_name='voter', name='last_sms_status'),
        migrations.RemoveField(model_name='election', name='sms_api_enabled'),
        migrations.RemoveField(model_name='election', name='sms_data'),
    ]
