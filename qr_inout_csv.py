 
import tkinter as tk
import re
import pandas as pd 
import os 
import cv2
import inout
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
from csv_process import read_csv, write_csv


class Qreader(tk.Frame):
    def __init__(self, master=None, today_csv=None):
        super().__init__(master)
        self.pack()
        self.today_csv = today_csv
        self.create_widgets()
        
    def create_widgets(self):
        self.CANVAS_X = 640
        self.CANVAS_Y = 480
        self.image_tk = None
        self.canvas = tk.Canvas(self, width=self.CANVAS_X, height=self.CANVAS_Y)
        self.canvas.pack()
        self.cap = cv2.VideoCapture(0)
        self.capture_code()
        
    def capture_code(self):
        ret, frame = self.cap.read()
        if ret == False:
            print("Not Image")
        else:
            # frameをもとにキャンバスを作成
            self.canvas.delete('all')
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            self.image_tk = ImageTk.PhotoImage(image_pil)
            self.canvas.create_image(self.CANVAS_X / 2, self.CANVAS_Y / 2, image=self.image_tk)

            # qrコードを検出 
            decoded_objs = decode(frame)
     
            if decoded_objs != []:
                for obj in decoded_objs:
                    print('Type: ', obj)
     
                    str_dec_obj = obj.data.decode('utf-8', 'ignore')
                    # 文字列から数値を抽出
                    id = int(re.sub("\\D","", str_dec_obj))
                    print(id)
                    # csvにidの人の入退室時間をpandasの形式で書き込む
                    inout.inout_to_csv(id,self.today_csv)
                    inout.inout_to_csv(id, "today.csv")

                    print('QR code: {}'.format(str_dec_obj))
                    left, top, width, height = obj.rect
                    # qrコードを四角で囲う
                    self.canvas.create_rectangle(left, top, 
                                            left + width, top + height,
                                            outline='green', width=5)
                    # 文字列を表示
                    self.canvas.create_text(left + (width / 2), top - 30, text=str_dec_obj,
                                       font=('Helvetica', 20, 'bold'), fill='firebrick1')
     
     
        self.after(10, self.capture_code)
        
if __name__=="__main__":
    now = pd.Timestamp.now()
    today_csv = now.strftime("%Y-%m-%d") + ".csv"
    print(today_csv)
    if os.path.exists(today_csv) == False:
        today_data = read_csv("students.csv")
        write_csv(today_data, today_csv)
        write_csv(today_data, "today.csv")

    root = tk.Tk()
    root.title('QR reader')
    root.geometry('640x488+50+50')
    app = Qreader(master=root, today_csv=today_csv)
    app.mainloop()
 