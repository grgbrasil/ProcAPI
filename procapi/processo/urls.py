# -*- coding: utf-8 -*-


from django.conf.urls import url
from rest_framework_extensions.routers import ExtendedSimpleRouter

from . import views

router = ExtendedSimpleRouter()
(
    router.register(r'processos', views.ProcessoViewSet, base_name='processo')
        .register(
            r'eventos', views.EventoViewSet, base_name='processos-evento',
            parents_query_lookups=['processo']),
)
urlpatterns = router.urls

urlpatterns += [
    url(r'^processos/(?P<parent_lookup_processo>[^/.]+)/partes/$', views.ParteListAPIView.as_view(), name='processos-partes-list')
]
