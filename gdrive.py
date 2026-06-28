# -*- coding: utf-8 -*-
"""
gdrive.py — Upload ảnh và CSV lên Google Drive bằng Service Account.
"""
import io
import csv

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload, MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def build_service(creds_dict: dict):
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def get_or_create_folder(service, parent_id: str, name: str) -> str:
    safe = name.replace("'", "\\'")
    q = (f"name='{safe}' and '{parent_id}' in parents "
         f"and mimeType='application/vnd.google-apps.folder' and trashed=false")
    res = service.files().list(q=q, fields="files(id)", pageSize=1).execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]
    body = {"name": name, "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id]}
    return service.files().create(body=body, fields="id").execute()["id"]


def resolve_path(service, root_id: str, parts: list) -> str:
    """Tạo nested folder theo danh sách parts, trả về folder_id lá."""
    fid = root_id
    for part in parts:
        fid = get_or_create_folder(service, fid, part)
    return fid


def upload_bytes(service, folder_id: str, filename: str,
                 data: bytes, mime: str = "application/octet-stream") -> str:
    safe = filename.replace("'", "\\'")
    q = f"name='{safe}' and '{folder_id}' in parents and trashed=false"
    res = service.files().list(q=q, fields="files(id)", pageSize=1).execute()
    media = MediaInMemoryUpload(data, mimetype=mime)
    if res.get("files"):
        fid = res["files"][0]["id"]
        service.files().update(fileId=fid, media_body=media).execute()
        return fid
    body = {"name": filename, "parents": [folder_id]}
    return service.files().create(body=body, media_body=media, fields="id").execute()["id"]


def _csv_line(row: list) -> str:
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n").writerow(row)
    return buf.getvalue()


def append_csv(service, folder_id: str, filename: str, header: list, row: list):
    """Append một dòng vào CSV trên Drive; tạo file với header nếu chưa tồn tại."""
    safe = filename.replace("'", "\\'")
    q = f"name='{safe}' and '{folder_id}' in parents and trashed=false"
    res = service.files().list(q=q, fields="files(id)", pageSize=1).execute()
    files = res.get("files", [])

    if files:
        file_id = files[0]["id"]
        req = service.files().get_media(fileId=file_id)
        buf = io.BytesIO()
        dl = MediaIoBaseDownload(buf, req)
        done = False
        while not done:
            _, done = dl.next_chunk()
        existing = buf.getvalue().decode("utf-8-sig")
        new_content = existing + _csv_line(row)
        media = MediaInMemoryUpload(new_content.encode("utf-8-sig"), mimetype="text/csv")
        service.files().update(fileId=file_id, media_body=media).execute()
    else:
        new_content = _csv_line(header) + _csv_line(row)
        media = MediaInMemoryUpload(new_content.encode("utf-8-sig"), mimetype="text/csv")
        body = {"name": filename, "parents": [folder_id]}
        service.files().create(body=body, media_body=media, fields="id").execute()
