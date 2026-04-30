from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
socketio = SocketIO(app)

# --- Route untuk halaman utama ---
@app.route("/")
def home():
    return render_template("index.html")

# --- Fungsi untuk baca/simpan JSON ---
def load_products():
    with open("products.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_products(products):
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=4, ensure_ascii=False)

# --- Endpoint REST API ---
@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(load_products())

@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    return jsonify(product) if product else ("Not Found", 404)

@app.route("/products", methods=["POST"])
def add_product():
    products = load_products()
    new_product = request.json
    new_product["id"] = max(p["id"] for p in products) + 1
    products.append(new_product)
    save_products(products)
    socketio.emit("update_products", products, broadcast=True)
    return jsonify(new_product), 201

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        product.update(request.json)
        save_products(products)
        socketio.emit("update_products", products, broadcast=True)
        return jsonify(product)
    return ("Not Found", 404)

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        products = [p for p in products if p["id"] != product_id]
        save_products(products)
        socketio.emit("update_products", products, broadcast=True)
        return jsonify({"message": "Deleted", "product": product}), 200
    return ("Not Found", 404)

# --- Event WebSocket manual ---
@socketio.on("get_products")
def handle_get_products():
    print("Client meminta data produk")  # log untuk debug
    emit("update_products", load_products())

if __name__ == "__main__":
    socketio.run(app, debug=True, host="localhost", port=5000)
