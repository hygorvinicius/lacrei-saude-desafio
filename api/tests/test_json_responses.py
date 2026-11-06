import json

from django.urls import reverse
from rest_framework import status

from .base import AuthenticatedAPITestCase


class JsonResponseTests(AuthenticatedAPITestCase):
    """Exige JSON para endpoints REST; a interface Swagger continua HTML."""

    def assert_json(self, response):
        self.assertEqual(response["Content-Type"].split(";")[0], "application/json")
        return json.loads(response.content)

    def test_profissionais_retorna_json(self):
        response = self.client.get(reverse("profissional-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", self.assert_json(response))

    def test_consultas_retorna_json(self):
        response = self.client.get(reverse("consulta-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", self.assert_json(response))

    def test_erro_validacao_retorna_json(self):
        response = self.client.post(
            reverse("profissional-list"), {"nome_social": "Teste"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profissao", self.assert_json(response))

    def test_nao_autenticado_retorna_json(self):
        self.client.credentials()
        response = self.client.get(reverse("consulta-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", self.assert_json(response))

    def test_login_retorna_json(self):
        self.client.credentials()
        response = self.client.post(
            reverse("token"),
            {"username": "avaliador", "password": "senha-de-teste-forte-123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", self.assert_json(response))

    def test_health_retorna_json(self):
        self.client.credentials()
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.assert_json(response), {"status": "ok"})

    def test_json_eh_renderer_unico_para_api(self):
        from django.conf import settings
        self.assertEqual(
            settings.REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"],
            ["rest_framework.renderers.JSONRenderer"],
        )

    def test_swagger_preservado(self):
        self.client.credentials()
        response = self.client.get(reverse("swagger-ui"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", response["Content-Type"])
