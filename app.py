from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# 資料庫連線設定
def get_db_connection():
    # 優先讀取環境變數，若無則使用固定連線字串
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        host="dpg-d5cegqbe5dus738dau7g-a.singapore-postgres.render.com",
        database="final_database_xnad",
        user="final_database_xnad_user",
        password="BMojjUkwDRZeQNs2rVdYdV479542lLrV",
        port=5432
    )

# --- 1. 接收硬體資料上傳 ---
@app.route("/upload", methods=["POST"])
def upload_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        member = data.get("member")
        inorout = data.get("inorout") # 預期為 True/False
        
        if member is None or inorout is None:
            return jsonify({"error": "Missing fields"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        # 插入資料，時間由資料庫自動產生或 Python 產生
        cur.execute(
            'INSERT INTO final (member, inorout, time) VALUES (%s, %s, %s)',
            (member, inorout, datetime.now())
        )
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": "Data uploaded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 2. 網頁查詢 API (含分頁與時間篩選) ---
@app.route("/data", methods=["GET"])
def get_data():
    try:
        page = int(request.args.get('page', 1))
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        limit = 10
        offset = (page - 1) * limit

        conn = get_db_connection()
        cur = conn.cursor()
        
        # 使用雙引號處理大寫 "ID"
        query = 'SELECT "ID", member, inorout, time FROM final'
        params = []

        if start_date and end_date:
            query += ' WHERE time BETWEEN %s AND %s'
            params.extend([start_date + " 00:00:00", end_date + " 23:59:59"])
        
        query += ' ORDER BY time DESC LIMIT %s OFFSET %s'
        params.extend([limit, offset])
        
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        result = [
            {
                "ID": r[0],
                "member": r[1].strip() if r[1] else "",
                "inorout": r[2],
                "time": r[3].strftime("%Y-%m-%d %H:%M:%S") if r[3] else ""
            } for r in rows
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 3. 統計場內人員 (最後狀態為 True 者) ---
@app.route("/missing", methods=["GET"])
def get_missing():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # 找出每個人最後一筆紀錄，且該紀錄為進入(True)的人
        sql = """
        SELECT member FROM (
            SELECT DISTINCT ON (member) member, inorout, time
            FROM final
            ORDER BY member, time DESC
        ) AS latest
        WHERE inorout = True;
        """
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([r[0].strip() for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 4. 渲染前端網頁 ---
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    # Render 環境需讀取 PORT 變數
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)