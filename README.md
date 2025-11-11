# Django AI Dashboard - YouTubeコメント管理ツール

このプロジェクトは、**DjangoベースのAIダッシュボード** です。  
YouTubeコメントをCSVからインポートし、管理画面で閲覧・分析・一括削除できるように構築されています。

---

## 🚀 1. 環境構築

### リポジトリをクローン
```bash
git clone https://github.com/<あなたのユーザー名>/django_ai_dashboard.git
cd django_ai_dashboard
```

### 仮想環境の作成と有効化

**Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 2. 必要パッケージのインストール
```bash
pip install -r requirements.txt
```

もし `requirements.txt` がまだ無い場合は、以下を直接実行：
```bash
pip install django pandas matplotlib psycopg2-binary
```

---

## ⚙️ 3. Django初期設定

### マイグレーションを実行
```bash
python manage.py migrate
```

### 管理ユーザーを作成
```bash
python manage.py createsuperuser
```
※ 以下を順に入力してください  
- ユーザー名  
- メールアドレス  
- パスワード  

---

## 🖥 4. サーバーを起動
```bash
python manage.py runserver
```

ブラウザで以下にアクセス：
```
http://127.0.0.1:8000/admin/
```

ログイン画面が表示されたら、作成した管理者アカウントでログインします。

---

## 📁 5. YouTubeコメントのインポート

管理画面の手順：
1. 左メニューの **「YouTube Comments」** をクリック  
2. 画面上部の **「Import CSV」** ボタンをクリック  
3. CSVファイルを選択してアップロード  
4. アップロード後、コメント一覧にデータが表示されます  

CSVファイルの例：
```csv
id,video_id,comment_id,comment_text,author,like_count,reply_count,reply_depth_potential,engagement_score,created_at,ai_reply,embedding
1,PTw4q-pp1GE,Ugw2g3kQcoy9Sk2zRQh4AaABAg,"いい動画ですね！",@user1,5,0,0,0.8,2025-11-05 12:00:00,,
```

---

## 🗑 6. コメントの一括削除

コメントを全件削除するには：
- **「🗑 Delete All Comments」** ボタンをクリック  
- 成功すると以下のようなメッセージが表示されます：
  ```
  🗑 56 件のコメントを削除しました。
  ```

---

## 🧱 7. プロジェクト構成

```
django_ai_dashboard/
├─ myproject/
│  ├─ settings.py
│  ├─ urls.py
│  └─ ...
├─ myapp/
│  ├─ admin.py
│  ├─ models.py
│  ├─ templates/
│  │   └─ admin/myapp/youtubecomment/change_list.html
│  ├─ static/
│  └─ ...
├─ db.sqlite3
├─ manage.py
└─ README.md
```

---

## 💡 8. よく使うコマンド集

| 目的 | コマンド |
|------|----------|
| サーバー起動 | `python manage.py runserver` |
| モデル変更を検知 | `python manage.py makemigrations` |
| DBに反映 | `python manage.py migrate` |
| 管理者作成 | `python manage.py createsuperuser` |
| エラーチェック | `python manage.py check` |
| 仮想環境終了 | `deactivate` |

---

## ⚠️ 9. 警告の対処法

以下の警告が出た場合：
```
staticfiles.W004: The directory 'myapp/static' does not exist.
```
→ `myapp/static` フォルダを手動で作成してください。
```bash
mkdir myapp/static
```

---

## 🔄 10. データをリセットしたい場合

すべてのコメントや設定を初期化したいとき：
```bash
del db.sqlite3
python manage.py migrate
```

---

## 📤 11. 変更をGitHubへ反映

```bash
git add .
git commit -m "Add CSV import and bulk delete features for YouTube comments in admin panel"
git push origin main
```

---

## ✅ 12. 動作確認

- `/admin/` にアクセスできる  
- CSVインポートが正常に行える  
- 「🗑 Delete All Comments」ボタンで全件削除できる  

---

## 🧠 補足メモ

- 現状はSQLiteを使用（`db.sqlite3`）  
- 今後PostgreSQLやAI分析機能に拡張可能  
- 静的ファイル (`/static`) にCSS・グラフ画像を配置可能  

---

© 2025 ts  
Built with using **Django 4.2**
