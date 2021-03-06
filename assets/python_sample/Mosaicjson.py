# coding=utf-8

from PIL import Image
import numpy as np
import json
from collections import OrderedDict
from pathlib import Path

# pathで指定された画像ファイルを読み込んで三次元配列(numpyのndarray)で返す


def load_img(path):
    img = Image.open(path)
    img.convert('HSV')
    return np.asarray(img)[:, :, :3]

# 画像の特徴量を計算


def feature(img, feature_div):
    chunk_sz = img.shape[0]/feature_div
    n_chunk_pixels = chunk_sz*chunk_sz
    f = np.zeros((feature_div, feature_div, img.shape[2]))
    for i in range(feature_div):
        for j in range(feature_div):
            tly = int(chunk_sz*i)
            tlx = int(chunk_sz*j)
            bry = int(chunk_sz*(i+1))
            brx = int(chunk_sz*(j+1))
            f[i, j] = np.sum(img[tly:bry, tlx:brx, :], axis=(0, 1))
    return f / n_chunk_pixels

# 2つの特徴量の差(距離，どのくらい違うか)を計算


def distance_feature(x, y):
    return np.sum(np.linalg.norm(x - y, axis=2))


def main(feature_div, blk_size, distance_pix, id, progress):
    # 近似対象画像をどれくらいの細かさでモザイク化するか
    # blk_size×blk_sizeの正方形を最小単位としてモザイク化する
    # 1のとき1×1の正方形が最小単位となるので最も細かいが，処理に時間がかかるし生成される画像が大きくなる
    # 事前に計算した素材画像の特徴量を読み込む
    with open(id + '/features.json', 'r') as f:
        tiles_features = json.load(f, object_pairs_hook=OrderedDict)
    # 近似対象画像を読み込む
    img = load_img(id + '/source.jpg')
    # 近似対象画像のサイズ(画素)
    h = img.shape[0]  # 縦
    w = img.shape[1]  # 横
    # モザイク化された近似対象画像のタイルの数
    n = h//blk_size  # 縦
    m = w//blk_size  # 横
    tile_blksz = tiles_features['block_size']
    tiles_data = tiles_features['feature']

    out = OrderedDict()
    out['block_size'] = tile_blksz
    out['mosaic_size_h'] = n
    out['mosaic_size_w'] = m
    abatement = [[] for i in range(distance_pix+1)]
    dele = []
    sa = []
    nouse = {}
    nears = []
    huga = {}
    tile_num = list(range(len(tiles_data)))
    count = 0
    progress[id] = 0.0
    hoge = 0
    c = 0

    for i in range(m*2-1):
        j = i
        k = 0
        count = count % (distance_pix)

        while True:
            while j > m-1:
                j -= 1
                k += 1
                if(k > n-1):
                    break
            c = c % distance_pix

            tly = blk_size*k
            tlx = blk_size*j
            bry = blk_size*(k+1)
            brx = blk_size*(j+1)
            block = img[tly:bry, tlx:brx, :]

            # 一番平均が近い画像番号探す
            for x in range(distance_pix):
                dele = dele + abatement[x]
            dele = dele + list([i for i in nouse.values()])
            dele.sort()
            if(k < n):
                tiles = list(set(tile_num) - set(dele))
                number = np.argmin([distance_feature(
                    feature(block, feature_div), tiles_data[tiles[y]]) for y in range(len(tiles))])
                nearest = tiles[number]
                hoge += 1
                progress[id] = round(float(hoge)/(float(n)*float(m)), 2)
                print(progress[id])
                huga[k*m + j] = nearest
                # 次のループで使ってはいけない画像番号の行列
                abatement[distance_pix].append(nearest)
                nouse[c] = nearest
                c += 1
            else:
                nouse = {}
            dele = []
            tiles = []
            j -= 1
            k += 1
            if j < 0:
                dele = []
                abatement[count] = []
                abatement[count] = abatement[distance_pix]
                nears = nears + abatement[distance_pix]
                abatement[distance_pix] = []
                nouse = {}
                count += 1
                break
    nears = sorted(huga.items())
    out['images'] = [nears[i][1] for i in range(len(nears))]
    fw = open(id + '/producemosaicart.json', 'w')
    json.dump(out, fw, indent=4)


if __name__ == '__main__':
    main(1, 15, 1, "static", {"static": 0})
