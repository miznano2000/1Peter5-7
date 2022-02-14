#from turtle import position
from cv2 import rectangle
import numpy as np
import cv2 #opencv
import time
from PIL import Image, ImageDraw, ImageFont
import pyocr
import pyocr.builders
import sys
#import tkinter

#動画の前処理 #改善の余地あり
def preprocess(src):
    kernel = np.ones((3,3), np.uint8)
    #グレースケールにする
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    #白黒画像生成
    threshoud = 0 #閾値
    o_retval, o_dst = cv2.threshold(gray, threshoud, 255, cv2.THRESH_OTSU)
    #モルフォロジー処理
    dst = cv2.morphologyEx(o_dst, cv2.MORPH_OPEN, kernel)
    #returnで上記処理後のdstを白黒反転させたものを返す
    return cv2.bitwise_not(dst)

#画像から文字認識を行う
def imageToText(tool, src):
    #画像のパス
    temp_path = "temp.png"

    #画像を保存する引数（パス、画像のデータ）
    #NumPy配列ndarrayとして読み込まれ、ndarrayを画像として保存する。
    cv2.imwrite(temp_path, src) 
    #画像をテキストに変換 #文字認識を実行
    dst = tool.image_to_string(
        Image.open(temp_path),#画像を指定し開く
        lang = "eng", #言語の設定
        builder = pyocr.builders.LineBoxBuilder(tesseract_layout=6)
    )

    #画像を読み込む
    #image = Image.open(temp_path)
    sentence = [] #空のsentenceという配列を用意する

    for item in dst:
        print(item.content, item.position)
        sentence.append(item.content) #dstをsentenceに入れていく

    return "".join(sentence) #sentenceの中身を結合する

#######################
#認識した文字を囲う
#######################
def CircleTextImage(src, sentence):

    tmp_path = "src_temp_path.png"
    cv2.imwrite(tmp_path, src)

    img = Image.open(tmp_path)
    draw = rectangle(img,position[0],position[1],(0,0,255),2)
    img.save(tmp_path)
    return cv2.imread(tmp_path)
#######################
#VideoCaptureを作成する
if __name__ == '__main__':
    
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)

    tool = tools[0]

    #動画ファイルからフレームを取得する
    videoname = "ABC_news_002.mp4"
    cap = cv2.VideoCapture(videoname)

    #動画ファイルの幅、高さ、fpsを読み取る
    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap_fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"size:({cap_width},{cap_height}), fps:{cap_fps}")

    #VideoWriterを作成する
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    writer = cv2.VideoWriter('output_name.mp4',fourcc, cap_fps, (cap_width, cap_height))

    start = time.time()
    count = 0

    #動画を１フレームずつ取得する
    try :
        while True:
            if not cap.isOpened():
                break

            if cv2.waitKey(1) & 0xFF == ord('q'): #qを押したら終了
                    break

            ret, frame = cap.read() #フレームの読み込みが正しく行われればTrue

            if not ret:
                break #取得に失敗した場合はループを抜ける

            ######ここから自分でやってみてる######
            #四角で囲む

            #preprocessを実行
            preframe = preprocess(frame)
            #imageToTextを実行
            RoI = preframe[:,:]
            ocrframe = imageToText(tool,RoI)

            ##################################
            #動画を描画する
            seconds = round(count/cap_fps, 4)
            writer.write(ocrframe)
            count += 1
            print("{}[sec]".format(seconds))


    except cv2.error as e:
        print(e)
        

    #全てのジョブ終了後、Release
    writer.release()
    cap.release()

    print("Done!!! {}[sec]".format(round(time.time() - start,4)))