from django.db import models

class Post(models.Model):
    rating = models.IntegerField(default=0)
    link = models.URLField(primary_key=True)
    title = models.CharField(max_length=200)
    image_src = models.URLField(blank=True, default='')
    author = models.CharField(max_length=100)
    section = models.CharField(max_length=50)
    date = models.DateField()
    comments = models.IntegerField(default=0)
    excerpt = models.TextField()
    content = models.TextField()
