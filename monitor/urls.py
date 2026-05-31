from django.urls import path
from monitor import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/noticias", views.api_noticias, name="api_noticias"),
    path("api/metricas", views.api_metricas, name="api_metricas"),
]
