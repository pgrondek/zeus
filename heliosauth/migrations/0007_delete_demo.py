# -*- coding: utf-8 -*-


from django.db import models, migrations

from heliosauth.models import UserGroup
from zeus.models import Institution


def remove_demo(apps, schema_editor):
    try:
        institution = Institution.objects.get(name="demo")
        institution.delete()
    except Institution.DoesNotExist:
        pass

    try:
        group = UserGroup.objects.get(name="demo")
        group.delete()
    except UserGroup.DoesNotExist:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('heliosauth', '0006_add_email_to_user'),
    ]

    operations = [
        migrations.RunPython(remove_demo)
    ]
