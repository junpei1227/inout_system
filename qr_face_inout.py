# -*- coding: utf-8 -*-
import cv2
import numpy as np
# try:
# from sklearn.externals import joblib
# except ImportError:
import joblib
import pandas as pd
import os
import inout
import re
from pyzbar.pyzbar import decode
from csv_process import read_csv, write_csv


def trimming_face_image(image, face, size=(40,40)):
    """
    画像から顔を切り取り,リサイズした画像を返す
    """
    for x, y, w, h in face:
        # スライシングで顔の部分を切り取る
        face_image = image[y:y+h, x:x+w]
        # リサイズする 
        face_image = cv2.resize(face_image, size)
        return face_image

def get_predicted(face_image, clsfile, IMAGE_SIZE=40, IMAGE_SIZE_Y=40, COLOR_BYTE=3):
    """
    clsfileから分類機を読み込みface_imageを分類し予想結果を整数で返す
    """ 
    # 学習済のファイルを読み込む
    loaded_cls = joblib.load(clsfile)
    # 学習モデルの形式に変換
    flat_face_image = face_image.reshape((-1, IMAGE_SIZE * IMAGE_SIZE_Y * COLOR_BYTE))
    # 誰の顔か予測する
    predicted = loaded_cls.predict(flat_face_image)[0]
    return predicted




def face_inout_csv(csv_file, cls_file,stream_size=(320,240), font=cv2.FONT_HERSHEY_SIMPLEX):
    # HaarLike特徴抽出アルゴリズムのパス
    # 任意のパス
    HAAR_FILE = "data/haarcascade_frontalface_alt.xml"
    # HaarLike特徴抽出アルゴリズムから分類器を作成
    cascade = cv2.CascadeClassifier(HAAR_FILE)
    
    data = read_csv(csv_file)
    cap = cv2.VideoCapture(0)
    while True: 
        # 映像データを読み込んでサイズ変更
        rst, stream = cap.read()
        stream = cv2.resize(stream, stream_size)
        
        # streamからfaceを検出する
        face = cascade.detectMultiScale(stream)

        # 顔認識したものが一つの時処理を行う
        if len(face) == 1:
            face_image = trimming_face_image(stream, face)
            # face_imageからidを取得
            id = get_predicted(face_image, cls_file)
            # idの人の入退室データをcsvに書き込む
            inout.inout_to_csv(id, csv_file)
            name_text = data["name"][id]
            for x, y, w, h in face:
                # 認識した顔を赤い四角で囲う
                cv2.rectangle(stream, (x,y), (x+w,y+h), (0,0,255), 1)
                # 名前を表示
                cv2.putText(stream, name_text,(x,y-10), font, 1, (0,255,0), 3, cv2.LINE_AA)

        # streamからqrを検出する
        decoded_objs = decode(stream)
        if decoded_objs != []:
            for obj in decoded_objs:
                print('Type: ', obj)
                str_dec_obj = obj.data.decode('utf-8', 'ignore')
                # 文字列から数値を抽出
                id = int(re.sub("\\D","", str_dec_obj))
                # csvにidの人の入退室時間をpandasの形式で書き込む
                inout.inout_to_csv(id, csv_file)

                print('QR code: {}'.format(str_dec_obj))
                x, y, w, h = obj.rect
                # qrコードを四角で囲う
                cv2.rectangle(stream, (x,y), (x+w,y+h), (0,0,255), 1)
                # 文字列を表示
                cv2.putText(stream, str_dec_obj,(x,y-10), font, 1, (0,255,0), 3, cv2.LINE_AA)




        # 画像をウインドウに表示
        cv2.imshow("img", stream)
        
        # 'q'を入力でアプリケーション終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    #終了処理
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    now = pd.Timestamp.now()
    today_csv = now.strftime("%Y-%m-%d") + ".csv"
    base_csv = "data/train_data_arasi.csv"
    if os.path.exists(today_csv) == False:
        today_data = read_csv(base_csv)
        write_csv(today_data, today_csv)

    #  学習した分類機のファイル
    cls_file = "data/face_result_arasi1118.pkl"
    face_inout_csv(today_csv, cls_file)