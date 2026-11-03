from django.db import DatabaseError, connection
from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, extend_schema

from .models import Consulta, Profissional
from .serializers import ConsultaSerializer, ProfissionalSerializer


class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_class = ProfissionalSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": "O profissional possui consultas; remova-as antes."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConsultaViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultaSerializer
    queryset = Consulta.objects.select_related("profissional").all()

    @extend_schema(parameters=[
        OpenApiParameter(name="profissional_id", type=int, description="Filtra consultas pelo ID do profissional"),
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        raw_id = self.request.query_params.get("profissional_id")
        if raw_id is None:
            return queryset
        if not raw_id.isdecimal() or int(raw_id) <= 0:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"profissional_id": "Informe um ID inteiro positivo."})
        return queryset.filter(profissional_id=int(raw_id))


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except DatabaseError:
            return Response({"status": "unhealthy"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"status": "ok"})


class LimitedObtainAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"
