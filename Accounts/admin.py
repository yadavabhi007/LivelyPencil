from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.widgets import AdminFileWidget


admin.site.site_title = "Lively Pencil"
admin.site.site_header = "Lively Pencil Administration"
admin.site.index_title = "Lively Pencil Administration"


# Register your models here.

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(
                f'<a href="{image_url}" target="_blank">'
                f'<img src="{image_url}" alt="{file_name}" width="150" height="150" '
                f'style="object-fit: cover;"/> </a>')
        output.append(super(AdminFileWidget, self).render(name, value, attrs, renderer))
        return mark_safe(u''.join(output))


class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'profile_image', 'username', 'email', 'first_name', 'last_name', 'email_verified', 'is_admin', 'created_at', 'updated_at')
    list_display_links = ('id', 'username', 'profile_image', 'email', 'first_name', 'last_name')
    list_filter = ("is_admin", "is_active", 'created_at', 'updated_at')
    ordering = ['id', 'first_name', 'last_name', 'email', 'created_at', 'updated_at']
    list_per_page = 10
    search_fields = ('first_name', 'last_name', 'email')
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'device_token',  'password')}),
        ('Personal Info', {'fields': ('username', 'first_name', 'last_name', 'stream_title', 'stream_cover_image', 'image', 'role', 'interesting')}),
        ('Personal Details', {'fields': ('birth_date', 'country', 'notification', 'followers', 'followings', 'likes',  'verify_email_otp', 'reset_password_otp', 'email_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'device_token', 'username', 'first_name', 'last_name', 'stream_title', 'stream_cover_image', 'image', 'role', 'interesting', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget}
    }
admin.site.register(User, UserAdmin)


@admin.register(PostContent)
class PostContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'text', 'created_at', 'updated_at']
    odering = ('id', 'book', 'text', 'created_at', 'updated_at')
    search_fields = ('book__book_name', 'text')
    list_filter = ('created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_file','post', 'created_at', 'updated_at']
    odering = ('id','post', 'created_at', 'updated_at')
    search_fields = ('post__text',)
    list_filter = ('created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')
    formfield_overrides = {
        models.FileField: {'widget': AdminImageWidget}
    }


@admin.register(Interesting)
class InterestingAdmin(admin.ModelAdmin):
    list_display = ['id','category', 'created_at', 'updated_at']
    odering = ('id','category', 'created_at', 'updated_at')
    search_fields = ('category',)
    list_filter = ('created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VideoUpload)
class VideoUploadAdmin(admin.ModelAdmin):
    list_display = ['id','video','post']
    odering = ('id','post', 'video')
    search_fields = ('post__text',)
    list_filter = ('created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')

    
@admin.register(MusicUpload)
class MusicUploadAdmin(admin.ModelAdmin):
    list_display = ['id','music','post']
    odering = ('id','post', 'music')
    search_fields = ('post__text',)
    list_filter = ('created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'file', 'type', 'user', 'interersting', 'role']
    odering = ('id', 'title', 'file', 'type', 'user', 'interersting', 'role')
    search_fields = ('title', 'file', 'type', 'role')
    list_filter = ('type', 'interersting', 'role', 'created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')


# @admin.register(PostLikes)
# class PostLikesAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'post']
#     odering = ('id', 'user', 'post')
#     search_fields = ('user__username', 'post__title')
#     list_filter = ('user', 'post')
#     list_per_page = 10
#     filter_horizontal = ()


# @admin.register(PostDislikes)
# class PostDislikesAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'post']
#     odering = ('id', 'user', 'post')
#     search_fields = ('user__username', 'post__title')
#     list_filter = ('user', 'post')
#     list_per_page = 10
#     filter_horizontal = ()


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'comment']
    odering = ('id', 'user', 'post', 'comment')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'post__title', 'comment')
    list_filter = ('user', 'post', 'created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')


# @admin.register(FriendRequest)
# class FriendRequestAdmin(admin.ModelAdmin):
#     list_display = ['id','sender', 'reciever', 'created_at', 'updated_at']
#     odering = ('id','sender', 'reciever', 'created_at', 'updated_at')
#     search_fields = ('sender__first_name', 'reciever__first_name')
#     list_per_page = 10
#     filter_horizontal = ()


# @admin.register(TVChannel)
# class TVChannelAdmin(admin.ModelAdmin):
#     list_display = ['id', 'tv_logo_file', 'user', 'topic', 'created_at', 'updated_at', 'action']
#     odering = ('id', 'tv_logo_file', 'user', 'topic', 'created_at', 'updated_at')
#     search_fields = ('topic', 'user__first_name', 'stream_name__category')
#     list_per_page = 10
#     list_filter = ('stream_name__category',)
#     filter_horizontal = ()
#     readonly_fields = ('tv_logo_file',)
#     def action(self, obj):
#         if obj.id:
#             return mark_safe("<a class='button btn' style='color:green; padding:0 1rem; ' href='/admin/Accounts/tvchannel/{}/change/'>Edit</a>".format(obj.id)
#                              + "    " + "<a class='button btn' style='color:red; padding:0 1rem; ' href='/admin/Accounts/tvchannel/{}/delete/'>Delete</a>".format(obj.id))
#         else:
#             social_button = '<a  href="#">---</a>'
#             return mark_safe(u''.join(social_button))


# @admin.register(TVChannelComment)
# class TVChannelCommentAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'tv_channel', 'comment']
#     odering = ('id', 'user', 'tv_channel', 'comment')
#     search_fields = ('user__username', 'tv_channel__topic', 'comment')
#     list_filter = ('user', 'tv_channel')
#     list_per_page = 10
#     filter_horizontal = ()


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'title', 'message', 'recieved_date', 'created_at', 'updated_at']
    search_fields = ('title',)
    ordering = ('id','sender', 'title', 'message', 'recieved_date', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'book_name', 'book_status', 'created_at', 'updated_at']
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'book_name',)
    ordering = ('id', 'user', 'book_name', 'book_status', 'created_at', 'updated_at')
    list_filter = ('user', 'book_status', 'created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'image_file', 'created_at', 'updated_at']
    search_fields = ('name', 'email',)
    ordering = ('id', 'name', 'email', 'created_at', 'updated_at')
    list_filter = ('name', 'email', 'created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget}
    }


@admin.register(Help)
class HelpAdmin(admin.ModelAdmin):
    list_display = ['id', 'heading', 'created_at', 'updated_at']
    search_fields = ('heading',)
    ordering = ('id', 'heading', 'created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['id', 'heading', 'description', 'created_at', 'updated_at']
    search_fields = ('heading',)
    ordering = ('id', 'heading', 'description', 'created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TermsAndConditions)
class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'heading', 'description', 'created_at', 'updated_at']
    search_fields = ('heading',)
    ordering = ('id', 'heading', 'description', 'created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProfileReport)
class ProfileReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'report_by', 'report_to', 'created_at', 'updated_at']
    search_fields = ('report_by__first_name', 'report_to__first_name', 'report_by__last_name', 'report_to__last_name', 'report_by__email', 'report_to__email')
    ordering = ('id', 'report_by', 'report_to', 'created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')