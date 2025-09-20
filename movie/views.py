from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie

import io
import matplotlib.pyplot as plt
import matplotlib
import urllib, base64

from openai import OpenAI
import numpy as np
import os
from dotenv import load_dotenv

# Cargar la API Key
load_dotenv('openAI.env')
client = OpenAI(api_key=os.environ.get('openai_apikey'))

# Create your views here.
def home(request):
    #return HttpResponse('<H1> Welcome to the Movie Reviews Home Page! </H1>')
    #return render(request, 'home.html')
    #return render(request, 'home.html',  {'name':'Simón Mazo Gómez'})
    searchtearm= request.GET.get('searchMovie') 
    if searchtearm:
        movies = Movie.objects.filter(title__icontains=searchtearm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm': searchtearm, 'movies': movies })


def about(request):
    #return HttpResponse('<H1> Welcome to about page </H1>')
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email': email})

def stadistics_view(request):
    matplotlib.use('Agg')

    # Movies per year
    years = Movie.objects.values_list('year', flat=True).distinct().order_by('year')
    movie_counts_by_year = {}
    for year in years:
        if year:
            movies_in_year = Movie.objects.filter(year=year)
        else:
            movies_in_year = Movie.objects.filter(year__isnull=True)
            year = "None"
        count = movies_in_year.count()
        movie_counts_by_year[year] = count
    bar_width = 0.5
    bar_positions = range(len(movie_counts_by_year))
    plt.figure(figsize=(6,4))
    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center', color='blue')
    plt.title('Number of Movies by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)
    plt.tight_layout()
    buffer_year = io.BytesIO()
    plt.savefig(buffer_year, format='png')
    buffer_year.seek(0)
    plt.close()
    image_png_year = buffer_year.getvalue()
    buffer_year.close()
    graphic_year = base64.b64encode(image_png_year).decode('utf-8')

    # Movies per genre (only first genre per movie)
    genre_counts = {}
    for movie in Movie.objects.all():
        if movie.genre:
            first_genre = movie.genre.split(',')[0].strip()
            genre_counts[first_genre] = genre_counts.get(first_genre, 0) + 1
        else:
            genre_counts['None'] = genre_counts.get('None', 0) + 1
    plt.figure(figsize=(6,4))
    plt.bar(genre_counts.keys(), genre_counts.values(), color='green')
    plt.title('Number of Movies by Genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of Movies')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buffer_genre = io.BytesIO()
    plt.savefig(buffer_genre, format='png')
    buffer_genre.seek(0)
    plt.close()
    image_png_genre = buffer_genre.getvalue()
    buffer_genre.close()
    graphic_genre = base64.b64encode(image_png_genre).decode('utf-8')

    # Renderizar la plantilla stadistics.html con ambas gráficas
    return render(request, 'stadistics.html', {'graphic_year': graphic_year, 'graphic_genre': graphic_genre})

def recommendations(request):
    result = None
    prompt = ''
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        if prompt:
            response = client.embeddings.create(
                input=[prompt],
                model="text-embedding-3-small"
            )
            prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)
            best_movie = None
            max_similarity = -1
            for movie in Movie.objects.all():
                if hasattr(movie, 'emb') and movie.emb:
                    movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                    similarity = cosine_similarity(prompt_emb, movie_emb)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_movie = movie
            result = best_movie
    return render(request, 'recommendations.html', {'result': result, 'prompt': prompt})

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))