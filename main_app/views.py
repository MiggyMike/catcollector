from django.db.models import fields
from django.views.generic.detail import DetailView
from .models import Cat, Toy, Photo
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import FeedingForm
from main_app import models

import boto3
import uuid

S3_BASE_URL = 'https://s3-us-west-1.amazonaws.com/'
BUCKET = 'catcollector-mj-photo-uploads'

# from django.http import HttpResponse  # generates a response to client, you just have to pass

# Create your views here.

def home(request):
    """
    this is where we can return a response
    in most cases we render a template
    we'll also need some data for that template in most cases
    """
    return render(request, 'home.html')
    # return HttpResponse('<h1>Hello World</h1>')

def about(request):
    return render(request, 'about.html')
    # return HttpResponse('<h1>About the CatCollector</h1>')


# this class is temporary as we dont have cats in our DB
# class Cat:
#     def __init__(self, name, breed, description, age):
#         self.name = name
#         self.breed = breed
#         self.description = description
#         self.age = age

# cats = [
#   Cat('Lolo', 'tabby', 'foul little demon', 3),
#   Cat('Sachi', 'tortoise shell', 'diluted tortoise shell', 0),
#   Cat('Raven', 'black tripod', '3 legged cat', 4)
# ]

# this replaces  the class Cat and cats' list because we have now created the model
# def cats_index(request):
#     cats = Cat.objects.all()
#     return render(request, 'cats/index.html', { 'cats': cats })

def cats_detail(request, pk): #changed cat_id to pk
    cat = Cat.objects.get(id=pk) #changed cat_id to pk
    
    feeding_form = FeedingForm()

    toys_cat_doesnt_have = Toy.objects.exclude(id__in=cat.toys.all().values_list('id'))
    
    return render(
        request,
        'cats/detail.html', {
            'cat': cat,
            'feeding_form': feeding_form,
            'toys': toys_cat_doesnt_have
        })

def add_feeding(request, pk):
      # create the ModelForm using the data in request.POST
  form = FeedingForm(request.POST)
  # validate the form
  if form.is_valid():
    # don't save the form to the db until it
    # has the cat_id / pk assigned
    new_feeding = form.save(commit=False)
    new_feeding.cat_id = pk
    new_feeding.save()
  return redirect('detail', pk=pk)

def assoc_toy(request, cat_id, toy_id):
    Cat.objects.get(id=cat_id).toys.add(toy_id)
    return redirect('detail', pk=cat_id)

def add_photo(request, pk):
    photo_file = request.FILES.get('photo-file')
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]

        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f'{S3_BASE_URL}{BUCKET}/{key}'
            photo = Photo(url=url, cat_id=pk)
            photo.save()
        except Exception as error:
            print(f'an error occured uploading to AWS S3')
            print(error)
    return redirect('detail', pk=pk)
    
# class-based-view set up
class CatIndex(ListView):
    model = Cat
    template_name = 'cats/index.html'

class CatCreate(CreateView):
    model = Cat
    # tell which fields we want to allow the user to create
    fields = '__all__'
    # for form submission to create the cat - not best practice -- BEST PRACTICE to add get_absolute_url in Model
    # success_url = '/cats/' 

class CatUpdate(UpdateView):
    model = Cat
    fields = ('breed', 'description', 'age')
    # or 
    # fields = '__all__'

class CatDelete(DeleteView):
    model = Cat
    success_url = '/cats/'


class ToyCreate(CreateView):
    model = Toy
    fields = ('name', 'color')


class ToyUpdate(UpdateView):
    model = Toy
    fields = ('name', 'color')


class ToyDelete(DeleteView):
    model = Toy
    success_url = '/toys/'


class ToyDetail(DetailView):
    model = Toy
    template_name = 'toys/detail.html'


class ToyList(ListView):
    model = Toy
    template_name = 'toys/index.html'