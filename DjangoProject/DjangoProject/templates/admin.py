from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from DjangoProject.models import Post, Category, Author, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class AuthorInline(admin.StackedInline):
    model = Author


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline, AuthorInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role')

    def get_role(self, obj):
        return obj.userprofile.get_role_display()

    get_role.short_description = 'Role'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Post)
admin.site.register(Category)