from django.urls import path, include
from rest_framework.routers import DefaultRouter
from gestion.views.perfil import PerfilViewSet
from gestion.views.cliente import  ClienteViewSet
from gestion.views.credito import  CreditoViewSet
from gestion.views.cuota import CuotaViewSet
from gestion.views.user import UserViewSet
from gestion.views.cobro import CobroViewSet
from gestion.views.gasto import GastoViewSet

# Configuración del router
router = DefaultRouter()

router.register(r'perfiles', PerfilViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'creditos', CreditoViewSet)
router.register(r'cuotas', CuotaViewSet)
router.register(r'user',UserViewSet)
router.register(r'cobro',CobroViewSet)
router.register(r'gastos',GastoViewSet)
urlpatterns = [
    path('', include(router.urls)),
]
