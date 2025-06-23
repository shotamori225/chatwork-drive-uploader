from uploader.sheet import read_room_configs, update_last_checked_at

def main():
    credentials_file = 'credentials.json'  # ← config.iniから使ってるパスに置換

    # スプレッドシートから設定を取得
    room_configs = read_room_configs(credentials_file=credentials_file)

    for i, config in enumerate(room_configs, start=2):  # ヘッダー除いた行番号
        print(f"更新: {i}行目 - {config['room_name']}")
        update_last_checked_at(row_index=i, credentials_file=credentials_file)

    print("🎉 全行の last_checked_at を更新しました")

if __name__ == "__main__":
    main()