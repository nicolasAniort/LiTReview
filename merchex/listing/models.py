from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="media/", null=True, blank=True)
    visibility = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    visibility = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)


class UserFollows(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following_users"
    )
    followed_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers_users"
    )


class Subscription(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following_subscriptions"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers_subscriptions"
    )


class Meta:
    unique_together = ("user", "followed_user")
