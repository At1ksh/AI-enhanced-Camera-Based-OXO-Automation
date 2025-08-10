from flask import Flask, request, render_template_string
import os

UPLOAD_DIR = r"D:\FilesFromOtherSystem"
app = Flask(__name__)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        uploaded_filenames = []
        for file in uploaded_files:
            if file.filename:
                save_path = os.path.join(UPLOAD_DIR, file.filename)
                file.save(save_path)
                uploaded_filenames.append(file.filename)
        return render_template_string(SUCCESS_HTML, files=uploaded_filenames)

    return render_template_string(UPLOAD_FORM)

UPLOAD_FORM = '''
<!doctype html>
<html lang="en">
<head>
    <title>Upload Files</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { background-color: #f5f7fa; padding-top: 60px; }
        .upload-box {
            background: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
<div class="container">
    <div class="upload-box text-center">
        <h2 class="mb-4">📁 Upload Files to This PC</h2>
        <form method="POST" enctype="multipart/form-data">
            <div class="form-group">
                <input type="file" name="file" class="form-control-file" multiple required>
            </div>
            <button type="submit" class="btn btn-primary">Upload Files</button>
        </form>
    </div>
</div>
</body>
</html>
'''

SUCCESS_HTML = '''
<!doctype html>
<html lang="en">
<head>
    <title>Upload Successful</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { background-color: #e9f7ef; padding-top: 60px; }
        .success-box {
            background: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
<div class="container">
    <div class="success-box text-center">
        <h2 class="mb-4 text-success">✅ Upload Successful!</h2>
        <p>The following files have been uploaded:</p>
        <ul class="list-group mb-4">
            {% for file in files %}
            <li class="list-group-item">{{ file }}</li>
            {% endfor %}
        </ul>
        <a href="/upload" class="btn btn-secondary">Upload More</a>
    </div>
</div>
</body>
</html>
'''

if __name__ == '__main__':
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
