# -*- coding: utf-8 -*-
"""
storage.py — Ghi dữ liệu thu được theo cấu trúc pipeline VNHerb-70.

Nếu gdrive_config được truyền vào → lưu thẳng lên Google Drive.
Nếu không → lưu vào local filesystem (fallback khi chạy offline).

Cấu trúc thư mục (local hoặc Drive):
  raw/<species_id>/<organ>/<md5>.jpg
  raw/<species_id>/<organ>/<md5>.jpg.json
  uncertain/<md5>.jpg
  source_log.csv
  verification_log.csv
"""
import os
import csv
import json
import datetime as dt
from typing import Dict, List, Optional

import taxonomy

SOURCE_LOG = "source_log.csv"
VERIF_LOG  = "verification_log.csv"
MASTER     = "taxonomy_master.csv"
CONFUSION  = "confusion_risk_pairs.csv"

SOURCE_HEADER = ["scientific_name", "common_name_vi", "organ_type", "source_id",
                 "url_goc", "license", "download_date", "image_hash_md5"]
VERIF_HEADER  = ["image_hash_md5", "species_id", "scientific_name", "common_name_vi",
                 "plantnet_top_name", "plantnet_top_score", "in_catalogue",
                 "iqa_passed", "routing", "verified_by", "verify_date", "organ_type",
                 "organ_subtype", "relative_path"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_record(root: str,
                image_bytes: bytes,
                md5: str,
                meta: Dict,
                source_id: str = "field_capture",
                url_goc: str = "",
                license: str = "",
                verified_by: str = "",
                gdrive_config: Optional[Dict] = None) -> Dict:
    """
    Lưu ảnh + log.
    - gdrive_config có giá trị  → lưu thẳng lên Google Drive.
    - gdrive_config là None      → lưu vào thư mục local `root`.
    Trả về dict: relative_path, source_logged, backend ('gdrive'|'local').
    """
    tax   = meta["taxonomy"]
    organ = meta["organ"]["organ_type"] or "unsorted"
    today = dt.date.today().isoformat()
    fname = f"{md5}.jpg"

    if tax["in_catalogue"]:
        dir_parts = ["raw", f"{tax['species_id']:02d}", organ]
    else:
        dir_parts = ["uncertain"]

    rel_path = "/".join(dir_parts + [fname])

    pn  = meta["identification"]
    top = pn["candidates"][0] if pn["candidates"] else {}

    source_logged = bool(license.strip())
    source_row: Optional[List] = ([
        tax["scientific_name"] or "", tax["common_name_vi"] or "", organ,
        source_id, url_goc, license, today, md5,
    ] if source_logged else None)

    verif_row: List = [
        md5, tax["species_id"] or "", tax["scientific_name"] or "",
        tax["common_name_vi"] or "", top.get("scientific_name", ""),
        top.get("score", ""), tax["in_catalogue"],
        meta["iqa"]["passed"] if meta["iqa"] else "",
        meta["routing"]["destination"], verified_by, today,
        organ, meta["organ"]["organ_subtype"] or "", rel_path,
    ]

    if gdrive_config:
        return _save_gdrive(gdrive_config, dir_parts, fname, rel_path,
                            image_bytes, meta, source_row, verif_row, source_logged)
    return _save_local(root, dir_parts, fname, rel_path,
                       image_bytes, meta, source_row, verif_row, source_logged)


# ---------------------------------------------------------------------------
# Drive backend
# ---------------------------------------------------------------------------

def _save_gdrive(config, dir_parts, fname, rel_path,
                 image_bytes, meta, source_row, verif_row, source_logged) -> Dict:
    import gdrive as gd
    svc     = gd.build_service(config["credentials"])
    root_id = config["folder_id"]

    folder_id = gd.resolve_path(svc, root_id, dir_parts)
    gd.upload_bytes(svc, folder_id, fname, image_bytes, "image/jpeg")
    gd.upload_bytes(svc, folder_id, fname + ".json",
                    json.dumps(meta, ensure_ascii=False, indent=2).encode("utf-8"),
                    "application/json")

    if source_row:
        gd.append_csv(svc, root_id, SOURCE_LOG, SOURCE_HEADER, source_row)
    gd.append_csv(svc, root_id, VERIF_LOG, VERIF_HEADER, verif_row)

    return {"relative_path": rel_path, "source_logged": source_logged, "backend": "gdrive"}


# ---------------------------------------------------------------------------
# Local backend
# ---------------------------------------------------------------------------

def _save_local(root, dir_parts, fname, rel_path,
                image_bytes, meta, source_row, verif_row, source_logged) -> Dict:
    _ensure_root(root)
    abs_dir  = os.path.join(root, *dir_parts)
    abs_path = os.path.join(abs_dir, fname)
    os.makedirs(abs_dir, exist_ok=True)

    with open(abs_path, "wb") as f:
        f.write(image_bytes)
    with open(abs_path + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    if source_row:
        with open(os.path.join(root, SOURCE_LOG), "a", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerow(source_row)
    with open(os.path.join(root, VERIF_LOG), "a", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerow(verif_row)

    return {"relative_path": rel_path, "abs_path": abs_path,
            "source_logged": source_logged, "backend": "local"}


# ---------------------------------------------------------------------------
# Local init helpers
# ---------------------------------------------------------------------------

def _ensure_root(root: str):
    os.makedirs(os.path.join(root, "raw"), exist_ok=True)
    os.makedirs(os.path.join(root, "uncertain"), exist_ok=True)
    _write_master(root)
    _write_confusion(root)
    _ensure_log(os.path.join(root, SOURCE_LOG), SOURCE_HEADER)
    _ensure_log(os.path.join(root, VERIF_LOG), VERIF_HEADER)


def _ensure_log(path: str, header):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerow(header)


def _write_master(root: str):
    path = os.path.join(root, MASTER)
    if os.path.exists(path):
        return
    header, rows = taxonomy.to_master_rows()
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def _write_confusion(root: str):
    path = os.path.join(root, CONFUSION)
    if os.path.exists(path):
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["species_a_id", "species_a_vi", "species_b_id", "species_b_vi", "note"])
        for a, b, note in taxonomy.CONFUSION_PAIRS:
            w.writerow([a, taxonomy.BY_ID[a].vi, b, taxonomy.BY_ID[b].vi, note])
