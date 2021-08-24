from django.db import models
from django.contrib.auth.models import User

class MOSSUser(models.Model):
    """ Custom user model """
    # Associated Django user
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # MOSS ID
    moss_id = models.CharField(unique=True, max_length=32)

    def __str__(self):
        """ Model to string method """
        return f"{self.user.username} ({self.user.email})"