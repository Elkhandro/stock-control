from django.db import migrations


def create_warehouse_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    group, _ = Group.objects.get_or_create(name="Warehouse Operators")
    allowed = {
        "product": ("view_product", "add_product", "change_product"),
        "operation": ("view_operation", "add_operation", "change_operation"),
    }
    permissions = Permission.objects.filter(
        content_type__app_label__in=("products", "operations"),
        codename__in=[code for codes in allowed.values() for code in codes],
    )
    group.permissions.set(permissions)


class Migration(migrations.Migration):
    dependencies = [
        ("operations", "0002_operation_status"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_warehouse_group, migrations.RunPython.noop),
    ]
