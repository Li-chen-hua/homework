
import csv
import queue
from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "expenses.csv"


class ExpenseChart:

    def __init__(self, update_queue):

        self.update_queue = update_queue

        # 設定中文字型
        plt.rcParams["font.sans-serif"] = [
            "Microsoft JhengHei",
            "Microsoft YaHei",
            "Arial"
        ]
        plt.rcParams["axes.unicode_minus"] = False

        # 建立圖表
        self.fig, self.ax = plt.subplots(figsize=(7, 6))

        self.fig.canvas.manager.set_window_title(
            "Expense Distribution"
        )

        # 初始繪圖
        self.update_chart()

        # 設定定時器，持續檢查是否需要更新
        self.timer = self.fig.canvas.new_timer(
            interval=100
        )

        self.timer.add_callback(self.check_update)
        self.timer.start()

    # 讀取並統計資料
    def read_expenses(self):

        category_total = defaultdict(float)

        if not CSV_FILE.exists():
            return category_total

        with open(
            CSV_FILE,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                try:
                    category = row["category"].strip()
                    amount = float(row["amount"])

                    if category and amount > 0:
                        category_total[category] += amount

                except (ValueError, KeyError, TypeError):
                    continue

        return category_total

    # 繪製圓餅圖
    def update_chart(self):

        category_total = self.read_expenses()

        self.ax.clear()

        if not category_total:

            self.ax.text(
                0.5,
                0.5,
                "No Expense Data",
                ha="center",
                va="center",
                fontsize=16
            )

            self.ax.axis("off")

        else:

            labels = list(category_total.keys())
            values = list(category_total.values())

            self.ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90
            )

            self.ax.set_title("Expense Distribution")
            self.ax.axis("equal")

        # 重新繪製
        self.fig.canvas.draw_idle()

    # 持續檢查更新通知
    def check_update(self):

        should_update = False

        try:
            while True:

                message = self.update_queue.get_nowait()

                if message == "update":
                    should_update = True

                elif message == "quit":
                    plt.close(self.fig)
                    return False

        except queue.Empty:
            pass

        if should_update:
            self.update_chart()


        return True

    # 啟動圖表視窗
    def run(self):

        plt.show()
