from django.contrib import admin
# add Feeding to the import
from .models import Cat, Feeding, Toy, Photo

# Register your models here.

admin.site.register(Cat)
# register the new Feeding Model
admin.site.register(Feeding)
admin.site.register(Toy)
admin.site.register(Photo)