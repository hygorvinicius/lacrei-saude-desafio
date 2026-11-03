from django.contrib import admin
from .models import Consulta, Profissional


@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ("id", "nome_social", "profissao", "contato")
    search_fields = ("nome_social", "profissao")


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "profissional")
    list_filter = ("data",)
