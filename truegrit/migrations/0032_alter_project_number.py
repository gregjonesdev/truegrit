# Generated by Django 4.2.15 on 2024-12-20 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('truegrit', '0031_alter_project_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='number',
            field=models.CharField(max_length=255, null=True),
        ),
    ]