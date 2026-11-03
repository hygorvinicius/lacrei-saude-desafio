from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Profissional",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome_social", models.CharField(max_length=150)),
                ("profissao", models.CharField(max_length=100)),
                ("endereco", models.CharField(max_length=255)),
                ("contato", models.CharField(max_length=150)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Consulta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.DateTimeField(db_index=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                (
                    "profissional",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="consultas",
                        to="api.profissional",
                    ),
                ),
            ],
            options={"ordering": ["data", "id"]},
        ),
        migrations.AddIndex(
            model_name="consulta",
            index=models.Index(fields=["profissional", "data"], name="api_consult_profiss_270a4d_idx"),
        ),
    ]
