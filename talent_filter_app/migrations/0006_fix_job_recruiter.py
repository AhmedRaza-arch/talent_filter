# Generated manually to fix migration issues

from django.db import migrations, models
import django.db.models.deletion


def make_recruiter_nullable(apps, schema_editor):
    # Get the Job model from the app registry
    Job = apps.get_model('talent_filter_app', 'Job')
    
    # Update the database schema to allow null values for recruiter
    schema_editor.execute(
        "ALTER TABLE talent_filter_app_job MODIFY recruiter_id INTEGER NULL;"
    )


class Migration(migrations.Migration):

    dependencies = [
        ('talent_filter_app', '0005_alter_job_recruiter_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='recruiter',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='jobs',
                to='talent_filter_app.recruiterprofile',
            ),
        ),
        migrations.CreateModel(
            name="JobMatchAnalysis",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("result", models.JSONField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="talent_filter_app.job",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auth.user",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
                "unique_together": {("user", "job")},
            },
        ),
    ]
