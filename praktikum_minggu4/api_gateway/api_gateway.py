import os
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

# Menyesuaikan path ke folder legacy_data
DATA_FILE = "../legacy_data/data.txt"

def read_legacy_records():
    """Membaca rekaman dari basis data teks legacy."""
    records = []
    if not os.path.exists(DATA_FILE):
        return records
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            clean_line = line.strip()
            if clean_line:
                fields = clean_line.split("|")
                if len(fields) >= 4:
                    records.append({
                        "id": fields[0].strip(),
                        "nama": fields[1].strip(),
                        "jurusan": fields[2].strip(),
                        "status": fields[3].strip()
                    })
    return records

def append_legacy_record(record):
    """Menulis rekaman baru ke basis data teks legacy."""
    line_entry = f"{record['id']}|{record['nama']}|{record['jurusan']}|{record['status']}\n"
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(line_entry)

@app.route("/api/v1/students", methods=["GET"])
def get_all_students():
    """Endpoint untuk mengambil semua data mahasiswa berformat JSON."""
    records = read_legacy_records()
    response_payload = {
        "metadata": {
            "service": "Legacy-Integrated API Gateway",
            "format": "JSON",
            "total_records": len(records),
            "timestamp": int(time.time())
        },
        "data": records
    }
    return jsonify(response_payload), 200

@app.route("/api/v1/students", methods=["POST"])
def create_student():
    """Endpoint untuk menambahkan data mahasiswa baru dari payload JSON ke file legacy."""
    payload = request.get_json()
    
    # Validasi input payload
    if not payload:
        return jsonify({"error": "Bad Request", "message": "Body payload JSON wajib disertakan"}), 400
    
    required_keys = ["id", "nama", "jurusan", "status"]
    missing_keys = [k for k in required_keys if k not in payload or not str(payload[k]).strip()]
    if missing_keys:
        return jsonify({
            "error": "Unprocessable Entity",
            "message": f"Kunci data berikut tidak boleh kosong: {', '.join(missing_keys)}"
        }), 422
    
    # Verifikasi ID tidak boleh ganda
    current_records = read_legacy_records()
    if any(r["id"] == str(payload["id"]) for r in current_records):
        return jsonify({
            "error": "Conflict",
            "message": f"Data dengan ID {payload['id']} sudah ada di sistem legacy"
        }), 409
    
    sanitized_record = {
        "id": str(payload["id"]).replace("|", ""),
        "nama": str(payload["nama"]).replace("|", ""),
        "jurusan": str(payload["jurusan"]).replace("|", ""),
        "status": str(payload["status"]).replace("|", "")
    }
    
    append_legacy_record(sanitized_record)
    
    return jsonify({
        "status": "success",
        "message": "Data berhasil disimpan ke sistem legacy",
        "created_item": sanitized_record
    }), 201

if __name__ == "__main__":
    print("[INFO] API Gateway berjalan di http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)