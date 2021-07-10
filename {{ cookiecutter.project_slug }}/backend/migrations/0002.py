import uuid

import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("backend", "0001"),
    ]

    operations = [
        migrations.CreateModel(
            name="Item",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated", models.DateTimeField(auto_now=True, db_index=True)),
                ("name", models.TextField()),
                ("description", models.TextField()),
                (
                    "search_vector",
                    django.contrib.postgres.search.SearchVectorField(null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated", models.DateTimeField(auto_now=True, db_index=True)),
                ("full_name", models.TextField()),
                ("email", models.TextField()),
                ("hashed_password", models.TextField()),
                (
                    "search_vector",
                    django.contrib.postgres.search.SearchVectorField(null=True),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["email"], name="backend_use_email_db66b5_idx"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="backend_use_search__6cf6bf_gin"
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(fields=("email",), name="unique_email"),
        ),
        migrations.AddField(
            model_name="item",
            name="owner",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="backend.user",
            ),
        ),
        migrations.AddIndex(
            model_name="item",
            index=models.Index(
                fields=["name", "owner"], name="backend_ite_name_c0732e_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="item",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="backend_ite_search__4170f7_gin"
            ),
        ),
        migrations.AddConstraint(
            model_name="item",
            constraint=models.UniqueConstraint(
                fields=("name", "owner"), name="unique_owner_and_name"
            ),
        ),
    ]
