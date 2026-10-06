"""Профили доступны владельцу и друзьям, редактирование — только владельцу."""
import logging
from django.contrib import messages
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import RegistrationForm, ProfileForm
from .models import User
logger = logging.getLogger(__name__)


def register(request):
    if request.user.is_authenticated:
        return redirect('users:profile',pk=request.user.pk)
    form = RegistrationForm(request.POST if request.method=='POST' else None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            logger.info('Регистрация user_id=%s',user.pk)
            login(request,user)
            return redirect('users:profile',pk=user.pk)
        logger.warning('Ошибка регистрации: поля=%s',','.join(sorted(form.errors)))
    return render(request,'form.html',{'form':form,'title':'Создать аккаунт','submit_label':'Зарегистрироваться'})


def user_list(request):
    friends = set(request.user.friends.values_list('pk',flat=True))
    return render(request,'users/list.html',{'members':User.objects.order_by('username'),'friend_ids':friends})


def permitted_profile(request, pk):
    user = get_object_or_404(User,pk=pk)
    if user.pk != request.user.pk and not request.user.friends.filter(pk=user.pk).exists():
        raise PermissionDenied('Профили доступны только друзьям.')
    return user


def profile(request,pk):
    user = permitted_profile(request,pk)
    return render(request,'users/profile.html',{'member':user,'friends':user.friends.all()})


def edit_profile(request,pk):
    if pk != request.user.pk:
        raise PermissionDenied('Редактировать можно только свой профиль.')
    form = ProfileForm(request.POST if request.method=='POST' else None,request.FILES or None,instance=request.user)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,'Профиль обновлён.')
        return redirect('users:profile',pk=pk)
    return render(request,'form.html',{'form':form,'title':'Мой профиль'})

@require_POST
def add_friend(request,pk):
    target = get_object_or_404(User,pk=pk)
    if target.pk==request.user.pk:
        raise PermissionDenied('Нельзя добавить себя в друзья.')
    already = request.user.friends.filter(pk=target.pk).exists()
    request.user.friends.add(target)
    logger.info('Добавление друга user_id=%s friend_id=%s already=%s',request.user.pk,pk,already)
    return redirect('users:list')

@require_POST
def remove_friend(request,pk):
    target = get_object_or_404(User,pk=pk)
    request.user.friends.remove(target)
    logger.info('Удаление друга user_id=%s friend_id=%s',request.user.pk,pk)
    return redirect('users:list')


def avatar(request,pk):
    user = permitted_profile(request,pk)
    if not user.avatar:
        raise Http404('Аватар не загружен.')
    try:
        return FileResponse(user.avatar.open('rb'))
    except FileNotFoundError:
        raise Http404('Файл аватара не найден.')
