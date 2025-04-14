from django.db import migrations

def create_default_manager(apps, schema_editor):
    User = apps.get_model('smartlib_api', 'User')
    if not User.objects.filter(user_id=1).exists():
        User.objects.create(user_name="user_name",
                email="email@gmail.com")
    Manager = apps.get_model('smartlib_api', 'Manager')
    # Check if Manager with ID 2 exists
    if not Manager.objects.filter(manager_id=2).exists():
        Manager.objects.create(manager_id=2, user_id=1)

class Migration(migrations.Migration):

    dependencies = [
        ('smartlib_api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_manager),
    ]
