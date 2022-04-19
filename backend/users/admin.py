from django.contrib import admin

from users import models


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    empty_value_display = '-empty-'


admin.site.register(models.Follow)
admin.site.register(models.CustomUser, UserAdmin)
