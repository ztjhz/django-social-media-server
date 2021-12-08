from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import related


class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    timestamp = models.DateTimeField(auto_now_add=True)
    #like = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} - '{self.content}'"

class Comment(models.Model):
    comment = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - '{self.comment}'"

class Follower(models.Model):
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following", default=None)

    def __str__(self):
        return f"{self.following} -> {self.followed}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user}, {self.post}"