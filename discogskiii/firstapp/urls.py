from django.urls import path

from . import views

app_name = "firstapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:artist>", views.artist_releases, name="artist_releases"),
    path("<str:artist>/<int:release_id>", views.release_market, name="release_market")
]