import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Cấu hình đường dẫn thư mục nguồn
BASE_PDF_DIR = os.path.join('resources', 'pdf')


@app.route('/')
def index():
    pdf_files = []
    if os.path.exists(BASE_PDF_DIR):
        # Lọc ra tất cả các file có đuôi .pdf
        for filename in os.listdir(BASE_PDF_DIR):
            if filename.lower().endswith('.pdf'):
                # Lấy tên file không bao gồm đuôi mở rộng
                name_without_ext = os.path.splitext(filename)[0]
                pdf_files.append({'name': name_without_ext})

    return render_template('index.html', pdf_files=pdf_files)


@app.route('/get-text/<filename>')
def get_text(filename):
    # Khôi phục đường dẫn: resources/pdf/filename/filename.txt (hoặc tên bất kỳ .txt nào bên trong)
    # Giả định file text trích xuất trùng tên và nằm trong thư mục của nó
    text_folder = os.path.join(BASE_PDF_DIR, filename)
    text_file_path = os.path.join(text_folder, f"{filename}.txt")

    # Nếu không tìm thấy file trùng tên, thử tìm file .txt đầu tiên xuất hiện trong thư mục đó
    if not os.path.exists(text_file_path) and os.path.exists(text_folder):
        for f in os.listdir(text_folder):
            if f.lower().endswith('.txt'):
                text_file_path = os.path.join(text_folder, f)
                break

    if os.path.exists(text_file_path):
        try:
            with open(text_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return jsonify({'success': True, 'content': content})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    return jsonify({'success': False, 'message': 'File không tồn tại'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
