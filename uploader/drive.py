from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import io

# スコープ：Driveファイルの作成やアップロードを許可
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service(credentials_path: str):
    """
    サービスアカウントの認証情報からDrive APIサービスを作成
    """
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)


def upload_file_to_drive(service, filename: str, file_data: bytes, folder_id: str) -> str:
    """
    Google Driveにファイルをアップロードし、アップロード後のfileIdを返す
    """
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }

    media = MediaIoBaseUpload(io.BytesIO(file_data), mimetype='application/octet-stream')

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"☁️ Driveアップロード完了: {filename} (id={uploaded.get('id')})")
    return uploaded.get('id')
