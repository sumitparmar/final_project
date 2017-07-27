# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from datetime import datetime
from demoapp.forms import SignUpForm,LoginForm,PostForm
from django.contrib.auth.hashers import make_password , check_password
from demoapp.models import UserModel,SessionToken,PostModel
from imgurpython import ImgurClient
from instagram.settings import BASE_DIR

# Create your views here.
def signup_view(request):
    #business logic.
    if request.method == 'GET':
        #display signup form
        #today = datetime.now()
        form = SignUpForm()
        template_name = 'signup.html'
    elif request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            # insert data to db
            new_user = UserModel(name=name, password=make_password(password), email=email, username=username)
            new_user.save()
            return redirect("/login/")

    return render(request, template_name, {'form':form})
def login_view(request):
    response_data={}
    if request.method == 'GET':
        #to do: display login form
         form = LoginForm()
    elif request.method == 'POST':
        #to do: process form data
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            #check user exist in db or not
            user = UserModel.objects.filter(username=username).first()
            if user:
                #compare password
                if check_password(password, user.password):
                    #login successful
                    new_token = SessionToken(user=user)
                    new_token.create_token()
                    new_token.save()
                    response = redirect('/feed/')
                    response.set_cookie(key='session_token', value=new_token.session_token)
                    return response
                else:
                    #password incorrect.

                    response_data['message'] = 'Incorrect Password! Please try again!'
            
    
    response_data['form'] = form
    return render(request,'login.html', response_data)


def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('created_on')
        return render(request,'feed.html', { 'posts' : posts})
    else:
        return redirect('/login/')

def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            return session.user
        else:
            return None

def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'GET':
            form = PostForm()
        return render(request,'post.html',{'form': form})
    elif request.method == 'POST':
        form = PostForm(request.POST,request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('image')
            caption = form.cleaned_data.get('caption')
            post = PostModel(user=user, image=image,caption=caption)
            post.save()

            path = str(BASE_DIR + post.image.url)

            client = ImgurClient('4e7e0f86b1ec9cd', '826ae58b2d75e41570e839f954b5ff3de73c4514')
            post.image_url = client.upload_from_path(path,anon=True)['link']
            post.save()

            return redirect('/feed/')
        else:
            form = PostForm()
            return render(request, 'post.html',{'form': form})
    else:
        return redirect('/login/')
