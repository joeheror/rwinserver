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
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.utils.encoding import smart_str

from app.config import MyConfig


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
    context = {"page": "patch", "patches": []}

    for key in MyConfig.patch_list:
        data = MyConfig.patch_list[key]
        data["url"] = key

        file_path = MyConfig.patch_path + data["file_name"]

        if not os.path.exists(file_path):
            data["last_update"] = ""
        else:
            data["last_update"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))

        context["patches"].append(data)

    template = loader.get_template("pages/patch.html")
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login")
def upload_page(request, service):
    context = {"patge": "patch"}

    if not request.user.is_superuser:
        context["error"] = "Only administrator can upload"
        return HttpResponse(loader.get_template("pages/patch.html").render(context, request))

    context["service"] = service
    return HttpResponse(loader.get_template("pages/upload-patch.html").render(context, request))


def download_patch(request, service):
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

    if service not in MyConfig.patch_list.keys():
        return HttpResponse("Service not found")

    file_path = MyConfig.patch_path + MyConfig.patch_list[service]["file_name"]

    if not os.path.exists(file_path):
        return HttpResponse("Patch not exists")

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=' + MyConfig.patch_list[service]["file_name"]
    return response


@login_required(login_url="/login")
def do_upload(request):

    if not request.user.is_superuser:
        return HttpResponseBadRequest("")

    service = request.POST['service']
    file = request.FILES['src_file']

    if service not in MyConfig.patch_list.keys():
        return HttpResponseBadRequest("")

    file_path = MyConfig.patch_path + MyConfig.patch_list[service]["file_name"]

    with open( file_path, 'wb+') as dest:
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
