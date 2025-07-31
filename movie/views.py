from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie

# Create your views here.
def home(request):
    #return HttpResponse('<H1> Welcome to the Movie Reviews Home Page! </H1>')
    #return render(request, 'home.html')
    #return render(request, 'home.html',  {'name':'Simón Mazo Gómez'})
    searchtearm= request.GET.get('search') 
    movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm': searchtearm, 'movies': movies })


def about(request):
    #return HttpResponse('<H1> Welcome to about page </H1>')
    return render(request, 'about.html')