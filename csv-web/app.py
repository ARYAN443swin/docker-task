from flask import Flask, request, render_template_string
import os, csv, io, statistics

app = Flask(__name__)
MAX_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
APP_ENV = os.getenv("APP_ENV", "development")

PAGE = """
<html><head><title>CSV Profiler</title>
<style>body{font-family:system-ui;max-width:900px;margin:2rem auto;padding:0 1rem}
table{border-collapse:collapse;width:100%;margin-top:1rem}
td,th{border:1px solid #ccc;padding:.4rem;text-align:left}</style></head>
<body>
<h1>CSV Dataset Profiler</h1>
<p>Environment: {{ env }} | Max upload: {{ maxmb }} MB</p>
<form method="post" enctype="multipart/form-data">
  <input type="file" name="file" accept=".csv" required>
  <button type="submit">Profile</button>
</form>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
{% if rows %}
<p>{{ nrows }} rows, {{ ncols }} columns</p>
<table><tr><th>Column</th><th>Type</th><th>Nulls</th><th>Distinct</th><th>Min</th><th>Max</th><th>Mean</th></tr>
{% for r in rows %}<tr><td>{{ r.name }}</td><td>{{ r.type }}</td><td>{{ r.nulls }}</td>
<td>{{ r.distinct }}</td><td>{{ r.min }}</td><td>{{ r.max }}</td><td>{{ r.mean }}</td></tr>{% endfor %}
</table>{% endif %}
</body></html>
"""

def profile(text):
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        raise ValueError("empty file")
    headers, data = rows[0], rows[1:]
    out = []
    for i, name in enumerate(headers):
        vals = [r[i].strip() for r in data if i < len(r) and r[i].strip()]
        nulls = len(data) - len(vals)
        nums = []
        for v in vals:
            try:
                nums.append(float(v))
            except ValueError:
                pass
        is_num = bool(vals) and len(nums) == len(vals)
        out.append({
            "name": name,
            "type": "numeric" if is_num else "text",
            "nulls": f"{nulls} ({nulls/len(data)*100:.1f}%)" if data else "0",
            "distinct": len(set(vals)),
            "min": f"{min(nums):.3f}" if is_num else "-",
            "max": f"{max(nums):.3f}" if is_num else "-",
            "mean": f"{statistics.mean(nums):.3f}" if is_num else "-",
        })
    return out, len(data), len(headers)

@app.route("/", methods=["GET", "POST"])
def index():
    ctx = {"env": APP_ENV, "maxmb": MAX_MB, "rows": None, "error": None}
    if request.method == "POST":
        f = request.files.get("file")
        if not f:
            ctx["error"] = "No file selected."
        else:
            blob = f.read()
            if len(blob) > MAX_MB * 1024 * 1024:
                ctx["error"] = f"File exceeds {MAX_MB} MB."
            else:
                try:
                    rows, n, c = profile(blob.decode("utf-8", errors="replace"))
                    ctx.update(rows=rows, nrows=n, ncols=c)
                except Exception as e:
                    ctx["error"] = f"Could not parse: {e}"
    return render_template_string(PAGE, **ctx)

@app.route("/health")
def health():
    return {"status": "healthy", "env": APP_ENV}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)