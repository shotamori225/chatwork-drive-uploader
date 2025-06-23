from sheet import read_room_configs, update_last_checked_at
from chatwork import get_new_files
import drive  # Drive連携モジュール（upload_fileなどが入ってる想定）
import configparser
from datetime import datetime, timezone, timedelta

def main():
    # config.ini 読み込み
    config = configparser.ConfigParser()
    config.read("config.ini")

    credentials_file = config.get("google", "credentials_file")
    chatwork_token = config.get("chatwork", "api_token")

    # スプレッドシートからルーム設定取得
    room_configs = read_room_configs(credentials_file=credentials_file)

    for i, config_row in enumerate(room_configs, start=2):  # row_index=2から始まる
        room_id = config_row["chatwork_room_id"]
        folder_id = config_row["drive_folder_id"]
        last_checked_at = config_row.get("last_checked_at")

        print(f"▶️ {i}行目：ルーム {config_row['room_name']} の処理を開始")

        # チェック条件が揃っていない行はスキップ
        if not room_id or not folder_id:
            print(f"⚠️  必要な情報が不足しています（room_idまたはfolder_id）→ スキップ")
            continue

        # ファイル取得
        try:
            files = get_new_files(chatwork_token, room_id, last_checked_at)
        except Exception as e:
            print(f"❌ Chatworkファイル取得エラー: {e}")
            continue

        # アップロード
        for f in files:
            try:
                drive.upload_file(folder_id, f["filename"], f["content"], credentials_file)
                print(f"  ✅ アップロード完了: {f['filename']}")
            except Exception as e:
                print(f"  ❌ アップロード失敗: {f['filename']} → {e}")

        # 処理が終わったら最終確認時刻を更新（JST現在時刻）
        jst = timezone(timedelta(hours=9))
        now_str = datetime.now(jst).isoformat(timespec='seconds')
        update_last_checked_at(i, new_timestamp=now_str, credentials_file=credentials_file)
        print(f"🕒 最終確認時刻を更新: {now_str}")

if __name__ == "__main__":
    main()
