from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# --- 修正後的連線設定 ---
def get_db_connection():
    # 建議直接使用 Render 提供的 DATABASE_URL
    # 如果你在 Render Environment 設定了這個 Key，這行就足夠了
    db_url = os.environ.get("DATABASE_URL")
    
    if db_url:
        return psycopg2.connect(db_url)
    
    return psycopg2.connect(
        host="dpg-d5cegqbe5dus738dau7g-a.singapore-postgres.render.com", # 需補全完整位址
        database="final_database_xnad",
        user="final_database_xnad_user",
        password="BMojjUkwDRZeQNs2rVdYdV479542lLrV",
        port=5432
    )
# -----------------------

@app.route("/", methods=["GET"])
def home():
    return "API is running"

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json
        member = data.get("member")
        inorout = data.get("inorout")
        time = data.get("time")

        if member is None or inorout is None:
            return jsonify({"error": "member and inorout are required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        # 請確認你的資料表名稱是 final，欄位包含 member, inorout, time
        cur.execute(
            "INSERT INTO final (member, inorout, time) VALUES (%s, %s, %s)",
            (member, inorout, time)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# 查詢所有紀錄
@app.route("/data", methods=["GET"])
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT ID, member, inorout, time FROM final ORDER BY ID DESC"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "ID": r[0],
            "member": r[1].strip(),  # 去掉多餘空白
            "inorout": r[2],
            "time": r[3].strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

