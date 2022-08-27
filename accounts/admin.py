from django.contrib import admin

from .models import  User, UserAddress, UserBankAccount, Profile



admin.site.register(User)
admin.site.register(UserAddress)
admin.site.register(UserBankAccount)
admin.site.register(Profile)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id','token','user','verify']