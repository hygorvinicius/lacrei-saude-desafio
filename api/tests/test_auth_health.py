from django.urls import reverse
from rest_framework import status

from .base import AuthenticatedAPITestCase


class AuthAndHealthTests(AuthenticatedAPITestCase):
    def test_health_publico(self):
        self.client.credentials()
        resposta = self.client.get(reverse("health"))
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data["status"], "ok")

    def test_gerar_token_com_login_valido(self):
        self.client.credentials()
        resposta = self.client.post(
            reverse("token"),
            {"username": "avaliador", "password": "senha-de-teste-forte-123!"},
            format="json",
        )
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertIn("token", resposta.data)

    def test_login_invalido(self):
        self.client.credentials()
        resposta = self.client.post(
            reverse("token"),
            {"username": "avaliador", "password": "errada"},
            format="json",
        )
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
