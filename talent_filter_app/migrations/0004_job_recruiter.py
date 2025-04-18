# Generated by Django 5.1.6 on 2025-04-13 14:37

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "talent_filter_app",
            "0003_company_location_rename_title_job_job_title_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="recruiter",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="jobs",
                null=True,
                blank=True,
                to="talent_filter_app.recruiterprofile",
            ),
        ),
    ]
