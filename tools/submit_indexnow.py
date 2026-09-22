#!/usr/bin/env python3
"""Notify Bing/Yandex-compatible IndexNow endpoints of the current sitemap.

The key file must already be live at https://qishanlabs.com/<key>.txt.

    python3 tools/submit_indexnow.py
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"
KEY = "3b98754f544a3bccd9366bd26665f6da"
HOST = "qishanlabs.com"
ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
]


def urls() -> list[str]:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.parse(DIST / "sitemap.xml").getroot()
    return [node.text for node in root.findall("s:url/s:loc", ns) if node.text]


def post(endpoint: str, payload: dict) -> tuple[int | str, str]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "QishanLabs-IndexNow/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read()[:200].decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()[:200].decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


def main() -> int:
    loc = f"https://{HOST}/{KEY}.txt"
    payload = {"host": HOST, "key": KEY, "keyLocation": loc, "urlList": urls()}
    print(f"submitting {len(payload['urlList'])} urls")
    ok = True
    for endpoint in ENDPOINTS:
        status, detail = post(endpoint, payload)
        print(f"  {status}  {endpoint}  {detail!r}")
        if status not in (200, 202):
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
