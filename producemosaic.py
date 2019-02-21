# coding: UTF-8
import json
import tqdm
import numpy as np
from PIL import Image
from collections import OrderedDict
from pathlib import Path

#5～23は処理が重複するので省略する
def load_img(path):
    img = Image.open(path)
    img.convert('HSV')
    return np.asarray(img)[:, :, :3]

def load_data(size=50):
    tlx = 0
    tly = 0
    sz = 500

    img_paths = list( Path('data/').glob('**/*.jpg') )
    img_paths = [str(path) for path in img_paths]

    img_list = [ load_img(img) for img in img_paths ]
    #画像をsz×szで切り取り
    img_list = [ img[tly:tly+sz, tlx:tlx+sz, :] for img in img_list ]

    #サイズを小さくする
    img_list = [ np.asarray(Image.fromarray(img).resize((size, size))) for img in img_list ]

    return (img_paths, img_list)

def main():
    with open('producemosaicart.json','r') as f:
        mosaic = json.load(f,object_pairs_hook=OrderedDict)
        
    _, data_list = load_data()
    size = mosaic['block_size']
    h = mosaic['mosaic_size_h']
    w = mosaic['mosaic_size_w']
    
    out = np.zeros((size*h, size*w, 3), dtype=np.uint8)
    for i in tqdm.trange(h):
        for j in range(w):

            out_tly = size*i
            out_tlx = size*j
            out_bry = size*(i+1)
            out_brx = size*(j+1)
            out[out_tly:out_bry, out_tlx:out_brx, :] = data_list[int(mosaic[str((i*w)+j)])]
        
    Image.fromarray(out).save('out.png')

if __name__ == '__main__':
    main()