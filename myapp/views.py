from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import YouTubeComment, Plan, UserPlan
import json
import pandas as pd
from datetime import datetime


def index(request):
    # 表示件数をクエリパラメータから取得（デフォルト: 30件）
    limit_options = [10, 30, 50]
    limit = int(request.GET.get('limit', 30))
    if limit not in limit_options:
        limit = 30
    
    # ページ番号を取得（デフォルト: 1ページ目）
    page_number = request.GET.get('page', 1)
    
    # グラフ用には最大300件を使用
    comments_for_graph = YouTubeComment.objects.all()[:300]
    # テーブル表示用には全件を取得してページネーション
    all_comments = YouTubeComment.objects.all().order_by('-created_at')
    
    # ページネーション
    paginator = Paginator(all_comments, limit)
    page_obj = paginator.get_page(page_number)
    comments = page_obj.object_list

    # 3Dグラフ用のデータを準備
    graph_data = None
    stats = None

    if comments_for_graph.exists():
        df = pd.DataFrame(list(comments_for_graph.values(
            "like_count",
            "reply_count",
            "created_at",
            "author",
            "comment_text",
        )))

        # タイムスタンプを数値に変換
        df["created_at_num"] = df["created_at"].astype("int64") // 10**9
        
        # グラフ用のデータをリスト形式に変換
        graph_data = {
            "x": df["like_count"].tolist(),
            "y": df["reply_count"].tolist(),
            "z": df["created_at_num"].tolist(),
            "text": [
                f"Author: {author}<br>Likes: {likes}<br>Replies: {replies}<br>Comment: {text[:50]}..."
                for author, likes, replies, text in zip(
                    df["author"], df["like_count"], df["reply_count"], df["comment_text"]
                )
            ],
            "colors": df["created_at_num"].tolist(),  # 色分け用
        }

        # 統計情報を計算
        stats = {
            "total_comments": len(df),
            "avg_likes": float(df["like_count"].mean()),
            "avg_replies": float(df["reply_count"].mean()),
            "max_likes": int(df["like_count"].max()),
            "max_replies": int(df["reply_count"].max()),
            "total_likes": int(df["like_count"].sum()),
            "total_replies": int(df["reply_count"].sum()),
        }

    return render(request, "index.html", {
        "graph_data": json.dumps(graph_data) if graph_data else None,
        "stats": stats,
        "comments": comments,
        "page_obj": page_obj,
        "current_limit": limit,
        "limit_options": limit_options,
    })


def comments_table(request):
    """Ajax用: コメントテーブル部分のみを返す"""
    # 表示件数をクエリパラメータから取得（デフォルト: 30件）
    limit_options = [10, 30, 50]
    limit = int(request.GET.get('limit', 30))
    if limit not in limit_options:
        limit = 30
    
    # ページ番号を取得（デフォルト: 1ページ目）
    page_number = request.GET.get('page', 1)
    
    # テーブル表示用には全件を取得してページネーション
    all_comments = YouTubeComment.objects.all().order_by('-created_at')
    
    # ページネーション
    paginator = Paginator(all_comments, limit)
    page_obj = paginator.get_page(page_number)
    comments = page_obj.object_list

    from django.template.loader import render_to_string
    html = render_to_string('comments_table.html', {
        'comments': comments,
        'page_obj': page_obj,
        'current_limit': limit,
        'limit_options': limit_options,
    }, request=request)
    
    return JsonResponse({'html': html})


def pricing(request):
    # 現在のユーザーのプラン情報を取得
    current_plan = None
    current_user_plan = None
    if request.user.is_authenticated:
        try:
            current_user_plan = UserPlan.objects.get(user=request.user, is_active=True)
            current_plan = current_user_plan.plan
        except UserPlan.DoesNotExist:
            pass
    
    # すべてのプランを取得
    plans = Plan.objects.all().order_by('price')
    
    return render(request, "pricing.html", {
        "current_plan": current_plan,
        "current_user_plan": current_user_plan,
        "plans": plans,
        "user": request.user,  # テンプレートでユーザーIDを使用するため
    })


