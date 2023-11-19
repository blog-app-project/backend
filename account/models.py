from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CASCADE
from django.urls import reverse


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), related_name='profile', on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)  # опциональное, может содержать null
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)
    blog_name = models.CharField(max_length=250, unique=True)

    # profile_image = models.ImageField(upload_to='profile_images/%Y/%m/%d', blank=True)

    def __str__(self):
        return f'Blog {self.blog_name}'

    def save(self, *args, **kwargs):
        if not self.blog_name:
            self.blog_name = self.user.username
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('user_detail', args=[self.user.username])


class Contact(models.Model):
    user_from = models.ForeignKey('auth.User', related_name='rel_from_set', on_delete=CASCADE)
    user_to = models.ForeignKey('auth.User', related_name='rel_to_set', on_delete=CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created'])
        ]
        ordering = ['-created']

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


user_model = get_user_model()
user_model.add_to_class('following',
                        models.ManyToManyField('self',
                                               through=Contact,
                                               related_name='followers',
                                               symmetrical=False))
