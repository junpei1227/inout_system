import tkinter as tk
import csv
import os
# import pygame.mixer
import datetime
import pandas as pd
from csv_process import read_csv, write_csv

from Romaji2Kanji import Romaji2Kanji
from students import students


class App(tk.Frame):
    def __init__(self, master=None, today_csv=None):
        self.n = 0
        super().__init__(master)
        self.pack()
        self.today_csv = today_csv
        print(self,today_csv)
        self.create_widgets()

    def create_widgets(self):
        # today_csvファイル更新時間
        self.tm_last = ""

        # widgetsの配置
        header = tk.Label(self,text = "AI-IoT科　出席状況", bg="blue",fg="white")
        header.grid(column = 1, row = 0, in_ = self)
        c = 0 ; r = 1
        for s in sorted(students.keys()):
            students[s] = tk.StringVar()
            label = tk.Label(self, textvariable=students[s])
            students[s].set(Romaji2Kanji[s])
            label.grid(column = c%3, row = r, in_ = self)
            c += 1
            if c % 3 == 0:
                r += 1
        footer1 = tk.Label(self,text = "◎出席　○完了")
        footer1.grid(column = 0, row = r+1, in_ = self)
        footer2 = tk.Label(self,text = "△遅刻　▽早退")
        footer2.grid(column = 1, row = r+1, in_ = self)
        footer3 = tk.Label(self,text = "□中抜　ー欠席")
        footer3.grid(column = 2, row = r+1, in_ = self)

        self.view_refresh()

    def view_refresh(self):
        if os.path.exists(self.today_csv):
            tm = datetime.datetime.fromtimestamp(os.path.getmtime(self.today_csv))
            tm_current = tm.strftime("%H%M%S")
            # ファイルが更新されたか判定
            if self.tm_last != tm_current:
                # pygame.mixer.music.play(1)
                self.tm_last = tm_current
                # csvファイルを読み込み、欠損値を−に変換
                df = read_csv(self.today_csv)
                df.fillna("-",inplace=True)
                # labelに名前とステータスをセットする
                for n, s in enumerate(sorted(students.keys())):
                    status = df["status"][n+1]
                    students[s].set(Romaji2Kanji[s] + status)
        else:
            status = "-"
            for n, s in enumerate(sorted(students.keys())):
                students[s].set(Romaji2Kanji[s] + status)

        self.after(500, self.view_refresh)

if __name__ == "__main__":
    # sound ="se_maoudamashii_system37.mp3"
    # pygame.mixer.init()
    # pygame.mixer.music.load(sound)

    now = pd.Timestamp.now()
    today_csv = now.strftime("%Y-%m-%d") + ".csv"
    print(today_csv)

    root = tk.Tk()
    root.wm_title("QR Inout View")
    root.option_add('*font', 'FixedSys 24')
    app = App(master=root, today_csv=today_csv)
    root.geometry("840x600+900+300")
    app.mainloop()
