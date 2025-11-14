# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helios', '0005_election_cast_consent_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poll',
            name='jwt_auth'
        ),
        migrations.RemoveField(
            model_name='poll',
            name='jwt_public_key'
        ),
        migrations.RemoveField(
            model_name='poll',
            name='jwt_issuer'
        ),
    ]
