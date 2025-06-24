import requests
import datetime
from typing import List, Dict

def fetch_files_from_room(api_token: str, room_id: str, last_checked: str) -> List[Dict]:
    """
    指定ルームから、last_checked以降に投稿されたファイル付きメッセージを取得
    """
    url = f"https://api.chatwork.com/v2/rooms/{room_id}/files"
    headers = {"X-ChatWorkToken": api_token}
    params = {
        "force": 1  # キャッシュを無視して最新を取得
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Chatwork API error: {response.status_code} - {response.text}")

    files = response.json()

    # last_checkedより新しいファイルだけをフィルタ
    if last_checked:
        last_checked_dt = datetime.datetime.fromisoformat(last_checked)
        if last_checked_dt.tzinfo is None:
            last_checked_dt = last_checked_dt.replace(tzinfo=datetime.timezone.utc)

    files = [
        f for f in files
        if datetime.datetime.fromtimestamp(f["upload_time"], tz=datetime.timezone.utc) > last_checked_dt
    ]

    return files


def download_file(api_token: str, room_id: str, file_id: str) -> bytes:
    """
    指定ファイルIDのファイルデータを取得（バイナリ）
    """
    url = f"https://api.chatwork.com/v2/rooms/{room_id}/files/{file_id}"
    headers = {"X-ChatWorkToken": api_token}
    params = {
        "create_download_url": 1
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"File download URL fetch failed: {response.status_code}")

    file_info = response.json()
    download_url = file_info.get("download_url")

    # 実際のファイル取得
    file_data = requests.get(download_url)
    if file_data.status_code != 200:
        raise Exception("Failed to download file from Chatwork")

    return file_data.content, file_info.get("filename")


def get_new_files(api_token: str, room_id: str, last_checked: str) -> List[Dict[str, object]]:
    """
    指定ルームから last_checked 以降の新規ファイルを取得し、
    ファイル名とバイナリをまとめて返す。

    戻り値例：
    [
        {"filename": "資料1.pdf", "content": b"..."},
        {"filename": "報告書.xlsx", "content": b"..."},
    ]
    """
    new_files = fetch_files_from_room(api_token, room_id, last_checked)
    result = []

    for f in new_files:
        file_id = f["file_id"]
        file_data, filename = download_file(api_token, room_id, file_id)
        result.append({"filename": filename, "content": file_data})

    return result