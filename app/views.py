# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
import os
import time

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import Error
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.encoding import smart_str


@login_required(login_url="/login/")
def index(request):
    return HttpResponseRedirect("/patch")
    #return render(request, "index.html")


@login_required(login_url="/login/")
def update_profile(request):
    context = {"page": "profile"}

    try:
        username = request.POST['username']
    except KeyError:
        return HttpResponse(loader.get_template("pages/error-404.html").render(context, request))

    user = request.user
    user.username = username
    user.save()

    template = loader.get_template("pages/page-user.html")
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login/")
def change_password(request):
    context = {"page": "profile"}

    try:
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
    except KeyError:
        return HttpResponse(loader.get_template("pages/error-404.html").render(context, request))

    if password != password_confirm:
        context['error'] = "Password doesn't match"
    elif len(password) < 8:
        context['error'] = "Password must contain 8 letters"
    else:
        user = request.user
        user.set_password(password)
        user.save()
        context['message'] = "Password changed"

    print(context)

    template = loader.get_template("pages/page-user.html")
    return HttpResponse(template.render(context, request))


@login_required(login_url='/login')
def patch(request):
    context = {"page": "patch"}

    if not os.path.exists("upload/patch.exe"):
        context['exist'] = False
    else:
        context['exist'] = True
        update_time = os.path.getmtime("upload/patch.exe")
        context['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(update_time))

    template = loader.get_template("pages/patch.html")
    return HttpResponse(template.render(context, request))


def download_patch(request):
    if not request.user.is_authenticated:
        try:
            username = request.GET['username']
            password = request.GET['password']
        except KeyError:
            return HttpResponse("No credential given")

        print("Username", username)
        print('Password', password)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse("User not found")

        if not check_password(password, user.password):
            return HttpResponse("Credential not correct")

    if not os.path.exists("upload/patch.exe"):
        return HttpResponse("Patch not exists")

    with open("upload/patch.exe", 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=RunningWin2.exe'
        response['X-Sendfile'] = smart_str("upload/patch.exe")
    return response


@login_required(login_url='/login')
def upload_patch(request):
    file = request.FILES['patch_file']
    print("Upload File", file)
    with open('upload/patch.exe', 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return HttpResponseRedirect("/patch")


@login_required(login_url='/login')
def manage_user(request):
    context = {"page": "usermng"}
    context['user_list'] = User.objects.filter(is_superuser=0)
    template = loader.get_template("pages/manage-user.html")
    return HttpResponse(template.render(context, request))


@login_required(login_url='/login')
def remove_user(request):
    user = request.user

    if user.is_superuser != 1:
        return HttpResponse("Not SuperUser")

    try:
        user_id = request.POST['userId']
        user_id = int(user_id)
    except:
        return HttpResponse("Parameter error")

    try:
        r_user = User.objects.get(id=user_id)
        r_user.delete()
    except User.DoesNotExist:
        return HttpResponse("User not exist")

    return HttpResponse("Success")


@login_required(login_url='/login')
def enable_user(request):
    user = request.user

    if user.is_superuser != 1:
        return HttpResponse("Not SuperUser")

    try:
        user_id = request.POST['userId']
        user_id = int(user_id)
    except:
        return HttpResponse("Parameter error")

    try:
        r_user = User.objects.get(id=user_id)
        r_user.is_active = 1
        r_user.save()
    except User.DoesNotExist:
        return HttpResponse("User not exist")

    return HttpResponse("Success")


@login_required(login_url='/login')
def disable_user(request):
    user = request.user

    if user.is_superuser != 1:
        return HttpResponse("Not SuperUser")

    try:
        user_id = request.POST['userId']
        user_id = int(user_id)
    except:
        return HttpResponse("Parameter error")

    try:
        r_user = User.objects.get(id=user_id)
        r_user.is_active = 0
        r_user.save()
    except User.DoesNotExist:
        return HttpResponse("User not exist")

    return HttpResponse("Success")


@login_required(login_url='/login')
def add_user(request):
    user = request.user

    if user.is_superuser != 1:
        return HttpResponse("Not SuperUser")

    try:
        username = request.POST['username']
        password = request.POST['password']
    except:
        return HttpResponse("Parameter error")

    if "" == username or "" == password:
        return HttpResponse("Empty string")

    try:
        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()
    except Error as ex:
        return HttpResponse("Can not create user")

    return JsonResponse({
        "Success": True,
        "id": user.id,
    })


@login_required(login_url="/login/")
def pages(request):
    context = {"page": "profile"}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        print("Template Path", load_template)
        template = loader.get_template('pages/' + load_template)
        print("Template Loaded")
        return HttpResponse(template.render(context, request))

    except:

        template = loader.get_template('pages/error-404.html')
        return HttpResponse(template.render(context, request))
