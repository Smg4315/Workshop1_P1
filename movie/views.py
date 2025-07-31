from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    #return HttpResponse('<H1> Welcome to the Movie Reviews Home Page! </H1>')
    #return render(request, 'home.html')
    return render(request, 'home.html',  {'name':'Simón Mazo Gómez'})

def about(request):
    #return HttpResponse('<H1> Welcome to about page </H1>')
    return render(request, 'about.html')