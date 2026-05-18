import os
import time
import threading
from collections import deque
from flask import Flask, jsonify

app = Flask(__name__)

# 设置
SLEEP_MS = int(os.getenv("SLEEP_MS", "30"))
QPS_LIMIT = int(os.getenv("QPS_LIMIT", "150"))
WINDOW_10S = 10.0
WINDOW_1S = 1.0

_lock = threading.Lock()
_biz_hits = deque()


def _trim(now: float, window_s: float) -> None:
    cutoff = now - window_s
    while _biz_hits and _biz_hits[0] < cutoff:
        _biz_hits.popleft()


@app.get("/biz")
def biz():
    now = time.monotonic()
    with _lock:
        _biz_hits.append(now)
        _trim(now, WINDOW_10S)
        # QPS监测
        cutoff_1s = now - WINDOW_1S
        hits_last_1s = 0
        for ts in reversed(_biz_hits):
            if ts < cutoff_1s:
                break
            hits_last_1s += 1

        if hits_last_1s >= QPS_LIMIT:
            return (
                jsonify(
                    {
                        "error": "too_many_requests",
                        "qps_limit": QPS_LIMIT,
                        "hits_last_1s": hits_last_1s,
                        "num": os.environ.get("NUM", "-1")
                    }
                ),
                429,
            )

    time.sleep(max(SLEEP_MS, 0) / 1000.0)
    return jsonify({"ok": True, "num": os.environ.get("NUM", "-1"), "slept_ms": max(SLEEP_MS, 0)})


@app.get("/healthz")
def healthz():
    now = time.monotonic()
    with _lock:
        _trim(now, WINDOW_10S)
        hits_last_10s = len(_biz_hits)

    return jsonify({"status": "ok","num": os.environ.get("NUM", "-1"), "biz_requests_last_10s": hits_last_10s})


if __name__ == "__main__":
    # Dev 服务器，生产环境请使用 Gunicorn 或其他 WSGI 服务器
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")), threaded=True)
