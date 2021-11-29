from django.db.models import fields
from django.db.models.query import QuerySet
from django.views.generic.detail import DetailView
from .models import Cat, Toy, Photo
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import FeedingForm

from django.contrib.auth import login # creates session cookie and session in DT
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

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

@login_required
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

def unassoc_toy(request, cat_id, toy_id):
    Cat.objects.get(id=cat_id).toys.remove(toy_id)
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

# this view fn handles both GET and POST request
def signup(request):
    error_message = ''
    # checks to see if method id POST
    if request.method == 'POST':
        # handle the creation of a new user
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # this iwll add the user to the database
            user = form.save()
            # this is how e log a use in via code
            # creates session entry in DB 
            # and persist the session site wide until the user logs out
            login(request, user)
            return redirect('index')
        else:   
            error_message = 'Invalid sign up- try again'
    # this if for GET request
    # assuming our user clicked on "signup" from the navbar
    form = UserCreationForm()  # clears for
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context) # re-renders new signup form


    
# CBV: class-based-view set up
class CatIndex(LoginRequiredMixin, ListView):
    model = Cat
    template_name = 'cats/index.html'
    
    # display only the user's cats
    def get_queryset(self):
        queryset = Cat.objects.filter(user=self.request.user)
        return queryset

class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    # tell which fields we want to allow the user to create
    # fields = '__all__' # changed to tuple bc it pulls USER and TOY model
    fields = ('name', 'breed', 'description', 'age')
    # for form submission to create the cat - not best practice -- BEST PRACTICE to add get_absolute_url in Model
    # success_url = '/cats/' 

    # This inherited method is called when a
    # valid cat form is being submitted
    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user # form.instance is the cat
        # Let the CreateView do its job as usual
        return super().form_valid(form)

class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    fields = ('breed', 'description', 'age')
    # or 
    # fields = '__all__'

class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    success_url = '/cats/'


class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = ('name', 'color')


class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ('name', 'color')


class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'


class ToyDetail(LoginRequiredMixin, DetailView):
    model = Toy
    template_name = 'toys/detail.html'


class ToyList(LoginRequiredMixin, ListView):
    model = Toy
    template_name = 'toys/index.html'