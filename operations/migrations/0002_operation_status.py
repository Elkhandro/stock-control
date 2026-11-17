from django.db import migrations, models


def move_legacy_statuses(apps, schema_editor):
    Operation = apps.get_model("operations", "Operation")
    Operation.objects.filter(is_cancelled=True).update(status="cancelled")
    Operation.objects.filter(is_cancelled=False).update(status="active")


class Migration(migrations.Migration):
    dependencies = [
        ("operations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="operation",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Активна"),
                    ("cancelled", "Отменена"),
                    ("completed", "Завершена"),
                ],
                db_index=True,
                default="active",
                help_text="Активна, отменена или завершена.",
                max_length=10,
                verbose_name="Статус",
            ),
        ),
        migrations.RunPython(move_legacy_statuses, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="operation",
            name="is_cancelled",
        ),
    ]
}
