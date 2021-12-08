from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

import json
from .models import User, Post, Comment, Follower, Like


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url='login')
def post(request):
    if request.method != "POST":
        return JsonResponse({"messsage": "Request must be POST"}, status=401)

    if not request.user.is_authenticated:
        return JsonResponse({"message": "You must be logged in to post!"}, status=401)
    data = json.loads(request.body)
    content = data.get("content")
    user = request.user

    if content == "":
        return JsonResponse({"message": "Post cannot be empty!"}, status=400)

    new_post = Post(content=content, user=user)
    new_post.save()

    return JsonResponse({"message": "Posted successfully"}, status=201)

def get_posts(request, count):
    end = int(count)
    start = end - 10
    
    posts_objects = Post.objects.all().order_by("timestamp")[start:end]
    posts = {"posts": []}
    for post_object in posts_objects:
        content = post_object.content
        user = post_object.user
        timestamp = post_object.timestamp.strftime("%B %d, %Y, %I:%M %p")
        like = len(post_object.likes.all())
        liked = False
        if request.user.is_authenticated and len(post_object.likes.filter(user=request.user)) > 0:
            liked = True

        posts["posts"].insert(0, {"content": content, "author": user.username, "timestamp": timestamp, "like": like, 
                                  "author_id": user.id, "viewer_id": request.user.id, "post_id": post_object.id, "liked": liked})

    return JsonResponse(posts)

def profile(request, user_id):
    user = User.objects.get(pk=int(user_id))
    username = user.username
    followers = user.followers.all()
    posts = user.posts.all()
    followed = False
    if request.user.is_authenticated:
        followed = len(followers.filter(following=request.user)) == 1
    liked = False;
    p = []
    for post in reversed(posts):
        if request.user.is_authenticated:
            liked = len(post.likes.filter(user=request.user)) == 1
        temp = {}
        temp["username"] = post.user.username
        temp["content"] = post.content
        temp["timestamp"] = post.timestamp
        temp["like"] = len(post.likes.all())
        temp["liked"] = liked
        temp["post_id"] = post.id
        temp["post_user_id"] = post.user.id
        p.append(temp)

    return render(request, "network/profile.html", {
        "username": username,
        "follower_count": len(followers),
        "posts": p,
        "post_user_id": posts[0].user.id,
        "followed": followed
    })

@login_required(login_url='login')
def follow(request):
    if request.method != "POST":
        return JsonResponse({"messsage": "Request must be POST"}, status=401)

    data = json.loads(request.body)
    t = data.get("type")

    if t != "follow" and t != "unfollow":
        return JsonResponse({"messsage": "Incorrect follow type"}, status=401)

    followed = User.objects.get(pk=data.get("user_id"))
    response = {}
    if t == "follow":
        follower = Follower(following=request.user, followed=followed)
        follower.save()
        response["new_type"] = "unfollow"
    else:
        follower = Follower.objects.get(following=request.user, followed=followed)
        follower.delete()
        response["new_type"] = "follow"
    response["follower_count"] = len(followed.followers.all())
    response["message"] = f"{t.capitalize()}ed succesfully"
    return JsonResponse(response)

@login_required(login_url='login')
def following(request):
    following = request.user.following.all()
    all_posts = []
    for i in following:
        user = i.followed
        posts = user.posts.all()
        for post in posts:
            temp = {}
            temp["username"] = post.user.username
            temp["content"] = post.content
            temp["timestamp"] = post.timestamp
            temp["like"] = len(post.likes.all())
            temp["liked"] = len(post.likes.filter(user=request.user)) == 1
            temp["post_id"] = post.id
            temp["post_user_id"] = posts[0].user.id
            all_posts.append(temp)

    return render(request, 'network/following.html', {
        "posts": sorted(all_posts, key=lambda x: x["timestamp"], reverse=True)
    })

@login_required(login_url='login')
def edit(request):
    if request.method != "POST":
        return JsonResponse({"messsage": "Request must be POST", "status": "401"}, status=401)
    
    data = json.loads(request.body)
    post_id = data.get("post_id")
    content = data.get("content")
    post = Post.objects.get(pk=post_id)
    if post.user != request.user:
        return JsonResponse({"message": "You are not authorised to edit the post!", "status": "401"}, status=401)
    post.content = content
    post.timestamp = timezone.now()
    post.save()

    return JsonResponse({"message": "Post edited successfully", "status": "200"}, status=200)

def like(request):
    if request.method != "POST":
        return JsonResponse({"messsage": "Request must be POST", "status": "401"}, status=401)
    
    if not request.user.is_authenticated:
        return JsonResponse({"messsage": "Must be logged in to like!", "status": "403"}, status=403)

    data = json.loads(request.body)
    post = Post.objects.get(pk=int(data.get("post_id")))
    user = request.user
    t = data.get("liked")
    response = {}

    if t == "false":
        new_like = Like(post=post, user=user)
        new_like.save()
        response["message"] = "Liked successfully!"
        response["liked"] = "true"
    elif t == "true":
        Like.objects.get(post=post, user=user).delete()
        response["message"] = "Unliked successfully!"
        response["liked"] = "false"
    
    response["likes"] = len(post.likes.all())

    return JsonResponse(response, status=200)