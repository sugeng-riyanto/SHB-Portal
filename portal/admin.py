"""Internal management is restricted to active superusers."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import School, Membership, SchoolUpdate

admin.site.has_permission = lambda request: bool(request.user.is_active and request.user.is_superuser)
admin.site.site_header = 'SHB Portal · Super Admin'
admin.site.site_title = 'SHB Portal'
admin.site.index_title = 'Pengelolaan sekolah dan pengguna'

User = get_user_model()
admin.site.unregister(User)
@admin.register(User)
class PortalUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser')
    list_filter = ('is_active', 'is_superuser', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_per_page = 25
    list_select_related = True

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 25

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'role', 'active')
    list_filter = ('school', 'role', 'active')
    search_fields = ('user__username', 'user__email', 'school__name')
    list_select_related = ('user', 'school')
    list_per_page = 25

@admin.register(SchoolUpdate)
class SchoolUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'published_at')
    list_filter = ('published',)
    search_fields = ('title', 'body')
    list_per_page = 25
