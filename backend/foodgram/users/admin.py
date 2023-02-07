from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')


@admin.register(Follow)
class SubscriptionAdmin(admin.ModelAdmin):
    pass