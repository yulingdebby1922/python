from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import shutil
import subprocess
from glob import glob

app = Flask(__name__)
input_dir = "./pdfs"  # PDF 上傳資料夾
output_dir = "./output"
cache_dir = "./cache"

# 初始化資料夾
for folder in [input_dir, output_dir, cache_dir]:
    os.makedirs(folder, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('index'))

        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('index'))

        if file and file.filename.endswith('.pdf'):
            file_path = os.path.join(input_dir, file.filename)
            file.save(file_path)
            process_pdf(file_path)
            return redirect(url_for('index'))

    files = os.listdir(output_dir)  # 取得轉換後的檔案列表
    return render_template('index.html', files=files)

def process_pdf(pdf_file):
    # 清除輸出資料夾
    for folder in [cache_dir, output_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    
    # PDF 處理命令
    command = [
        "unstructured-ingest", "local",
        "--input-path", pdf_file,
        "--output-dir", output_dir,
        "--reprocess",
        "--skip-infer-table-types", "true"
    ]

    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        print("成功轉檔！")
    except subprocess.CalledProcessError as e:
        print("轉檔失敗。錯誤訊息：", e.stderr)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(output_dir, filename)

if __name__ == '__main__':
    app.run(debug=True)
