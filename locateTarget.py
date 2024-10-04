import cv2
import numpy as np

def preprocess(imInput):
    # 入力画像をHSVに変換し、平滑化
    imInputHSV = cv2.cvtColor(imInput, cv2.COLOR_BGR2HSV)
    imGaussianHSV = cv2.blur(imInputHSV, (3, 3))
    return imGaussianHSV

def locateFlag(imInputHSV):
    # 対象色の定義１（赤の場合）
    vMinHSV = np.array([0, 180, 0])
    vMaxHSV = np.array([10, 255, 255])
    imRed1 = cv2.inRange(imInputHSV, vMinHSV, vMaxHSV)

    # 対象色の定義２（赤の場合は色相が最大と最小に分かれるため2つ必要）
    vMinHSV = np.array([160, 180, 0])
    vMaxHSV = np.array([180, 255, 255])
    imRed2 = cv2.inRange(imInputHSV, vMinHSV, vMaxHSV)

    # 対象色のエリア画像の作成
    imRed = imRed1 + imRed2

    # モルフォロジー処理でノイズ除去と滑らかさを向上
    kernel = np.ones((5, 5), np.uint8)
    imRedMorph = cv2.morphologyEx(imRed.astype(np.uint8), cv2.MORPH_CLOSE, kernel)

    #ガウシアンフィルタでさらに滑らかにする
    imRedSmooth = cv2.GaussianBlur(imRedMorph, (5, 5), 0)

    #中値フィルタを適用してさらに滑らかに
    imRedSmooth = cv2.medianBlur(imRedSmooth, 5)

    # 画像の表示
    cv2.imshow('mask', imRedSmooth)

    # 輪郭検出を実施
    contours, _ = cv2.findContours(imRedSmooth, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # 輪郭をポリゴンとして近似し、頂点数で形状を判別
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        num_vertices = len(approx)

        # 頂点数による形状の判別
        if num_vertices == 3:
            shape = "三角形"
        elif num_vertices == 4:
            # 四角形かどうか
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            if 0.95 <= aspect_ratio <= 1.05:
                shape = "正方形"
            else:
                shape = "長方形"
        elif num_vertices > 4:
            shape = "円形に近い"
        else:
            shape = "不明"

        # 形状をプリント
        print(f"検出された形状: {shape}")

    # 対象色エリア（最も縦に長いもの）の水平位置の割り出し
    vSumRedVertical = np.sum(imRedSmooth / 255, axis=0)
    sMaxIndex = vSumRedVertical.argmax()

    # 対象色エリアの縦の長さが5画素よりも大きい場合、ターゲットに設定
    if vSumRedVertical[sMaxIndex] > 5:
        sHorizontal = sMaxIndex
        sVertical = -1
        sSize = vSumRedVertical[sMaxIndex]
    else:
        sHorizontal = -1
        sVertical = -1
        sSize = -1

    return (sHorizontal, sVertical, sSize), imRedSmooth


def locateEnemy(imInputHSV):
    # 緑色の範囲を定義（HSVで）
    lower_green = np.array([35, 100, 100])  # 緑色の下限
    upper_green = np.array([85, 255, 255])  # 緑色の上限

    # 緑色範囲に対するバイナリマスクを作成
    imGreen = cv2.inRange(imInputHSV, lower_green, upper_green)

    # 1. モルフォロジー処理でノイズ除去
    kernel = np.ones((5, 5), np.uint8)
    imGreenMorph = cv2.morphologyEx(imGreen.astype(np.uint8), cv2.MORPH_CLOSE, kernel)

    # 2. ガウシアンフィルタで滑らかに
    imGreenSmooth = cv2.GaussianBlur(imGreenMorph, (5, 5), 0)

    # 3. 中値フィルタを適用
    imGreenSmooth = cv2.medianBlur(imGreenSmooth, 5)

    # バイナリ画像を適切に表示
    cv2.imshow('mask', imGreenSmooth)

    # 輪郭検出を実施
    contours, _ = cv2.findContours(imGreenSmooth, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 検出されたオブジェクトの情報を保存するための変数
    detected_objects = []

    # 各輪郭に対して処理
    for contour in contours:
        # 輪郭に外接する矩形を取得
        x, y, w, h = cv2.boundingRect(contour)

        # 矩形の面積が一定以上の場合に敵として認識
        if w * h > 500:  # 面積が小さすぎるものは無視
            detected_objects.append((x, y, w, h))

    # 検出されたオブジェクトがあれば最初のものを返す、なければデフォルト値を返す
    if detected_objects:
        sHorizontal, sVertical, sSize = detected_objects[0][0], detected_objects[0][1], detected_objects[0][2] * detected_objects[0][3]
    else:
        sHorizontal, sVertical, sSize = -1, -1, -1

    return (sHorizontal, sVertical, sSize), imGreenSmooth
