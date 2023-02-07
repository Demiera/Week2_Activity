from django.shortcuts import render
from django.http import HttpResponse
from .models import Room


def home(request):
    roomas = Room.objects.all()
    context = {
        'rooms' : roomas
    }
    return render(request, 'base/home.html', context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    context = {
        'rooms': room,
    }
    return render(request, 'base/room.html', context)

