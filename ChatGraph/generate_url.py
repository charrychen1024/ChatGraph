from flask import Flask, request, jsonify
import uuid
import os

app = Flask(__name__)
UPLOAD_FOLDER = "html_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload-html', methods=['POST'])
def upload_html():
    html_content = request.json.get('html')
    if not html_content:
        return jsonify({"error": "缺少 HTML 内容"}), 400
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4()) + ".html"
    file_path = os.path.join(UPLOAD_FOLDER, file_id)
    
    # 保存 HTML 文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # 返回预览链接（需部署到公网，如用 ngrok 暴露本地服务）
    preview_url = f"https://your-domain.com/{file_id}"
    return jsonify({"success": True, "url": preview_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)