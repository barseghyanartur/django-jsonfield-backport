# Generated by Django 3.0.8 on 2020-07-02 08:55
import django.core.serializers.json
from django.db import migrations, models

import django_jsonfield_backport.models
import tests.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JSONModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID",
                    ),
                ),
                ("value", django_jsonfield_backport.models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name="NullableJSONModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID",
                    ),
                ),
                ("value", django_jsonfield_backport.models.JSONField(blank=True, null=True),),
                (
                    "value_custom",
                    django_jsonfield_backport.models.JSONField(
                        decoder=tests.models.CustomJSONDecoder,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                        null=True,
                    ),
                ),
            ],
        ),
    ]