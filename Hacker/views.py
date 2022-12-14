from multiprocessing import context
import profile 
from pydoc_data.topics import topics
from telnetlib import AUTHENTICATION
from urllib import request
from django.shortcuts import render,redirect
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
from .models import Message, Room
from .forms import RoomForm, ProjectForm, ReviewForm
from .models import Topic 
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .models import Project, Tag
from django.contrib import admin
from .utils import searchProjects,paginateProjects
from django.db.models import Q
from users.decorators import unauthenticated_user,allowed_users,admin_only
from django.contrib.auth.models import Group



# @unauthenticated_user
# def registerPage(request):
#     form =  UserCreationForm()

#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.username = user.username.lower()
#             user.save()
#             # login(request,user)
#             return  redirect ('home')
#         else: 
#             messages.error(request, 'An error occured during registration, Please check all fields supplied credinetials.')

#     return render (request, 'login_register.html', {'form':form})

def index(request):
    
    print(request.user)
    return render(request, 'index.html')
    

# Addws for the extra messagesvTrainer room 

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def communicate(request):
    #Query for room database 
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__contains = q) |
        Q(name__contains=q)  |
        Q(description__contains=q)
    )

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context ={'rooms':rooms, 'topics':topics,
    'room_count': room_count, 'room_messsages': room_messages }
    return render( request, 'communicate.html', context)
@login_required(login_url='login')
#Primary key added to distinguish between the rooms. 
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    patricipants = room.participants.all()


    if request.method == 'POST':
        message = Message.objects.create(
        user=request.user,
        room=room,
        body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect ('room', pk = room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants':patricipants }
    return render( request, 'room.html', context )

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('communicate')

    context = {'form':form}
    return render(request, 'room_form.html',context)



@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(request.POST,request.FILES, instance=room)

    context = {'form':form}
    return render (request, 'room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get (id=pk)
    context = {'room':room}
    if request.method == 'POST':
        room.delete()
        return redirect('communicate')
    return render(request, 'delete_template.html',context )



@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get (id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed to this room')

    if request.method == 'POST':
        message.delete()
        return redirect('communicate')
    return render(request, 'delete_template.html',{'obj':message} )

#  For different Project 
# @login_required(login_url='login')
# @unauthenticated_user


def projects(request):  
   projects, search_query = searchProjects(request)
   custom_range, projects = paginateProjects(request,projects,3)

   context = {'projects':projects, 'search_query':search_query,  'custom_range':custom_range}
   return render (request, 'projects.html', context)


# @login_required(login_url='login')

def project(request,pk):
    projectObj = Project.objects.get(id=pk)
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        review = form.save(commit = False)
        review.project = projectObj
        review.owner = request.user.profile
        review.save()

        projectObj.getVoteCount

        # update  project vote count 
        messages.success(request, 'Your review was sucessfully submitted')
        return redirect('project' ,pk = projectObj.id)


    return render (request, 'single.project.html', {'project': projectObj,'form':form})
    
@login_required(login_url='login')
def createProject(request):
    profile = request.user.profile
    form = ProjectForm()

    if request.method == 'POST':
        newtags = request.POST.get('newtags').replace(','," ").split()
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit = False)
            project.owner = profile
            project.save()
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name = tag )
                project.tags.add(tag)
            return redirect('account')



    context = {'form':form}
    return render(request, "project_form.html", context)


def updateProject(request,pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    form = ProjectForm(instance = project)

    if request.method == 'POST':
        newtags = request.POST.get('newtags').replace(','," ").split()

        form = ProjectForm(request.POST, request.FILES, instance = project )
        if form.is_valid():
            project = form.save()
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name = tag )
                project.tags.add(tag)
            return redirect('account')



    context = {'form':form, 'project':project}
    return render(request, "project_form.html", context)





def deleteProject(request,pk):
    profile = request.user.profile
    project = profile.project_set.get (id = pk)
    if request.method == 'POST':
        project.delete()
        return redirect(projects)

    context = {'object': project }
    return render(request, 'delete_template.html', context)




