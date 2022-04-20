from django.shortcuts import render
import requests

def index(request):
    r = requests.get('http://numbersapi.com/random/')
    
    context = {'fact': r.text}
    return render(request, 'randnum/index.html', context)