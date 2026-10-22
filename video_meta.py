"""Probe every labeled video with ffprobe and cache duration/fps/resolution to a CSV."""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

root = Path(sys.argv[1])
out = Path(sys.argv[2])

def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
         "-show_entries", "stream=width,height,avg_frame_rate,nb_read_packets,codec_name:format=duration,size",
         "-of", "json", str(p)], capture_output=True, text=True)
    d = json.loads(r.stdout)
    s, f = d["streams"][0], d["format"]
    num, den = map(int, s["avg_frame_rate"].split("/"))
    rel = p.relative_to(root).parts
    return dict(id=p.stem, tract=rel[0], category=rel[1], folder=rel[2],
                duration_s=float(f["duration"]), size_mb=int(f["size"]) / 1e6,
                fps=num / den if den else None, frames=int(s["nb_read_packets"]),
                width=s["width"], height=s["height"], codec=s["codec_name"])

if __name__ == "__main__":
    import pandas as pd
    files = sorted(root.rglob("*.avi"))
    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(probe, files))
    pd.DataFrame(rows).to_csv(out, index=False)
    print(len(rows), "videos ->", out)
