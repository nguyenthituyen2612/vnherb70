# -*- coding: utf-8 -*-
"""
app.py — VNHerb-70 · Trạm thu mẫu ảnh cây thuốc
Pipeline rút gọn trong 1 app: chụp/tải ảnh -> P5 IQA -> P3 PlantNet (đối chiếu 70 loài)
-> P4 gán bộ phận -> ghi raw/ + source_log.csv + verification_log.csv

Chạy:  streamlit run app.py
"""
import io
import json
import datetime as dt

import streamlit as st
from PIL import Image

import taxonomy
import iqa as iqa_mod
import plantnet
import storage

st.set_page_config(page_title="VNHerb-70 · Thu mẫu cây thuốc",
                   page_icon="🌿", layout="centered")

# ---------------- style ----------------
st.markdown("""
<style>
  .stApp { background:#f3efe4; }
  h1,h2,h3 { font-family:Georgia,serif; color:#1c2418; }
  .eyebrow { font-family:ui-monospace,monospace; font-size:11px; letter-spacing:.3em;
             text-transform:uppercase; color:#3f6b3a; margin-bottom:2px; }
  .pillpass{background:#3f6b3a18;color:#274d27;border:1px solid #3f6b3a;
            padding:2px 8px;border-radius:20px;font-size:11px;font-family:monospace}
  .pillwarn{background:#b88a2e18;color:#8a6a1f;border:1px solid #b88a2e;
            padding:2px 8px;border-radius:20px;font-size:11px;font-family:monospace}
  .pillfail{background:#a8542d18;color:#a8542d;border:1px solid #a8542d;
            padding:2px 8px;border-radius:20px;font-size:11px;font-family:monospace}
  .meta-note{font-size:12px;color:#4b5340;font-style:italic}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="eyebrow">VNHerb-70 · QĐ4664/QĐ-BYT 2014</p>', unsafe_allow_html=True)
st.title("Trạm thu mẫu ảnh cây thuốc")
st.caption("Chụp một bức — app chạy IQA, định loại PlantNet, gán bộ phận và ghi vào dataset.")

# ---------------- Google Drive config (từ st.secrets nếu có) ----------------
try:
    if "gcp_service_account" in st.secrets and "gdrive_folder_id" in st.secrets:
        _gdrive_config = {
            "credentials": dict(st.secrets["gcp_service_account"]),
            "folder_id": st.secrets["gdrive_folder_id"],
        }
    else:
        _gdrive_config = None
except Exception:
    _gdrive_config = None

# ---------------- session ----------------
ss = st.session_state
ss.setdefault("img_bytes", None)
ss.setdefault("img", None)
ss.setdefault("md5", None)
ss.setdefault("iqa", None)
ss.setdefault("pn", None)
ss.setdefault("matched_id", None)

# ---------------- sidebar config ----------------
with st.sidebar:
    st.subheader("Cấu hình")
    dataset_root = st.text_input("Thư mục dataset", value="VNHerb70_dataset",
                                 help="Nơi lưu raw/, uncertain/, các file log.")
    api_key = st.text_input("PlantNet API key", type="password",
                            help="Lấy tại my.plantnet.org. Không bắt buộc để chạy IQA.")
    collector = st.text_input("Người thu mẫu / xác nhận", value="")
    st.divider()
    st.subheader("Nguồn ảnh (P2)")
    source_id = st.text_input("source_id", value="field_capture")
    url_goc = st.text_input("url_goc (nếu lấy từ web)", value="")
    license_ = st.text_input("license", value="",
                             help="BẮT BUỘC để ghi vào source_log.csv (theo P2).")
    st.caption("Không có license → ảnh vẫn lưu & ghi verification_log, "
               "nhưng source_log.csv bỏ qua đúng quy tắc P2.")
    st.divider()
    if _gdrive_config:
        st.success("☁ Google Drive: đã kết nối")
    else:
        st.caption("☁ Google Drive: chưa cấu hình\n(thêm secrets để bật)")

# ---------------- P1 capture ----------------
st.header("1 · Chụp / tải ảnh mẫu")
tab_cam, tab_up = st.tabs(["📷 Chụp bằng camera", "⤓ Tải ảnh"])
new_bytes = None
with tab_cam:
    shot = st.camera_input("Căn cây thuốc chiếm phần lớn khung hình")
    if shot is not None:
        new_bytes = shot.getvalue()
with tab_up:
    up = st.file_uploader("Chọn ảnh", type=["jpg", "jpeg", "png", "webp"])
    if up is not None:
        new_bytes = up.getvalue()

if new_bytes is not None:
    md5 = plantnet.md5_bytes(new_bytes)
    if md5 != ss.md5:                       # ảnh mới -> reset chuỗi phân tích
        ss.img_bytes = new_bytes
        ss.md5 = md5
        ss.img = Image.open(io.BytesIO(new_bytes)).convert("RGB")
        ss.iqa = iqa_mod.analyze(ss.img)    # chạy IQA ngay
        ss.pn = None
        ss.matched_id = None

if ss.img is not None:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(ss.img, caption=f"md5 {ss.md5[:16]}…", use_container_width=True)
    with col2:
        st.metric("Kích thước", f"{ss.img.size[0]}×{ss.img.size[1]} px")
        st.metric("Dung lượng", f"{len(ss.img_bytes)/1024:.0f} KB")
        st.code(ss.md5, language=None)

# ---------------- P5 IQA ----------------
if ss.iqa is not None:
    st.header("P5 · Chất lượng ảnh (IQA)")
    res = ss.iqa
    for c in res.checks:
        cls = {"pass": "pillpass", "warn": "pillwarn", "fail": "pillfail"}[c.status]
        cc1, cc2, cc3 = st.columns([3, 1.2, 1])
        cc1.write(c.label)
        cc2.write(f"`{c.display}`")
        cc3.markdown(f'<span class="{cls}">{c.status}</span>', unsafe_allow_html=True)
    if res.passed:
        st.success("quality_pass — ảnh đạt IQA, chuyển sang định loại.")
    else:
        bad = ", ".join(c.label.split(" (")[0] for c in res.checks if c.status == "fail")
        st.warning(f"Cảnh báo IQA: {bad} chưa đạt. Vẫn tiếp tục được — "
                   "cờ cảnh báo sẽ ghi vào metadata.")

# ---------------- P3 PlantNet ----------------
if ss.img is not None:
    st.header("P3 · Định loại (PlantNet) + đối chiếu 70 loài")
    organ_hint = st.selectbox("Gợi ý cơ quan cho PlantNet",
                              ["auto", "leaf", "flower", "fruit", "bark"], index=0)
    if st.button("🔎 Gửi ảnh tới PlantNet", disabled=not api_key):
        with st.spinner("Đang gọi PlantNet…"):
            ss.pn = plantnet.identify(ss.img_bytes, api_key, organ=organ_hint)
        if ss.pn["ok"] and ss.pn["results"]:
            for r in ss.pn["results"]:
                t = taxonomy.find_by_scientific(r["scientific_name"])
                if t:
                    ss.matched_id = t.id
                    break
    if not api_key:
        st.info("Nhập PlantNet API key ở thanh bên để định loại tự động. "
                "Bạn vẫn có thể chọn loài thủ công bên dưới.")

    if ss.pn and ss.pn.get("error"):
        st.error(f"Lỗi PlantNet: {ss.pn['error']}")

    if ss.pn and ss.pn.get("results"):
        st.caption("Ứng viên PlantNet (✓ = nằm trong 70 loài QĐ4664):")
        for i, r in enumerate(ss.pn["results"][:8], 1):
            t = taxonomy.find_by_scientific(r["scientific_name"])
            mark = f"✓ #{t.id} {t.vi}" if t else "— ngoài danh mục"
            cc1, cc2, cc3 = st.columns([3, 1.4, 1])
            cc1.markdown(f"**{i}.** *{r['scientific_name']}*")
            cc2.markdown(f"`{r['score']*100:.1f}%`")
            cc3.write(mark)
            st.progress(min(1.0, r["score"]))

    # manual / confirmed pick
    options = [("", "— uncertain (không khớp 70 loài) —")] + \
              [(t.id, f"#{t.id} · {t.vi} — {t.sci}") for t in taxonomy.TAXA]
    labels = [o[1] for o in options]
    default_idx = 0
    if ss.matched_id:
        default_idx = next((k for k, o in enumerate(options) if o[0] == ss.matched_id), 0)
    pick = st.selectbox("Loài xác nhận (chuyên gia)", labels, index=default_idx)
    chosen_id = options[labels.index(pick)][0]
    chosen = taxonomy.BY_ID.get(chosen_id) if chosen_id else None

    if chosen:
        st.markdown(f"**Họ:** {chosen.family}  ·  **Bộ phận dùng (QĐ4664):** {chosen.organs_qd}")
        conf = taxonomy.confusion_for(chosen.id)
        if conf:
            warn = "; ".join(f"#{cid} {vi}" for cid, vi, _ in conf)
            st.warning(f"⚠ Loài dễ nhầm (P6) — kiểm tra kỹ với: {warn}")
else:
    chosen = None
    chosen_id = ""

# ---------------- P4 organ ----------------
chosen_organ = None
chosen_sub = None
if ss.img is not None:
    st.header("P4 · Gán nhãn bộ phận")
    organ_labels = [f"{k} · {vi}" for k, vi in taxonomy.ORGAN_TYPES]
    organ_keys = [k for k, _ in taxonomy.ORGAN_TYPES]
    sel = st.radio("organ_type (chọn bộ phận chiếm phần lớn ảnh)",
                   organ_labels, horizontal=True, index=0)
    chosen_organ = organ_keys[organ_labels.index(sel)]
    subs = taxonomy.ORGAN_SUBTYPES.get(chosen_organ)
    if subs:
        chosen_sub = st.selectbox("organ_subtype", ["—"] + subs)
        if chosen_sub == "—":
            chosen_sub = None

# ---------------- build metadata + save ----------------
def build_meta():
    sp = chosen
    iqa_passed = ss.iqa.passed if ss.iqa else False
    if sp:
        routing = "verified_pending_expert" if iqa_passed else "quality_flagged"
        folder = f"raw/{sp.id:02d}/{chosen_organ or 'unsorted'}/"
    else:
        routing = "uncertain"
        folder = "uncertain/"
    cands = []
    if ss.pn and ss.pn.get("results"):
        cands = [{"scientific_name": r["scientific_name"], "score": round(r["score"], 4)}
                 for r in ss.pn["results"][:5]]
    return {
        "schema": "vnherb70.capture.v1",
        "capture_timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "image": {"hash_md5": ss.md5, "width_px": ss.img.size[0],
                  "height_px": ss.img.size[1], "mime": "image/jpeg"},
        "taxonomy": {
            "species_id": sp.id if sp else None,
            "common_name_vi": sp.vi if sp else None,
            "scientific_name": sp.sci if sp else None,
            "family": sp.family if sp else None,
            "organs_qd4664": sp.organs_qd if sp else None,
            "in_catalogue": bool(sp),
            "source": "taxonomy_master.csv · QĐ4664/QĐ-BYT 2014",
        },
        "identification": {
            "tool": "PlantNet API v2",
            "organ_hint": locals().get("organ_hint", "auto") if ss.img else "auto",
            "top_score": cands[0]["score"] if cands else None,
            "candidates": cands,
            "manual_confirmation_required": True,
        },
        "organ": {"organ_type": chosen_organ, "organ_subtype": chosen_sub},
        "iqa": ss.iqa.to_dict() if ss.iqa else None,
        "routing": {"destination": routing, "folder": folder},
    }

if ss.img is not None:
    st.header("⤓ Metadata & lưu vào dataset")
    meta = build_meta()
    st.json(meta, expanded=False)

    cdl, csave = st.columns([1, 1])
    with cdl:
        st.download_button("Tải metadata JSON",
                           data=json.dumps(meta, ensure_ascii=False, indent=2),
                           file_name=f"vnherb70_{ss.md5[:8]}.json",
                           mime="application/json")
    with csave:
        if st.button("💾 Lưu vào dataset", type="primary"):
            info = storage.save_record(
                dataset_root, ss.img_bytes, ss.md5, meta,
                source_id=source_id, url_goc=url_goc,
                license=license_, verified_by=collector,
                gdrive_config=_gdrive_config,
            )
            if info["backend"] == "gdrive":
                st.success(f"☁ Đã lưu lên Google Drive → `{info['relative_path']}`")
            else:
                st.success(f"Đã lưu local → `{info['relative_path']}`")
            if info["source_logged"]:
                st.caption("✓ Đã ghi source_log.csv (có license).")
            else:
                st.caption("⚠ Bỏ qua source_log.csv vì thiếu license (đúng quy tắc P2). "
                           "verification_log.csv vẫn được ghi.")

st.divider()
st.caption("VNHerb-70 · 70 loài cây thuốc nam · Ảnh chỉ route 'pending_expert' — "
           "cần chuyên gia thực vật/dược liệu xác nhận trước khi vào tập verified (P3).")
