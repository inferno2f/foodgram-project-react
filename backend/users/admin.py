from pyexpat import model
from django.contrib import admin

from users import models


admin.site.register(models.Follow)
admin.site.register(models.CustomUser)
