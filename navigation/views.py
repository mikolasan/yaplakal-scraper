from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .scrap import get_front_page_posts
from navigation.models import Post

def index(request):
    template = loader.get_template('navigation/index.html')
    return HttpResponse(template.render({}, request))

def list(request):
    posts = Post.objects.order_by('-rating')
    template = loader.get_template('navigation/list.html')
    return HttpResponse(template.render({'posts':posts}, request))

def update(request):
    posts = get_front_page_posts()
    for p in posts:
        post = Post(rating = p['rating'],
                    link = p['link'],
                    title = p['title'],
                    image_src = p['image_src'],
                    author = p['author'],
                    section = p['section'],
                    date = p['date'],
                    comments = p['comments'],
                    excerpt = p['excerpt'],
                    content = p['content'])
        post.save()
    return HttpResponseRedirect(reverse('navigation:list'))

def soup(request):
    posts = get_front_page_posts()
    for p in posts:
        post = Post(rating = p['rating'],
                    link = p['link'],
                    title = p['title'],
                    image_src = p['image_src'],
                    author = p['author'],
                    section = p['section'],
                    date = p['date'],
                    comments = p['comments'],
                    excerpt = p['excerpt'],
                    content = p['content'])
        post.save()
    template = loader.get_template('navigation/posts.html')
    return HttpResponse(template.render({'posts':posts}, request))
