# Локальный сервер для просмотра: отдаёт page.html и по адресу без .html
import http.server
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path) and not self.path.startswith("/admin"):
            # /page -> /page.html
            clean = self.path.split("?", 1)[0].split("#", 1)[0].rstrip("/")
            candidate = clean + ".html"
            if os.path.exists(self.translate_path(candidate)):
                self.path = candidate
        return super().send_head()

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 8123), Handler)
    print("Serving on http://127.0.0.1:8123")
    server.serve_forever()
