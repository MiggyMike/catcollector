from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User

# Create your models here.

# defining constant variables are ALL CAPS
MEALS = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner')
)

class Toy(models.Model): # must come before the Cat as its a many to many
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.name} with and color of {self.color}'
    
    def get_absolute_url(self):
        return reverse('toys_detail', kwargs={'pk': self.id})

class Cat(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()
    toys = models.ManyToManyField(Toy)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Best practice to overried the __str__ method so they print in a more helpful way
    # YOU DONT NEED TO CREATE ANOTHER MIGRATION WITH THIS HERE becuase it doesnt
    
    def __str__(self):
        return f'{self.name} with and id of {self.id}'

    def get_absolute_url(self):
        # return reverse('detail', kwargs={'cat_id': self.id})
        return reverse('detail', kwargs={'pk': self.id})

class Feeding(models.Model):
    date = models.DateField('Feeding Date')
    meal = models.CharField(
        max_length=1, 
        #  add the 'choices' field option
        choices=MEALS, 
        #  set the defailt value for meal to be 'B'
        default=MEALS[0][0],
    )
    
    # Create a cat_id FK
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        # Nice method for obtaining the friendly value of a Field.choice
        return f"{self.get_meal_display()} on {self.date}"
    
    class Meta:
        ordering = ('-date',)

class Photo(models.Model):
    url = models.CharField(max_length=200)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        return f'Photo for cat_id: {self.cat_id} @{self.url}'