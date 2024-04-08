import requests
import json

def send_slack_message(token, channel, message):
    """
    Slackにメッセージを送信する関数。

    :param token: Slack APIトークン
    :param channel: メッセージを送信するチャンネルID
    :param message: 送信するメッセージ
    """
    # SlackのトークンとチャンネルIDを設定
    TOKEN = token
    CHANNEL = channel

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "channel": CHANNEL,
        "text": message
    }

    response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("Message sent successfully")
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None

def upload_file_to_slack(token, channel, file_path, text=""):
    """
    Slackにファイルをアップロードする関数。

    :param token: Slack APIトークン
    :param channel: ファイルをアップロードするチャンネルID
    :param file_path: アップロードするファイルのパス
    :param text: ファイルと一緒に送信するテキスト
    """
    url = "https://slack.com/api/files.upload"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # ファイルを開いてデータを読み込む
    with open(file_path, "rb") as file:
        file_data = file.read()

    # パラメータを設定
    payload = {
        "channels": channel,
        "initial_comment": text
    }

    files = {
        "file": file_data
    }

    # Slackにファイルをアップロード
    response = requests.post(url, headers=headers, data=payload, files=files)

    if response.status_code == 200:
        print("File uploaded successfully")
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None