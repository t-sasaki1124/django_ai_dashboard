from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from .models import YouTubeComment
import csv
from io import TextIOWrapper

@admin.register(YouTubeComment)
class YouTubeCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'like_count', 'reply_count', 'created_at')
    search_fields = ('author', 'comment_text')
    change_list_template = "admin/myapp/youtubecomment/change_list.html"

    # ✅ URLルーティング追加
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv, name='import_csv'),
            path('delete-all/', self.delete_all, name='delete_all_youtube_comments'), 
        ]
        return custom_urls + urls

    # ✅ CSVインポート機能
    def import_csv(self, request):
        if request.method == "POST" and request.FILES.get("csv_file"):
            csv_file = TextIOWrapper(request.FILES["csv_file"].file, encoding="utf-8")
            reader = csv.DictReader(csv_file)
            count = 0
            for row in reader:
                YouTubeComment.objects.create(
                    video_id=row.get("video_id"),
                    comment_id=row.get("comment_id"),
                    comment_text=row.get("comment_text"),
                    author=row.get("author"),
                    like_count=int(row.get("like_count") or 0),
                    reply_count=int(row.get("reply_count") or 0),
                    reply_depth_potential=int(row.get("reply_depth_potential") or 0),
                    engagement_score=float(row.get("engagement_score") or 0),
                    created_at=row.get("created_at") or None,
                    ai_reply=row.get("ai_reply") if row.get("ai_reply") != "null" else None,
                    embedding=row.get("embedding") if row.get("embedding") else None,
                )
                count += 1
            messages.success(request, f"{count} 件のコメントをインポートしました。")
            return redirect("..")

        messages.error(request, "CSVファイルを選択してください。")
        return redirect("..")

    # ✅ 全件削除機能（CSVと同じレベルに定義）
    def delete_all(self, request):
        count = YouTubeComment.objects.count()
        YouTubeComment.objects.all().delete()
        messages.success(request, f"🗑 {count} 件のコメントを削除しました。")
        return redirect("..")
