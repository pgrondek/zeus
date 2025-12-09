from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('helios', '0010_allow_uneven_quota'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='new_droop',
            field=models.BooleanField(default=False),
        )
    ]
