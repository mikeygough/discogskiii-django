from django.urls import path

from . import views

app_name = "firstapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:artist>", views.amarkets, name="amarkets"),
    path("<str:artist>/<int:release_id>", views.release_market, name="release_market")
]