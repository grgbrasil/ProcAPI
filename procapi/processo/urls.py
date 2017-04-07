# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework_extensions.routers import ExtendedSimpleRouter

from . import views

router = ExtendedSimpleRouter()
(
    router.register(
        r'processos',
        views.ProcessoViewSet,
        base_name='processo'
    )
)

urlpatterns = router.urls
