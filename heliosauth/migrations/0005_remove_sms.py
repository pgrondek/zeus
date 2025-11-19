# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heliosauth', '0004_sms_data'),
    ]

    operations = [
        migrations.RemoveField(model_name='user', name='sms_data'),
        migrations.DeleteModel(
            name='SMSBackendData'
        )
    ]
