from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Room, Topic, Message, Profile, Signup, Notes
from .forms import RoomForm, RegistrationForm, ProfileForm
import traceback


def login_page(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        done = False
        email = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=email)
        except:
            messages.error(request, "User does not exists!")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            context = {"page": page}
            return redirect("home")
        else:
            messages.error(request, "Username OR Password does not exist!")

    context = {"page": page}
    return render(request, "base/login_register.html", context)


def logout_user(request):
    logout(request)
    return redirect("home")


def register_page(request):
    form = RegistrationForm()

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occured during registration!")

    context = {"form": form}
    return render(request, "base/login_register.html", context)


def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    prof = None
    try:
        prof = Profile.objects.get(user=request.user)
        print(prof.avatar.url)
    except Exception as e:
        return redirect("update_user")

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
        "prof": prof,
    }
    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by("-created")
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    room.participants.add(request.user)
    return render(request, "base/room.html", context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    try:
        prof = Profile.objects.get(user=user)
        print(prof)
        rooms = user.room_set.all()
        room_messages = user.message_set.all()
        topics = Topic.objects.all()
        context = {
            "user": user,
            "prof": prof,
            "rooms": rooms,
            "room_messages": room_messages,
            "topics": topics,
        }
        return render(request, "base/profile.html", context)
    except prof.DoesNotExist:
        print("prof dne in profilw")
        return redirect("update_user")


@login_required(login_url="login")
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")

    context = {
        "form": form,
        "topics": topics,
    }
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here!!!")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    context = {
        "form": form,
        "topics": topics,
        "room": room,
    }
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here!!!")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    context = {"obj": room}
    return render(request, "base/delete_form.html", context)


@login_required(login_url="login")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed here!!!")

    if request.method == "POST":
        message.delete()
        return redirect("home")
    context = {"obj": message}
    return render(request, "base/delete_message.html", context)


@login_required(login_url="login")
def update_user(request):

    # user = request.user
    # try:
    #   prof = Profile.objects.get(user=user)
    #   form = ProfileForm(instance=user)

    # if request.method == 'POST':
    #     form = ProfileForm(request.POST, request.FILES, instance=user)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('user_profile', pk=user.id)

    # context = {'form': form}
    # return render(request, 'base/update_user.html', context)
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
        # Profile exists, update it
        form = ProfileForm(
            request.POST or None, request.FILES or None, instance=profile
        )
    except Profile.DoesNotExist:
        # Profile doesn't exist, create a new one
        print("prof dne in update_user")
        form = ProfileForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            if (
                "name" not in form.cleaned_data
                and "bio" not in form.cleaned_data
                and "avatar" not in form.cleaned_data
            ):
                # If the form data doesn't contain any changes to profile fields, return to profile page
                return redirect("user_profile", pk=user.id)

            # Set the user for the profile
            form.instance.user = user
            form.save()
            return redirect("user_profile", pk=user.id)

    context = {"form": form}
    return render(request, "base/update_user.html", context)


def topics_page(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics": topics}
    return render(request, "base/topics.html", context)


def activity_page(request):
    room_messages = Message.objects.all()
    context = {"room_messages": room_messages}
    return render(request, "base/activity.html", context)


def chat(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }
    return render(request, "base/chat.html", context)

###############################################################################################
def addNotes(request):
    if not request.user.is_authenticated:
        return redirect('register_page')
    user = User.objects.get(id=request.user.id)
    #signup = Signup.objects.get(user=user)
    #print(signup)
    error = ""
    if request.method == "POST":
        title = request.POST['Title']
        content = request.POST['Content']
        #print("request is post in addnotes")
        try:
            Notes.objects.create(user=request.user, Title=title, Content=content) # signup=signup,  sucess

            error = "no" 
        except Exception as e:
             # Get the traceback as a string
            tb_str = traceback.format_exc()
            print("An error occurred:", e)
            print("Traceback:\n", tb_str)
            error = "yes"
    return render(request, 'base/addNotes.html', {"error":error})

def viewNotes(request):
    if not request.user.is_authenticated:
        return redirect('register_page')
    user = User.objects.get(id=request.user.id)
    #signup = Signup.objects.get(user=user)
    notes = Notes.objects.filter(user=request.user)
    print(locals())
    return render(request, 'base/viewNotes.html', locals())

def editNotes(request,pid):
    if not request.user.is_authenticated:
        return redirect('register_page')
    notes = Notes.objects.get(id=pid)
    if request.method == "POST":
        title = request.POST['Title']
        content = request.POST['Content']

        notes.Title = title
        notes.Content = content

        try:
            notes.save()
            error = "no"
        except:
            error = "yes"
    return render(request, 'base/editNotes.html', locals())

def deleteNotes(request,pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    notes = Notes.objects.get(id=pid)
    notes.delete()
    return redirect('viewNotes')

def courses(request):
    if not request.user.is_authenticated:
        return redirect('register_page')
    error = "no"
    return render(request, 'base/courses.html')
###############################################################################################

