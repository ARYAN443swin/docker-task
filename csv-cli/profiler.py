#!/usr/bin/env python3
import argparse, csv, json, logging, os, statistics, sys
from datetime import datetime, timezone

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("csv-profiler")

def profile_file(path):
    log.info("Profiling %s", path)
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        raise ValueError("file is empty")
    headers, data = rows[0], rows[1:]
    cols = []
    for i, name in enumerate(headers):
        vals = [r[i].strip() for r in data if i < len(r) and r[i].strip()]
        nums = []
        for v in vals:
            try:
                nums.append(float(v))
            except ValueError:
                pass
        numeric = bool(vals) and len(nums) == len(vals)
        col = {
            "column": name,
            "type": "numeric" if numeric else "text",
            "nulls": len(data) - len(vals),
            "distinct": len(set(vals)),
        }
        if numeric:
            col.update(min=min(nums), max=max(nums), mean=statistics.mean(nums))
        cols.append(col)
    log.info("Profiled %d columns across %d rows", len(headers), len(data))
    return {"file": os.path.basename(path), "rows": len(data),
            "columns": len(headers),
            "profiled_at": datetime.now(timezone.utc).isoformat(),
            "column_profiles": cols}

def main():
    p = argparse.ArgumentParser(description="Profile CSV files from a mounted directory.")
    p.add_argument("--input", default="/data/input", help="directory of CSV files")
    p.add_argument("--output", default="/data/output", help="directory for JSON reports")
    args = p.parse_args()

    if not os.path.isdir(args.input):
        log.error("Input directory %s not found. Did you mount a volume?", args.input)
        sys.exit(1)
    os.makedirs(args.output, exist_ok=True)

    files = [f for f in sorted(os.listdir(args.input)) if f.lower().endswith(".csv")]
    if not files:
        log.warning("No CSV files found in %s", args.input)
        sys.exit(0)

    log.info("Found %d file(s)", len(files))
    failures = 0
    for name in files:
        try:
            result = profile_file(os.path.join(args.input, name))
            out = os.path.join(args.output, name.rsplit(".", 1)[0] + "-profile.json")
            with open(out, "w") as fh:
                json.dump(result, fh, indent=2)
            log.info("Wrote %s", out)
        except Exception as e:
            log.error("Failed on %s: %s", name, e)
            failures += 1

    log.info("Done. %d succeeded, %d failed", len(files) - failures, failures)
    sys.exit(1 if failures else 0)

if __name__ == "__main__":
    main()