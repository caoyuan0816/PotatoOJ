from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from .models import *


class PotatoPlantInline(admin.StackedInline):
    model = PotatoPlant
    can_delete = False
    verbose_name_plural = 'Potato User Data'


class UserAdmin(BaseUserAdmin):
    inlines = (PotatoPlantInline, )


class GroupProfileInline(admin.StackedInline):
    model = GroupProfile
    can_delete = False
    verbose_name_plural = "Group Profile"


class GroupAdmin(BaseGroupAdmin):
    inlines = (GroupProfileInline, )


class ContestPubQuestionInline(admin.TabularInline):
    model = ContestPubQuestions
    extra = 1


class ContestAdmin(admin.ModelAdmin):
    inlines = (ContestPubQuestionInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

admin.site.register(Question)
admin.site.register(ContestMission)
admin.site.register(Mission)
admin.site.register(Contest, ContestAdmin)
