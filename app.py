from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# PostgreSQL 連線資訊從環境變數
DB_HOST = os.environ.get("dpg-d5cegqbe5dus738dau7g-a")
DB_NAME = os.environ.get("final_database_xnad")
DB_USER = os.environ.get("final_database_xnad_user")
DB_PASSWORD = os.environ.get("BMojjUkwDRZeQNs2rVdYdV479542lLrV")
DB_PORT = int(os.environ.get("DB_PORT", 5432))

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

# 測試服務
@app.route("/", methods=["GET"])
def home():
    return "API is running"

# 上傳紀錄
@app.route("/upload", methods=["POST"])
def upload():
    data = request.json
    member = data.get("member")
    inorout = data.get("inorout")  # True/False
    time = data.get("time")
    if member is None or inorout is None:
        return jsonify({"error": "member and inorout are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO final (member, inorout, time) VALUES (%s, %s, %s)",
        (member, inorout, time)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "success"})

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
