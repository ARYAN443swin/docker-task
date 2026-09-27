from flask import Flask
import os, socket

app = Flask(__name__)

@app.route("/")
def index():
    return f"""
    <html><body style="font-family:system-ui;max-width:700px;margin:3rem auto">
      <h1>SWE40006 Containerised Flask App</h1>
      <p>Running inside a Docker container.</p>
      <ul>
        <li>Hostname: {socket.gethostname()}</li>
        <li>Environment: {os.getenv('APP_ENV', 'not set')}</li>
      </ul>
    </body></html>
    """

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)