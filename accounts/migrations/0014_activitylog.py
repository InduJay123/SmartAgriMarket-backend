from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0013_adminprofile"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ActivityLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("actor_username", models.CharField(blank=True, max_length=150)),
                (
                    "action_type",
                    models.CharField(
                        choices=[
                            ("ADMIN_LOGIN_SUCCESS", "Admin login"),
                            ("DASHBOARD_VIEWED", "Dashboard viewed"),
                            ("USER_APPROVED", "User approved"),
                            ("USER_REJECTED", "User rejected"),
                            ("TRANSACTIONS_REPORT_GENERATED", "Transactions report generated"),
                            ("COMBINED_REPORT_GENERATED", "Combined market report generated"),
                        ],
                        max_length=64,
                    ),
                ),
                ("module", models.CharField(max_length=64)),
                ("message", models.CharField(max_length=255)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="activity_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="activitylog",
            index=models.Index(fields=["-created_at"], name="accounts_act_created_67706a_idx"),
        ),
        migrations.AddIndex(
            model_name="activitylog",
            index=models.Index(fields=["action_type"], name="accounts_act_action__186cc1_idx"),
        ),
        migrations.AddIndex(
            model_name="activitylog",
            index=models.Index(fields=["module"], name="accounts_act_module_95600c_idx"),
        ),
    ]