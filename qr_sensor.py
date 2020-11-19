from qr_inout_csv import Qreader
import tkinter as tk



root = tk.Tk()
app = Qreader(master=root, today_csv="today.csv")
app.mainloop()