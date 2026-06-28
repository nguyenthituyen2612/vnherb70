# -*- coding: utf-8 -*-
"""
storage.py — Ghi dữ liệu thu được theo đúng cấu trúc pipeline VNHerb-70.

Cây thư mục:
  dataset_root/
    taxonomy_master.csv
    source_log.csv
    verification_log.csv
    raw/<species_id>/<organ>/<md5>.jpg      (loài khớp danh mục)
    uncertain/<md5>.jpg                      (không khớp 70 loài)
    confusion_risk_pairs.csv
"""
import os
import csv
import json
import datetime as dt
from typing import Dict, Optional

import taxonomy

SOURCE_LOG = "source_log.csv"
VERIF_LOG = "verification_log.csv"
MASTER = "taxonomy_master.csv"
CONFUSION = "confusion_risk_pairs.csv"

SOURCE_HEADER = ["scientific_name", "common_name_vi", "organ_type", "source_id",
                 "url_goc", "license", "download_date", "image_hash_md5"]
VERIF_HEADER = ["image_hash_md5", "species_id", "scientific_name", "common_name_vi",
                "plantnet_top_name", "plantnet_top_score", "in_catalogue",
                "iqa_passed", "routing", "verified_by", "verify_date", "organ_type",
                "organ_subtype", "relative_path"]


def ensure_root(root: str):
    os.makedirs(root, exist_ok=True)
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


def save_record(root: str,
                image_bytes: bytes,
                md5: str,
                meta: Dict,
                source_id: str = "field_capture",
                url_goc: str = "",
                license: str = "",
                verified_by: str = "") -> Dict:
    """
    Lưu ảnh + append vào source_log & verification_log.
    Trả về dict gồm relative_path đã lưu.
    """
    ensure_root(root)
    tax = meta["taxonomy"]
    organ = meta["organ"]["organ_type"] or "unsorted"
    today = dt.date.today().isoformat()

    if tax["in_catalogue"]:
        sid = f"{tax['species_id']:02d}"
        rel_dir = os.path.join("raw", sid, organ)
    else:
        rel_dir = "uncertain"

    abs_dir = os.path.join(root, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)
    fname = f"{md5}.jpg"
    rel_path = os.path.join(rel_dir, fname)
    abs_path = os.path.join(abs_dir, fname)

    with open(abs_path, "wb") as f:
        f.write(image_bytes)

    # also dump sidecar json
    with open(abs_path + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # append source_log (KHÔNG ghi nếu chưa có license — theo P2)
    if license.strip():
        with open(os.path.join(root, SOURCE_LOG), "a", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerow([
                tax["scientific_name"] or "", tax["common_name_vi"] or "", organ,
                source_id, url_goc, license, today, md5,
            ])
        source_logged = True
    else:
        source_logged = False

    # append verification_log
    pn = meta["identification"]
    top = pn["candidates"][0] if pn["candidates"] else {}
    with open(os.path.join(root, VERIF_LOG), "a", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerow([
            md5, tax["species_id"] or "", tax["scientific_name"] or "",
            tax["common_name_vi"] or "", top.get("scientific_name", ""),
            top.get("score", ""), tax["in_catalogue"], meta["iqa"]["passed"] if meta["iqa"] else "",
            meta["routing"]["destination"], verified_by, today,
            organ, meta["organ"]["organ_subtype"] or "", rel_path,
        ])

    return {"relative_path": rel_path, "abs_path": abs_path,
            "source_logged": source_logged}
