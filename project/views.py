from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Post, Recycle_Event
import bcrypt
import requests
import urllib
import os
from datetime import date

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

# Create your views here.
def home(request):
    if request.session.get('logged_in') == True:
        return redirect('/dashboard')
    else:
        return render(request, 'home.html')

def signup(request):
    if request.method == "POST":
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        zip = request.POST.get('zip')
        password = request.POST.get('password').encode("utf8")
        confirmPass = request.POST.get('confirmPass').encode("utf8")
        inputs = [email, username, password, confirmPass, phone, zip]

        # checking if confirm password matches password   
        if (password != confirmPass):
            messages.error(request, "The passwords do not match.")
            return redirect('signup')

        for inp in inputs:
            if inp == '':
                messages.error(request, "Please fill all the boxes.")
                return redirect('signup')

        if password != '' and len(password) < 6:
            messages.error(request, "Your password must be at least 6 charecters.")
            return redirect('signup')
        

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists. If this is you, please log in.")
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "An account with this username already exists. Please pick another one.")
            return redirect('signup')

        else:
            salt = bcrypt.gensalt()
            user = User()
            user.email = email
            user.zipcode = zip
            user.username = username
            user.phone = phone
            user.password = bcrypt.hashpw(password, salt)
            user.salt = salt
            user.save()
            return redirect('login')
    else:
        if request.session.get('logged_in'):
            return redirect('dashboard')

    return render(request, 'auth/signup.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password').encode("utf8")
        inputs = [username, password]

        for inp in inputs:
            if inp == '':
                messages.error(request, "Please input all the information.")
                return redirect('login')

        

        if User.objects.filter(username=username).exists():
            saved_hashed_pass = User.objects.filter(username=username).get().password.encode("utf8")[2:-1]
            saved_salt = User.objects.filter(username=username).get().salt.encode("utf8")[2:-1]
            user  = User.objects.filter(username=username).get()
            request.session["username"] = user.username
            request.session['logged_in'] = True
        
            salted_password = bcrypt.hashpw(password, saved_salt)

            if salted_password == saved_hashed_pass:
                return redirect('dashboard')
            else:
                messages.error(request, "Your password is incorrect")
                return render(request, 'auth/login.html')
            

        else:
            messages.error(request, "An account with this username does not exist. Please sign up.")
            return redirect('login')

   
    return render(request, 'auth/login.html')


    
def logout(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        request.session["username"] = None
        request.session['logged_in'] = False
        return redirect('/')



def dashboard(request):
    if not request.session.get('logged_in'):
        return redirect('/')
    for event in Recycle_Event.objects.all():
        if date.today()>event.date_of:
            event.delete()
    if request.method == "GET":
        user=request.session.get('username')
        info = Post.objects.filter(seller__username=user)    
        events = Recycle_Event.objects.filter(organizer__username = user)    
        context={
            'details' : info,
            'events' : events
        }
        return render(request, 'dashboard.html', context)
    

def post(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "POST":       
        user = User.objects.get(username=request.session["username"])
        
        # Fetching form data
        image = request.FILES.get('image')
        title = request.POST.get('title')
        sale_type = request.POST.get('sale-type')
        description = request.POST.get('description')
        price = request.POST.get('price')
       

        if sale_type == "1":
            inputs = [image, title, sale_type, description, price]
            for inp in inputs:
                if inp == '' or inp == None:
                    messages.error(request, "Please fill all the boxes.")
                    return redirect('post')
            post = Post(image=image, title=title, sale_type=int(sale_type), description=description, 
                seller=user, price=int(price))
            post.save()
        elif sale_type == "2":
            inputs = [image, title, sale_type, description]
            for inp in inputs:
                if inp == '' or inp == None:
                    messages.error(request, "Please fill all the boxes.")
                    return redirect('post')
            post = Post(image=image, title=title, sale_type=int(sale_type), description=description, 
                seller=user)
            post.save()
        else:
            messages.error(request, "Choose a type of sale.")
            return redirect('post')
        return redirect('dashboard')
    else:
        return render(request, 'postDevice.html')


def explore(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        user = User.objects.get(username=request.session["username"])
        info = Post.objects.exclude(seller=user)
        context = {'details': info}
        return render(request, 'explore.html', context)
    
def deviceSearch(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        Searched = request.GET.get("deviceSearch")
        user = User.objects.get(username=request.session["username"])
        info = Post.objects.filter(title__contains=Searched)    
        context={'details' : info.exclude(seller=user)}
        return render(request, 'explore.html', context)
    
def typeSearch(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        Searched = request.GET.get("typeSearch")
        user = User.objects.get(username=request.session["username"])
        if int(Searched) == 0:
            info = Post.objects.all()
        else:
            info = Post.objects.filter(sale_type=int(Searched))

        context = {'details': info.exclude(seller=user)}
        return render(request, 'explore.html', context)


def show_device(request, device_id):
    user = User.objects.get(username=request.session["username"])

    device = Post.objects.get(id=device_id)
    
    context = {'device': device}
    

    return render(request, 'showDevice.html', context)

def createRecycleEvent(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "POST":       
        user = User.objects.get(username=request.session["username"])
        
        # Fetching form data
        recycler = request.POST.get('recycler')
        date = request.POST.get('date')
        zipcode = request.POST.get('zipcode')
        fee = request.POST.get('fee')
        instructions = request.POST.get('instructions')
       

        inputs = [recycler, date, zipcode, fee, instructions]
        for inp in inputs:
            if inp == '' or inp == None:
                messages.error(request, "Please fill all the boxes.")
                return redirect('createRecycleEvent')
        recycleEvent = Recycle_Event(organizer=user, recycler=recycler, date_of = date, zipcode = zipcode, fee=fee, instructions = instructions)
        recycleEvent.save()
        
        return redirect('dashboard')
    else:
        return render(request, 'recycle.html')
    

def recycle(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    for event in Recycle_Event.objects.all():
        if date.today()>event.date_of:
            event.delete()
    if request.method == "GET":
        user = User.objects.get(username=request.session["username"])
        info = Recycle_Event.objects.all()
        context = {'details': info}
        return render(request, 'showRecycleEvents.html', context)
    

def zipSearch(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        Searched = request.GET.get("zipSearch")
        user = User.objects.get(username=request.session["username"])
        info = Recycle_Event.objects.filter(zipcode=Searched)    
        context={'details' : info}
        return render(request, 'showRecycleEvents.html', context)

def delete_post(request, device_id):
    if request.method == "GET":
        device = Post.objects.get(id=device_id)
        device.delete()
        messages.error(request, "Device has been deleted!")
        return redirect("dashboard")
    
def sold(request, device_id):
    if request.method == "GET":
        device = Post.objects.get(id=device_id)
        device.delete()
        messages.error(request, "Congratulations!")
        return redirect("dashboard")
    
def delete_event(request, event_id):
    if request.method == "GET":
        event = Recycle_Event.objects.get(id=event_id)
        event.delete()
        messages.error(request, "Event has been deleted!")
        return redirect("dashboard")
    
def send_email(request):
    if request.method == "POST":
        device = Post.objects.get(id=request.POST.get('device'))
        user = User.objects.get(username=request.session["username"])
        context = {'user': user, 'seller': device.seller, 'device': device}
        message = render_to_string('email1.html', context)
        subject = f'{user.username} is interested in your device!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [device.seller.email,]
        send_mail(subject, message, email_from, recipient_list)


        messages.error(request, "The seller will be notified of your request!") 
        return redirect(f'/show_device/{device.id}/')






