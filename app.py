from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# --- 資料庫連線 (保持你原本的連線邏輯) ---
def get_db_connection():
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

# 1. 查詢與分頁 API
@app.route("/data", methods=["GET"])
def get_data():
    page = int(request.args.get('page', 1))
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    limit = 10
    offset = (page - 1) * limit

    conn = get_db_connection()
    cur = conn.cursor()
    
    # 這裡加上雙引號處理大寫 ID
    query = 'SELECT "ID", member, inorout, time FROM final'
    params = []

    if start_date and end_date:
        query += ' WHERE time BETWEEN %s AND %s'
        params.extend([start_date + " 00:00:00", end_date + " 23:59:59"])
    
    query += " ORDER BY time DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # 這裡對應的 r[0] 就是你的大寫 ID
    result = [
        {
            "ID": r[0], 
            "member": r[1].strip(), 
            "inorout": r[2], 
            "time": r[3].strftime("%Y-%m-%d %H:%M:%S")
        } for r in rows
    ]
    return jsonify(result)

# 2. 統計「還在裡面」的人員 API
@app.route("/missing", methods=["GET"])
def get_missing():
    conn = get_db_connection()
    cur = conn.cursor()
    # 邏輯：找最後一筆紀錄是 True (進入) 的人
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

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))