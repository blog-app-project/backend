from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)  # опциональное, может содержать null
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)
    # profile_image = models.ImageField(upload_to='profile_images/%Y/%m/%d', blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'
