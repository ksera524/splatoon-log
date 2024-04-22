import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2

from slack import upload_file_to_slack,send_slack_message

def get_x_power(driver, url, rule_name):
    driver.get(url)
    detail_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "table.table-striped.table-condensed tbody tr.battle-row .btn.btn-primary.btn-xs"))
    )
    detail_button.click()

    first_table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
    rows = first_table.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        th_elements = row.find_elements(By.TAG_NAME, "th")
        td_elements = row.find_elements(By.TAG_NAME, "td")
        
        for th in th_elements:
            if "X Power" in th.text and td_elements:
                x_power_text = td_elements[0].text
                x_power_values = [x.strip() for x in x_power_text.split(' ')]
                x_power_value = x_power_values[-1]  # 最後の値（2つある場合は2つ目の値、1つの場合はその値）
                print(f"{rule_name} X Power: {x_power_value}")
                return x_power_value
     
def insert_x_power(date, area_xp, hoko_xp, yagura_xp, asari_xp):
    # PostgreSQLデータベースの接続設定
    conn = psycopg2.connect(
        dbname=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT')
    )
    cur = conn.cursor()
    
    # SQLクエリの定義
    insert_query = """
    INSERT INTO x_power (date, area_x_power, hoko_x_power, yagura_x_power, asari_x_power)
    VALUES (%s, %s, %s, %s, %s);
    """

    # カンマを削除して数値に変換
    area_xp = float(area_xp.replace(',', ''))
    hoko_xp = float(hoko_xp.replace(',', ''))
    yagura_xp = float(yagura_xp.replace(',', ''))
    asari_xp = float(asari_xp.replace(',', ''))
    
    # SQLクエリの実行
    cur.execute(insert_query, (date, area_xp, hoko_xp, yagura_xp, asari_xp))
    
    # 変更のコミット
    conn.commit()
    
    # リソースの解放
    cur.close()
    conn.close()

def fetch_data():
    conn = psycopg2.connect(
        dbname=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT')
    )
    # SQLクエリを実行してDataFrameを直接作成
    df = pd.read_sql("SELECT * FROM x_power ORDER BY date ASC;", conn)
    conn.close()
    return df


def main():
    # chromedriverのパス
    CHROMEDRIVER = '/usr/bin/chromedriver'

    # ヘッドレスオプションとエラー回避オプション
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")  # GPUハードウェアアクセラレーションを無効にする
    options.add_argument("--no-sandbox")  # サンドボックスプロセスを無効にする
    options.add_argument("--disable-dev-shm-usage")  # /dev/shmパーティションの使用を避ける
    options.add_argument("--window-size=1920x1080")  # 仮想画面サイズの指定

    # ドライバー指定でChromeブラウザを開く 
    chrome_service = service.Service(executable_path=CHROMEDRIVER) 
    driver = webdriver.Chrome(options=options, service=chrome_service)
    driver.implicitly_wait(10)
    driver.set_window_size('1200', '1000')

    urls = {
        "area": 'https://stat.ink/@ksera/spl3?f%5Blobby%5D=xmatch&f%5Brule%5D=area',
        "hoko": 'https://stat.ink/@ksera/spl3?f%5Blobby%5D=xmatch&f%5Brule%5D=hoko',
        "yagura": 'https://stat.ink/@ksera/spl3?f%5Blobby%5D=xmatch&f%5Brule%5D=yagura',
        "asari": 'https://stat.ink/@ksera/spl3?f%5Blobby%5D=xmatch&f%5Brule%5D=asari'
    }

    x_power_values = {}
    for rule_name, url in urls.items():
        x_power = get_x_power(driver, url, rule_name)
        x_power_values[rule_name] = x_power

    # 現在の日付を取得
    today = datetime.now().date()

    # DBに値を挿入
    insert_x_power(
        today,
        x_power_values.get("area"),
        x_power_values.get("hoko"),
        x_power_values.get("yagura"),
        x_power_values.get("asari")
    )

    # データを取得
    df = fetch_data()

    # DataFrameの日付列を日付型に変換
    df['date'] = pd.to_datetime(df['date'])

    # 日付をMM/DD形式に変換
    df['date'] = df['date'].dt.strftime('%m/%d')

    # Seabornの設定
    sns.set(style="darkgrid")

    # 折れ線グラフの作成
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['area_x_power'], label='Area', marker='o')
    plt.plot(df['date'], df['hoko_x_power'], label='Hoko', marker='o')
    plt.plot(df['date'], df['yagura_x_power'], label='Yagura', marker='o')
    plt.plot(df['date'], df['asari_x_power'], label='Asari', marker='o')

    # グラフをPNGとして保存
    plt.savefig('x_power_trends.png')

    text = "日付: " + df['date'].iloc[-1] + "\n" + "エリア: " + str(df['area_x_power'].iloc[-1]) + "\n" + "ホコ: " + str(df['hoko_x_power'].iloc[-1]) + "\n" + "ヤグラ: " + str(df['yagura_x_power'].iloc[-1]) + "\n" + "アサリ: " + str(df['asari_x_power'].iloc[-1])

    send_slack_message(
        os.getenv('SLACK_API_TOKEN'),
        os.getenv('SLACK_CHANNEL_ID'),
        text
    )
    
    # Slackに画像をアップロード
    upload_file_to_slack(
        os.getenv('SLACK_API_TOKEN'),
        os.getenv('SLACK_CHANNEL_ID'),
        'x_power_trends.png'
    )

    # 必要な操作を行った後、ドライバーを閉じる
    driver.quit()

if __name__ == "__main__":
    main()
