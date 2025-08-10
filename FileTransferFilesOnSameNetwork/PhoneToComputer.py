from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi, os

UPLOAD_DIR = r"D:\ImagesFromPhone"
os.makedirs(UPLOAD_DIR, exist_ok=True)    # or your target path

class UploadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        html = '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>📤 Upload Files</title>
                <style>
                    body {
                        font-family: 'Segoe UI', sans-serif;
                        background: #f3f4f6;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .upload-box {
                        background: white;
                        padding: 30px 40px;
                        border-radius: 12px;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
                        text-align: center;
                        max-width: 400px;
                        width: 100%;
                    }
                    h2 {
                        color: #333;
                        margin-bottom: 20px;
                    }
                    input[type="file"] {
                        display: none;
                    }
                    label {
                        background-color: #4f46e5;
                        color: white;
                        padding: 12px 24px;
                        border-radius: 6px;
                        cursor: pointer;
                        display: inline-block;
                        margin-bottom: 20px;
                    }
                    label:hover {
                        background-color: #4338ca;
                    }
                    .btn-upload {
                        padding: 10px 24px;
                        background: #22c55e;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        cursor: pointer;
                    }
                    .btn-upload:hover {
                        background: #16a34a;
                    }
                    footer {
                        margin-top: 20px;
                        font-size: 13px;
                        color: #888;
                    }
                </style>
            </head>
            <body>
                <div class="upload-box">
                    <h2>📸 Upload Your Photos</h2>
                    <form enctype="multipart/form-data" method="post">
                        <label for="file">Choose Images</label><br>
                        <input id="file" name="files" type="file" accept="image/*" multiple />
                        <br><br>
                        <input class="btn-upload" type="submit" value="Upload"/>
                    </form>
                    <footer>FAP File Uploader • LAN Transfer</footer>
                </div>
            </body>
            </html>
        '''
        self.wfile.write(html.encode('utf-8'))


    def do_POST(self):
        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid content type")
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )

        if "files" not in form:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No files found in form data")
            return

        files = form["files"]
        if not isinstance(files, list):
            files = [files]

        uploaded = []
        for file_item in files:
            if file_item.filename:
                filename = os.path.basename(file_item.filename)
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(file_item.file.read())
                uploaded.append(filename)

        self.send_response(200)
        self.end_headers()
        if uploaded:
            msg = "<h3>✅ Uploaded:</h3><ul>" + "".join(f"<li>{name}</li>" for name in uploaded) + "</ul>"
        else:
            msg = "<h3>⚠️ No valid files uploaded</h3>"
        self.wfile.write(msg.encode('utf-8'))


if __name__ == "__main__":
    PORT = 8000
    print(f"📡 Upload server running ")
    server = HTTPServer(('', PORT), UploadHandler)
    server.serve_forever()
