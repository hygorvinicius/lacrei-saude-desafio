from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class AuthenticatedAPITestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="avaliador", password="senha-de-teste-forte-123!"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
