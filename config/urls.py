# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework_swagger.views import get_swagger_view

from procapi.processo import views

schema_view = get_swagger_view(title='ProcApi')

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^admin/', admin.site.urls),

    # Docs Api
    url(r'^$', schema_view),

    # Include Processo api urls
    url(r'^api/v1/', include(
        'procapi.processo.urls', namespace='api-processo')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
