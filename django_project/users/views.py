import logging
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProfileForm, RegisterForm
from .models import User

logger = logging.getLogger(__name__)

def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info("User %s registered", user.username)
            return redirect("profile")
        logger.warning("Failed registration attempt: %s", form.errors.as_json())
    return render(request, "users/register.html", {"form": form})

@login_required
def profile(request, username=None):
    user_obj = request.user if username is None else get_object_or_404(User, username=username)
    allowed = user_obj == request.user or request.user.friends.filter(pk=user_obj.pk).exists()
    if not allowed:
        return render(request, "users/forbidden.html", status=403)
    return render(request, "users/profile.html", {"profile_user": user_obj})

@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        logger.info("User %s updated profile", request.user.username)
        return redirect("profile")
    return render(request, "users/profile_form.html", {"form": form})

@login_required
def user_list(request):
    return render(request, "users/user_list.html", {"users": User.objects.exclude(pk=request.user.pk)})

@login_required
def add_friend(request, pk):
    friend = get_object_or_404(User, pk=pk)
    request.user.friends.add(friend)
    logger.info("User %s added friend %s", request.user.username, friend.username)
    return redirect("user_list")

@login_required
def remove_friend(request, pk):
    friend = get_object_or_404(User, pk=pk)
    request.user.friends.remove(friend)
    logger.info("User %s removed friend %s", request.user.username, friend.username)
    return redirect("user_list")
