from django.urls import path

from . import views

app_name = "firstapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("saved_markets", views.saved_markets, name="saved_markets"),
    path("artist_releases/<str:artist>", views.artist_releases, name="artist_releases"),
    path("artist_markets/<str:artist>/<int:release_id>", views.release_market, name="release_market"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]