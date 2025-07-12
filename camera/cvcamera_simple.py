import cv2

# カメラデバイスを順に試して利用可能なデバイスを探す
for index in range(10):
    cap = cv2.VideoCapture(index)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('captured_image.jpg', frame)  # 画像を保存
        cap.release()
        break  # カメラが見つかればループを抜ける
