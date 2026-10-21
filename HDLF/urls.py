from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("empezar/", views.empezar, name="empezar"),
    path("disparar/", views.disparar, name="disparar"),
]