from rest_framework.routers import DefaultRouter
from .views import ConsultaViewSet, ProfissionalViewSet

router = DefaultRouter()
router.register(r"profissionais", ProfissionalViewSet, basename="profissional")
router.register(r"consultas", ConsultaViewSet, basename="consulta")
urlpatterns = router.urls
