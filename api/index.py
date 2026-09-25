from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

@app.route('/api/get-tree', methods=['GET'])
def get_tree():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "缺少網址"}), 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tree_name = "未知樹木"
        all_texts = list(soup.stripped_strings)

        if 'greening.gov.hk' in url:
            for idx, text in enumerate(all_texts):
                if '學名' in text or 'Scientific Name' in text:
                    for i in range(idx - 1, max(-1, idx - 10), -1):
                        prev_text = all_texts[i]
                        if "名稱" not in prev_text and "Name" not in prev_text and len(prev_text) < 30:
                            tree_name = prev_text
                            break
                    break
        else:
            if soup.title and soup.title.string:
                parts = re.split(r'[-|]', soup.title.string)
                tree_name = parts[-1].strip()

        if tree_name != "未知樹木":
            tree_name = re.sub(r'[（\(].*?[）\)]', '', tree_name)
            tree_name = tree_name.split(',')[0].split('，')[0].strip()

        return jsonify({"name": tree_name})

    except Exception as e:
        return jsonify({"error": "解析失敗"}), 500

# 注意：Vercel 會自動處理 app 實例，不需要寫 app.run()
