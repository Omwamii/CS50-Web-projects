from django.db import models

class Page(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    url = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title
