from django.contrib import admin
from .models import YouTubeComment

@admin.register(YouTubeComment)
class YouTubeCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'like_count', 'reply_count', 'created_at')
    search_fields = ('author', 'comment_text')
    change_list_template = "admin/myapp/youtubecomment/change_list.html"
