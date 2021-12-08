
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("get_posts/<int:count>", views.get_posts, name="get_posts"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("edit", views.edit, name="edit"),
    path("like", views.like, name="like")
]
