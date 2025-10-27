from django.contrib import admin
from .models import PartyModel, PartyUser, PartyGroup, FollowModel
from django.contrib.auth.admin import UserAdmin


class PartyAdmin(admin.ModelAdmin):
    list_display = ["party_title", "date"]


class UserPartyAdmin(UserAdmin):
    list_display = ["email", "username", "birth"]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ("avatar", 'email', 'birth')}))


class GroupAdmin(admin.ModelAdmin):
    list_display = ["name"]


class FollowerAdmin(admin.ModelAdmin):
    list_display = ["follower", 'followed']


admin.site.register(PartyModel, PartyAdmin)
admin.site.register(PartyUser, UserPartyAdmin)
admin.site.register(PartyGroup, GroupAdmin)
admin.site.register(FollowModel, FollowerAdmin)
