from django.urls import reverse
from rest_framework import status

from .base import AuthenticatedAPITestCase
from api.models import Profissional


class ProfissionalAPITests(AuthenticatedAPITestCase):
    def sample_data(self):
        return {
            "nome_social": "Alex Oliveira",
            "profissao": "Psicologia",
            "endereco": "Rua das Flores, 10",
            "contato": "alex@example.com",
        }

    def test_crud_completo(self):
        resposta = self.client.post(reverse("profissional-list"), self.sample_data(), format="json")
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        pk = resposta.data["id"]

        resposta = self.client.get(reverse("profissional-list"))
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data["count"], 1)

        url = reverse("profissional-detail", args=[pk])
        resposta = self.client.get(url)
        self.assertEqual(resposta.data["nome_social"], "Alex Oliveira")

        resposta = self.client.patch(url, {"profissao": "Enfermagem"}, format="json")
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data["profissao"], "Enfermagem")

        resposta = self.client.delete(url)
        self.assertEqual(resposta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Profissional.objects.count(), 0)

    def test_requer_autenticacao(self):
        self.client.credentials()
        resposta = self.client.get(reverse("profissional-list"))
        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_campos_obrigatorios(self):
        resposta = self.client.post(reverse("profissional-list"), {"nome_social": "Alex"}, format="json")
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profissao", resposta.data)

    def test_rejeita_html(self):
        dados = self.sample_data()
        dados["nome_social"] = "<script>alert(1)</script>"
        resposta = self.client.post(reverse("profissional-list"), dados, format="json")
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Profissional.objects.count(), 0)

    def test_sql_injection_tratada_como_texto(self):
        dados = self.sample_data()
        dados["nome_social"] = "x'; DROP TABLE api_profissional; --"
        resposta = self.client.post(reverse("profissional-list"), dados, format="json")
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profissional.objects.count(), 1)

    def test_id_inexistente(self):
        resposta = self.client.get(reverse("profissional-detail", args=[99999]))
        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)
