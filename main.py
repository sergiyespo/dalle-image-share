from flask import Flask, request, send_file, jsonify
import requests
import tempfile
import os

app = Flask(__name__)

@app.route('/fetch-image', methods=['POST'])
def fetch_image():
    data = request.json
    image_url = data.get("url")

    if not image_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        for chunk in response.iter_content(1024):
            temp_file.write(chunk)
        temp_file.close()

        return send_file(temp_file.name, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/make-public', methods=['POST'])
def make_public():
    image_url = request.form.get("url")

    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        for chunk in response.iter_content(1024):
            temp_file.write(chunk)
        temp_file.close()

        return f'''
            <p>Image made public:</p>
            <img src="/serve-temp?filename={os.path.basename(temp_file.name)}" width="400">
            <p>Direct link: <a href="/serve-temp?filename={os.path.basename(temp_file.name)}">Open image</a></p>
        '''
    except Exception as e:
        return f"<p>Error: {e}</p>"

@app.route('/make-public-json', methods=['POST'])
def make_public_json():
    image_url = request.json.get("url")
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        for chunk in response.iter_content(1024):
            temp_file.write(chunk)
        temp_file.close()

        public_url = f"https://dalle-image-share.onrender.com/serve-temp?filename={os.path.basename(temp_file.name)}"
        return jsonify({"public_url": public_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/serve-temp')
def serve_temp():
    filename = request.args.get("filename")
    filepath = f"/tmp/{filename}"
    if os.path.exists(filepath):
        return send_file(filepath, mimetype="image/png")
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
