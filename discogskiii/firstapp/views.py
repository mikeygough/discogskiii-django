# imports
from django.shortcuts import render


artist_markets = [
    "Sun Ra",
    "John Coltrane",
    "Miles Davis",
    "Alice Coltrane"
]

# Create your views here.
def index(request):
    return render(request, "firstapp/index.html", {
        "artist_markets": artist_markets
    })

def amarkets(request, artist):
    return render(request, "firstapp/artist_markets.html", {
        "artist": artist
    })