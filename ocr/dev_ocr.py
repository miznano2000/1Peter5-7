import sys

import cv2
import os
import numpy as np

import pyocr
import pyocr.builders

from PIL import Image, ImageDraw, ImageFont

import time

#前処理
def process(src):
    kernel = np.ones((3,3),np.uint8)
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) #グレースケールの画像生成

    o_ret, o_dst = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU) #白黒画像生成（２値化）
    dst = cv2.morphologyEx(o_dst, cv2.MORPH_OPEN, kernel) #モルフォロジー処理
    return cv2.bitwise_not(dst)

#画像から文字認識
def imageToText(tool, src):
    tmp_path = "temp.png"

    cv2.imwrite(tmp_path, src)
    dst = tool.image_to_string(
        Image.open(tmp_path),
        lang='eng',
        builder=pyocr.builders.LineBoxBuilder(tesseract_layout=6)
    )

    sentence = []
    for item in dst:
        print(item.content, item.position)
        sentence.append(item.content)
        #cv2.imread(item)
        #cv2.rectangle(item,item.position[0],item.position[1],(0,0,255),2) #dstをsentenceに入れていく   
    return "".join(sentence)

#下に認識した文字を出す
def createTextImage(src, sentence, px, py, color=(8,8,8), fsize=28):

    tmp_path = "src_temp.png"
    cv2.imwrite(tmp_path, src)

    img = Image.open(tmp_path)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", fsize)
    draw.text((px, py), sentence, fill=color, font=font)
    img.save(tmp_path)
    return cv2.imread(tmp_path)



if __name__ == '__main__':

    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)

    tool = tools[0]
    #動画の読み込み※１枚ずつ画像を読む
    cap = cv2.VideoCapture('ABC_news_002.mp4')
    #幅、高さ、fpsのプロパティ読み込む
    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    #テロップ
    telop_height = 50
    #動画の形式を指定してVideoWriterを実行
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    writer = cv2.VideoWriter('extract_telop_text.mp4',fourcc, fps, (cap_width, cap_height + telop_height))

    start = time.time()
    count = 0
    try :
        while True:
            if not cap.isOpened():
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            ret, frame = cap.read()

            if frame is None:
                break
            #テロップ
            telop = np.zeros((telop_height, cap_width, 3), np.uint8)
            telop[:] = tuple((128,128,128))
            #preprocessを実行
            gray_frame = process(frame)
            roi = gray_frame[:, :] #RoIだとすれば
            #imagetoTextを実行
            txt = imageToText(tool, roi)

            images = [frame, telop]

            frame = np.concatenate(images, axis=0)
            font = cv2.FONT_HERSHEY_SIMPLEX
            seconds = round(count/fps, 4)

            #テキストを描画
            cv2.putText(frame, "{:.4f} [sec]".format(seconds), 
                        (cap_width - 250, cap_height + telop_height - 10), 
                        font, 
                        1, 
                        (0, 0, 255), 
                        2, 
                        cv2.LINE_AA)
            
            writer.write(createTextImage(frame, txt, 20, cap_height + 10))
            count += 1

            print("{}[sec]".format(seconds))

    except cv2.error as e:
        print(e)    

    writer.release()
    cap.release()

    print("Done!!! {}[sec]".format(round(time.time() - start,4)))
