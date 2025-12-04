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
        
        # 分析結果とアドバイスを生成（有料プラン・無料プラン両方で生成）
        analysis = None
        advice = None
        
        # 有料プランチェック
        is_premium = False
        if request.user.is_authenticated:
            try:
                user_plan = UserPlan.objects.get(user=request.user, is_active=True)
                is_premium = user_plan.is_premium
            except UserPlan.DoesNotExist:
                pass
        
        if len(df) > 0:
            # 分析結果を生成
            high_engagement = df[(df["like_count"] > stats["avg_likes"]) & (df["reply_count"] > stats["avg_replies"])]
            low_engagement = df[(df["like_count"] < stats["avg_likes"]) & (df["reply_count"] < stats["avg_replies"])]
            
            engagement_ratio = len(high_engagement) / len(df) * 100 if len(df) > 0 else 0
            
            analysis = {
                "high_engagement_count": len(high_engagement),
                "low_engagement_count": len(low_engagement),
                "engagement_ratio": round(engagement_ratio, 1),
                "top_comment_likes": int(df.nlargest(1, "like_count")["like_count"].iloc[0]) if len(df) > 0 else 0,
                "top_comment_replies": int(df.nlargest(1, "reply_count")["reply_count"].iloc[0]) if len(df) > 0 else 0,
            }
            
            # アドバイスを生成
            advice_items = []
            
            if stats["avg_likes"] < 5:
                advice_items.append("平均いいね数が低い傾向にあります。コメントの内容をより具体的で価値のあるものにすることで、エンゲージメントを向上させることができます。")
            
            if stats["avg_replies"] < 2:
                advice_items.append("返信数が少ない傾向にあります。質問形式のコメントや議論を促す内容を増やすことで、コミュニティの活性化につながります。")
            
            if engagement_ratio < 20:
                advice_items.append("高エンゲージメントコメントの割合が低いです。視聴者の興味を引く話題や、タイムリーな内容を意識することで改善できます。")
            
            if len(high_engagement) > 0:
                top_comment = df.nlargest(1, "like_count").iloc[0]
                advice_items.append(f"最もエンゲージメントが高いコメントは{int(top_comment['like_count'])}いいね、{int(top_comment['reply_count'])}返信を獲得しています。このようなコメントの特徴を分析し、同様のアプローチを他のコメントにも適用することをお勧めします。")
            
            if stats["max_likes"] > stats["avg_likes"] * 3:
                advice_items.append("一部のコメントが非常に高いエンゲージメントを獲得しています。これらの成功パターンを分析し、コンテンツ戦略に反映させることで、全体的なエンゲージメント向上が期待できます。")
            
            if not advice_items:
                advice_items.append("現在のエンゲージメント状況は良好です。継続的な分析と改善により、さらなる成長が期待できます。")
            
            advice = advice_items

    return render(request, "index.html", {
        "graph_data": json.dumps(graph_data) if graph_data else None,
        "stats": stats,
        "comments": comments,
        "page_obj": page_obj,
        "current_limit": limit,
        "limit_options": limit_options,
        "is_premium": is_premium,
        "analysis": analysis,
        "advice": advice,
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


