# -*- coding: utf-8 -*-
"""
plantnet.py — P3: Gọi PlantNet API v2 để định loại sơ bộ.
"""
import hashlib
import requests
from typing import List, Dict, Optional

PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/{project}"


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def identify(image_bytes: bytes,
             api_key: str,
             organ: str = "auto",
             project: str = "all",
             nb_results: int = 8,
             lang: str = "vi",
             timeout: int = 30) -> Dict:
    """
    Gửi ảnh tới PlantNet. Trả về dict:
      {ok: bool, results: [...], error: str|None, raw: {...}}
    Mỗi result: {scientific_name, genus, score}
    """
    if not api_key:
        return {"ok": False, "error": "Thiếu API key", "results": [], "raw": None}

    url = PLANTNET_URL.format(project=project)
    params = {"api-key": api_key, "nb-results": nb_results, "lang": lang}
    files = {"images": ("sample.jpg", image_bytes, "image/jpeg")}
    data = {"organs": organ if organ else "auto"}

    try:
        resp = requests.post(url, params=params, files=files, data=data, timeout=timeout)
    except requests.RequestException as e:
        return {"ok": False, "error": f"Lỗi kết nối: {e}", "results": [], "raw": None}

    if resp.status_code != 200:
        snippet = resp.text[:160]
        return {"ok": False,
                "error": f"HTTP {resp.status_code} · {snippet}",
                "results": [], "raw": None}

    raw = resp.json()
    results = []
    for r in raw.get("results", []):
        sp = r.get("species", {})
        sci = sp.get("scientificNameWithoutAuthor") or sp.get("scientificName") or ""
        genus = (sp.get("genus") or {}).get("scientificNameWithoutAuthor") or (sci.split()[0] if sci else "")
        common = sp.get("commonNames") or []
        results.append({
            "scientific_name": sci,
            "genus": genus,
            "common_names": common,
            "score": float(r.get("score", 0.0)),
        })
    return {"ok": True, "error": None, "results": results, "raw": raw}
