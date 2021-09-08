from django.contrib import admin
from .models import Contributor,Participant,Team

# Register your models here.
admin.site.register(Contributor)
admin.site.register(Participant)
admin.site.register(Team)