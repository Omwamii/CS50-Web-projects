from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from model_utils import FieldTracker
from django.utils.text import slugify

def generate_unique_filename(instance, filename):
    """Generate a unique filename for the uploaded file based on the user's username."""
    username = instance.username
    _ , extension = filename.split('.')
    new_filename = f"{slugify(username)}.{extension}"
    return f"profile_pics/{new_filename}"  # Save in a 'profile_pics' folder

class User(AbstractUser):
    following = models.ManyToManyField('self', related_name='followers', symmetrical=False, blank=True)
    profile_pic = models.ImageField(upload_to=generate_unique_filename, blank=True, null=True)

class Post(models.Model):
    ''' implement posts model '''
    poster = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now, null=False)
    liked_by = models.ManyToManyField(User, related_name='likes')
    text = models.TextField()
    posted_by = models.CharField(max_length=255, null=True)
    edited = models.BooleanField(default=False)
    text_tracker = FieldTracker(fields=['text'])  # track if post text changed, only then change time
    
    def __str__(self):
        return f"Post by {self.poster.username} at {self.time}"

    def save(self, *args, **kwargs):
        # Set the posted_by field before saving the object
        self.posted_by = self.poster.username
        if self.text_tracker.changed():
            self.time = timezone.now()
        super().save(*args, **kwargs)
