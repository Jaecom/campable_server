from django.urls import path
from . import views

urlpatterns = [
    path("convert-file", views.index, name="convert-file"),
]
