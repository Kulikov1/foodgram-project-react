from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')
    list_display = (
        'username',
        'id',
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
