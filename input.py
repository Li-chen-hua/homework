#1132963
import csv
import queue
import threading

from pathlib import Path
from datetime import datetime

from vis import ExpenseChart


BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "expenses.csv"


# 建立 CSV
def create_csv():

    if not CSV_FILE.exists():

        with open(
            CSV_FILE,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "date",
                "amount",
                "category",
                "notes"
            ])


# 輸入日期
def input_date():

    while True:

        date = input("請輸入日期 (YYYY-MM-DD)：")

        try:
            datetime.strptime(date, "%Y-%m-%d")
            return date

        except ValueError:
            print("日期格式錯誤，請重新輸入！")


# 輸入金額
def input_amount():

    while True:

        try:
            amount = float(input("請輸入金額："))

            if amount <= 0:
                print("金額必須大於 0！")
                continue

            return amount

        except ValueError:
            print("請輸入有效的數字！")


# 輸入類別
def input_category():

    while True:

        category = input("請輸入類別：").strip()

        if category:
            return category

        print("類別不能為空！")


# 終端機輸入流程
def terminal_input(update_queue):


    while True:

        print("\n========== 支出管理系統 ==========")
        print("1. 新增支出")
        print("2. 離開程式")

        choice = input("請選擇功能：").strip()
        if choice == '1':

            print("\n========== 新增支出 ==========")
            date = input_date()
            amount = input_amount()
            category = input_category()

            notes = input("請輸入備註：").strip()

            # 儲存資料
            with open(
                CSV_FILE,
                "a",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    date,
                    amount,
                    category,
                    notes
                ])

            print("\n支出資料新增成功！")

            # 通知圖表更新
            update_queue.put("update")

        elif choice == '2':

            print("正在關閉程式...")

            update_queue.put("quit")
            break

        else:

            print("選項錯誤，請重新輸入！")


# 主程式
def main():

    create_csv()

    # 建立訊息佇列
    update_queue = queue.Queue()

    # 建立圓餅圖
    expense_chart = ExpenseChart(update_queue)

    # 建立終端機輸入執行緒
    input_thread = threading.Thread(
        target=terminal_input,
        args=(update_queue,),
        daemon=True
    )

    input_thread.start()

    # 主執行緒負責維持圖表視窗
    expense_chart.run()


if __name__ == "__main__":
    main()
