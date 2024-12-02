from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    TYPE_USERS = (
        ('admin', 'Admin'),
        ('user', 'User')
    )
    dob = models.DateField(null=True, blank=True)
    mobile = models.CharField(max_length=10, null=True)
    type = models.CharField(max_length=10, choices=TYPE_USERS, default='user')

    class Meta:
        verbose_name_plural='UserProfile'


class LoadTest(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    url = models.URLField()
    request_count = models.PositiveIntegerField()
    time_interval = models.FloatField(help_text="Interval between requests in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    is_test = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.url} - {self.request_count} requests"

class RequestLog(models.Model):
    test = models.ForeignKey(LoadTest, on_delete=models.CASCADE)
    url = models.URLField()  # The URL that was tested
    status_code = models.IntegerField()  # Status code of the request
    timestamp = models.DateTimeField(auto_now_add=True)  # When the request was made

    def __str__(self):
        return f"{self.url} - {self.status_code} at {self.timestamp}"