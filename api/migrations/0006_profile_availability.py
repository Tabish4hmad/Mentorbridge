from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_profile_address_profile_institute_profile_mobile"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="availability",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
