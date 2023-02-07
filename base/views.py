from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm


def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User Does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or Password doesn't exist")

    context = {
        'page': page
    }

    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')

def registerUser(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid:
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')

        else:
            messages.error(request, 'Error Registration!')

    context = {
        'form': form,
    }

    return render(request, 'base/login_register.html', context)

@login_required(login_url ='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''


    roomas = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)

    )


    topic = Topic.objects.all()
    room_count = roomas.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))


    context = {
        'rooms': roomas,
        'topic': topic,
        'room_count':room_count,
        'room_messages': room_messages,
    }
    return render(request, 'base/home.html', context)



@login_required(login_url ='login')
def room(request, pk):
    rooms = Room.objects.get(id=pk)
    room_messages = rooms.message_set.all()
    participant = rooms.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = rooms,
            body = request.POST.get('body')
        )
        rooms.participants.add(request.user)
        return redirect('room', pk=rooms.id)

    context = {
        'rooms': rooms,
        'room_messages': room_messages,
        'participants': participant,
    }
    return render(request, 'base/room.html', context)

@login_required(login_url ='login')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('home')

    context = {
        'form': form
    }
    return render(request, "base/room_form.html", context)


@login_required(login_url ='login')
def updateRoom(request,pk):

    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not allowed here")

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid:
            form.save()
            return redirect('home')


    context = {
        'form': form
    }

    return render(request, 'base/room_form.html', context)


@login_required(login_url ='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here")

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url ='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed here")

    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})
