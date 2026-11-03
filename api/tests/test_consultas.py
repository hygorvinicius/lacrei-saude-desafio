from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from .base import AuthenticatedAPITestCase
from api.models import Consulta, Profissional


class ConsultaAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.profissional = Profissional.objects.create(
            nome_social="Maria Souza",
            profissao="Medicina",
            endereco="Avenida Brasil, 123",
            contato="maria@example.com",
        )
        self.data = (timezone.now() + timedelta(days=1)).isoformat()

    def test_crud_e_filtro_profissional(self):
        url_lista = reverse("consulta-list")
        resposta = self.client.post(
            url_lista,
            {"data": self.data, "profissional": self.profissional.id},
            format="json",
        )
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        pk = resposta.data["id"]

        resposta = self.client.get(url_lista, {"profissional_id": self.profissional.id})
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data["count"], 1)

        resposta = self.client.get(url_lista, {"profissional_id": self.profissional.id + 999})
        self.assertEqual(resposta.data["count"], 0)

        detalhe = reverse("consulta-detail", args=[pk])
        self.assertEqual(self.client.get(detalhe).status_code, status.HTTP_200_OK)
        resposta = self.client.patch(detalhe, {"data": self.data}, format="json")
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.delete(detalhe).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Consulta.objects.count(), 0)

    def test_profissional_inexistente_retorna_400(self):
        resposta = self.client.post(
            reverse("consulta-list"), {"data": self.data, "profissional": 999999},
            format="json",
        )
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejeita_data_invalida(self):
        resposta = self.client.post(
            reverse("consulta-list"),
            {"data": "não-é-data", "profissional": self.profissional.pk},
            format="json",
        )
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filtro_id_invalido_retorna_400(self):
        resposta = self.client.get(reverse("consulta-list"), {"profissional_id": "1 OR 1=1"})
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_protecao_contra_exclusao_de_profissional_com_consulta(self):
        Consulta.objects.create(data=timezone.now(), profissional=self.profissional)
        resposta = self.client.delete(reverse("profissional-detail", args=[self.profissional.pk]))
        self.assertEqual(resposta.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Profissional.objects.filter(pk=self.profissional.pk).exists())

    def test_requer_autenticacao(self):
        self.client.credentials()
        resposta = self.client.get(reverse("consulta-list"))
        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)
