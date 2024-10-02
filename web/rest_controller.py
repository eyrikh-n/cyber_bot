import threading

from flask import Flask

web = Flask(__name__)

@web.route("/health")
def health():
    return '{"Up!"}'

class RestController:

    def __init__(self, port=5000):
        self.port = port

    def run(self):
        print(f"Web-server starting on port {self.port}")
        web.run(host='0.0.0.0', port=self.port)

    def run_background(self):
        threading.Thread(target=self.run, daemon=True).start()
