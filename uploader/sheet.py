from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime, timezone, timedelta

# スプレッドシートの情報
SPREADSHEET_ID = '1TbxilNt4xeYRqs-lFbrSiK8F8Dogv4rZfNCW9YGUj_k'
SHEET_NAME = 'シート1'
RANGE_NAME = f"{SHEET_NAME}!A2:D"

def read_room_configs(credentials_file='credentials.json'):
    """
    Google SheetsからChatworkルーム設定を読み込む。
    """
    # 認証
    creds = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build('sheets', 'v4', credentials=creds)

    # シートデータ取得
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    # データが空の場合
    if not values:
        return []

    # 結果を構造化
    configs = []
    for row in values:
        config = {
            'room_name': row[0] if len(row) > 0 else '',
            'chatwork_room_id': row[1] if len(row) > 1 else '',
            'drive_folder_id': row[2] if len(row) > 2 else '',
            'last_checked_at': row[3] if len(row) > 3 else None  # ISO8601想定
        }
        configs.append(config)

    return configs


def update_last_checked_at(row_index, new_timestamp=None, credentials_file='credentials.json'):
    """
    指定行の last_checked_at（D列）を更新する。
    :param row_index: 2行目以降（1行目はヘッダー）
    :param new_timestamp: 指定がなければ現在時刻（JST）を使用
    """
    # タイムスタンプが指定されていなければ現在時刻（JST）
    if new_timestamp is None:
        jst = timezone(timedelta(hours=9))
        new_timestamp = datetime.now(jst).isoformat(timespec='seconds')  # e.g., 2025-06-13T11:45:00+09:00

    # 認証
    creds = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build('sheets', 'v4', credentials=creds)

    # 書き込む範囲（例: D2）
    cell_range = f"{SHEET_NAME}!D{row_index}"

    body = {
        'values': [[new_timestamp]]
    }

    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=cell_range,
        valueInputOption='RAW',
        body=body
    ).execute()