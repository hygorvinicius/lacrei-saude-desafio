from django.db import models


class Profissional(models.Model):
    nome_social = models.CharField(max_length=150)
    profissao = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255)
    contato = models.CharField(max_length=150)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.nome_social} ({self.profissao})"


class Consulta(models.Model):
    data = models.DateTimeField(db_index=True)
    profissional = models.ForeignKey(
        Profissional,
        on_delete=models.PROTECT,
        related_name="consultas",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data", "id"]
        indexes = [models.Index(fields=["profissional", "data"], name="api_consult_profiss_270a4d_idx")]

    def __str__(self):
        return f"Consulta {self.pk} - Profissional {self.profissional_id}"
