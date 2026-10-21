from django.urls import path

# .venv\Scripts\Activate.ps1

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("empezar/", views.empezar, name="empezar"),
    path("disparar/", views.disparar, name="disparar"),
    path("rendirse/", views.rendirse, name="rendirse"),
    path("limpiar/", views.limpiar, name="limpiar"),
]