import pyocr
import pyocr.builders
from PIL import Image

# tesseractをインストールしたフォルダにパスが通っていること
tools = pyocr.get_available_tools()
line_boxs=tools[0].image_to_string(
    Image.open('test_img.png'),
    lang='jpn',
    builder=pyocr.builders.LineBoxBuilder()
)

for line_box in line_boxs:
    # 件 名 : バブ リッ クコ メン ト へ の 意見 ((68, 182), (235, 191))
    print(line_box.content, line_box.position)
    for word_box in line_box.word_boxes:
        print('  ', word_box.content, word_box.position)