import configparser
import os
from uploader.chatwork import fetch_files_from_room, download_file
from uploader.drive import get_drive_service, upload_file_to_drive

def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["chatwork"], config["google"]

def main():
    chatwork_config, google_config = load_config()

    api_token = chatwork_config["api_token"]
    room_id = chatwork_config["room_id"]
    last_checked = chatwork_config["last_checked"]

    credentials_path = google_config["credentials_path"]
    drive_folder_id = google_config["drive_folder_id"]

    # Google Drive 認証
    service = get_drive_service(credentials_path)

    print(f"📥 Chatworkからファイル一覧を取得中... (room_id={room_id})")

    try:
        files = fetch_files_from_room(api_token, room_id, last_checked)
        print(f"✅ 取得件数: {len(files)} 件\n")

        for f in files:
            print(f"📄 処理中: {f['filename']}")
            file_binary, filename = download_file(api_token, room_id, f["file_id"])

            # ローカル保存（いったん保存する）
            os.makedirs("downloads", exist_ok=True)
            local_path = os.path.join("downloads", filename)
            with open(local_path, "wb") as f_out:
                f_out.write(file_binary)
            print(f"💾 ローカル保存完了: {local_path}")

            # Google Driveにアップロード
            upload_file_to_drive(service, filename, file_binary, drive_folder_id)

            # ローカルファイル削除
            os.remove(local_path)
            print(f"🧹 ローカルファイル削除: {local_path}\n")

    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    main()
