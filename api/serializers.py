import re

from django.utils.html import strip_tags
from rest_framework import serializers

from .models import Consulta, Profissional


CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def validate_clean_text(value):
    """Rejeita HTML e controles invisíveis; SQL é parametrizado pelo ORM."""
    if value != strip_tags(value) or CONTROL_CHARS.search(value):
        raise serializers.ValidationError("Não use HTML ou caracteres de controle.")
    value = " ".join(value.split())
    if not value:
        raise serializers.ValidationError("Este campo não pode estar vazio.")
    return value


class ProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profissional
        fields = ["id", "nome_social", "profissao", "endereco", "contato", "criado_em", "atualizado_em"]
        read_only_fields = ["id", "criado_em", "atualizado_em"]

    def validate_nome_social(self, value):
        return validate_clean_text(value)

    def validate_profissao(self, value):
        return validate_clean_text(value)

    def validate_endereco(self, value):
        return validate_clean_text(value)

    def validate_contato(self, value):
        return validate_clean_text(value)


class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = ["id", "data", "profissional", "criado_em", "atualizado_em"]
        read_only_fields = ["id", "criado_em", "atualizado_em"]
