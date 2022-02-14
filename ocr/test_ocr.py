import sys

import os

import pyocr
import pyocr.builders

import cv2
from PIL import Image


def imageToText(src):
    #OCRエンジンの取得
    tools = pyocr.get_available_tools() 
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)

    tool = tools[0]

    dst = tool.image_to_string(
        #解析画像読み込み
        Image.open(src),
        lang='jpn',
        #OCRの設定　※tesseract_layout=6が精度には重要　デフォルトは3
        builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6)
    )
    return dst  

if __name__ == '__main__':
    img_path = sys.argv[0]

    out = imageToText("/Users/suimonnanohana/github/ocr/test_img.png")

    img = cv2.imread("/Users/suimonnanohana/github/ocr/test_img.png")
    sentence = []
    for d in out:
        sentence.append(d.content)
        cv2.rectangle(img, d.position[0], d.position[1], (0, 0, 255), 2)

    print("".join(sentence).replace("。","。\n"))

    cv2.imshow("img", img) #実行結果を出す
    cv2.imwrite("output.png", img) #実行結果ファイルを作成する
    cv2.waitKey(0)
    cv2.destroyAllWindows()