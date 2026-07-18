import socket
import threading
# pyrefly: ignore [missing-import]
import cv2
import time
import numpy as np
# データ受け取り用の関数
def udp_receiver():
        global battery_text
        global time_text
        global status_text
        while True:
            try:
                data, server = sock.recvfrom(1518)
                resp = data.decode(encoding="utf-8").strip()
                # レスポンスが数字だけならバッテリー残量
                if resp.isdecimal():
                    battery_text = "Battery:" + resp + "%"
                # 最後の文字がsなら飛行時間
                elif resp[-1:] == "s":
                    time_text = "Time:" + resp
                else:
                    status_text = "Status:" + resp
            except:
                pass
# 問い合わせ
def ask():
    while True:
        try:
            sent = sock.sendto('battery?'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
        time.sleep(0.5)
        try:
            sent = sock.sendto('time?'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
        time.sleep(0.5)
# 離陸
def takeoff():
        print("-----")
        try:
            print("ok")
            sent = sock.sendto('takeoff'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            print("error")
            pass
# 着陸
def land():
        try:
            sent = sock.sendto('land'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 上昇(20cm)
def up():
        try:
            sent = sock.sendto('up 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 下降(20cm)
def down():
        try:
            sent = sock.sendto('down 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 前に進む(0cm)
def forward():
        try:
            sent = sock.sendto('forward 0'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 後に進む(0cm)
def back():
        try:
            sent = sock.sendto('back 0'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 右に進む(0cm)
def right():
        try:
            sent = sock.sendto('right 0'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 左に進む(0cm)
def left():
        try:
            sent = sock.sendto('left 0'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 右回りに回転(90 deg)
def cw():
        try:
            sent = sock.sendto('cw 90'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 左回りに回転(90 deg)
def ccw():
        try:
            sent = sock.sendto('ccw 90'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 速度変更(例：速度40cm/sec, 0 < speed < 100)
def set_speed(n=60):
        try:
            sent = sock.sendto(f'speed {n}'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass

            
# Tello側のローカルIPアドレス(デフォルト)、宛先ポート番号(コマンドモード用)
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)
# Telloからの映像受信用のローカルIPアドレス、宛先ポート番号
TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=50000000'
command_text = "None"
battery_text = "Battery:"
time_text = "Time:"
status_text = "Status:"
# キャプチャ用のオブジェクト
cap = None
# データ受信用のオブジェクト備
response = None
# 通信用のソケットを作成
# ※アドレスファミリ：AF_INET（IPv4）、ソケットタイプ：SOCK_DGRAM（UDP）
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 自ホストで使用するIPアドレスとポート番号を設定
sock.bind(('', TELLO_PORT))
# 問い合わせスレッド起動
ask_thread = threading.Thread(target=ask)
ask_thread.daemon = True
ask_thread.start()
# 受信用スレッドの作成
recv_thread = threading.Thread(target=udp_receiver, args=())
recv_thread.daemon = True
recv_thread.start()
# コマンドモード
sock.sendto('command'.encode('utf-8'), TELLO_ADDRESS)
time.sleep(2)
# カメラ映像のストリーミング開始
sock.sendto('streamon'.encode('utf-8'), TELLO_ADDRESS)
time.sleep(2)
if cap is None:
    cap = cv2.VideoCapture(TELLO_CAMERA_ADDRESS)
if not cap.isOpened():
    cap.open(TELLO_CAMERA_ADDRESS)
# cap = cv2.VideoCapture(0)
time.sleep(2)
count = 0
sent = sock.sendto('setfps low'.encode(encoding="utf-8"), TELLO_ADDRESS)
# Telloクラスを使って，droneというインスタンス(実体)を作る
current_time = time.time()  # 現在時刻の保存変数
pre_time = current_time     # 5秒ごとの'command'送信のための時刻変数
time.sleep(0.5)     # 通信が安定するまでちょっと待つ
# ウィンドウのタイトル
window_title = "OpenCV Window"
out_image = 0
# ウィンドウを生成
cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)

# 4色のHSVしきい値定義
# 赤: H(0-10, 170-179), S(100-255), V(50-255)
# 青: H(100-140), S(100-255), V(50-255)
# 黄: H(20-40), S(100-255), V(50-255)
# 黒: S(0-255), V(0-60)
COLOR_RANGES = {
    'red1': ((0, 100, 50), (10, 255, 255)),
    'red2': ((170, 100, 50), (179, 255, 255)),
    'blue': ((100, 100, 50), (140, 255, 255)),
    'yellow': ((20, 100, 50), (40, 255, 255))
}
a = b = c = d = 0   # rcコマンドの初期値を入力
b = 0              # 前進の値を0に設定
flag = 0

# 繰り返し実行
try:
    while True:
        # (A)画像取得
        ret, frame = cap.read()  # 映像を1フレーム取得
        if frame is None or frame.size == 0:    # 中身がおかしかったら無視
            continue
        image = frame
        # (B)ここから画像処理
        # image = cv2.imread("IMG_7614.jpg")
        # image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)      # OpenCV用のカラー並びに変換する（既にBGRなので現状必要なし）
        small_image = cv2.resize(image, dsize=(480,360) )   # 画像サイズを半分に変更
        # 注目する領域(ROI)を広げて少し先まで見えるようにする (150から下にする)
        bgr_image = small_image[150:359,0:479]              
        hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)  # BGR画像 -> HSV画像
        
        # 4色のマスクを作成して合成する
        mask = np.zeros(hsv_image.shape[:2], dtype=np.uint8)
        for name, (lower, upper) in COLOR_RANGES.items():
            lower_bound = np.array(lower, dtype=np.uint8)
            upper_bound = np.array(upper, dtype=np.uint8)
            color_mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
            mask = cv2.bitwise_or(mask, color_mask)
            
        bin_image = mask
        kernel = np.ones((15,15),np.uint8)  # 15x15で膨張させる
        dilation_image = cv2.dilate(bin_image,kernel,iterations = 1)    # 膨張して線を太くつなげる
        #erosion_image = cv2.erode(dilation_image,kernel,iterations = 1)    # 収縮
        # bitwise_andで元画像にマスクをかける -> マスクされた部分の色だけ残る
        masked_image = cv2.bitwise_and(bgr_image, bgr_image, mask=dilation_image)
        # ラベリング結果書き出し用に画像を準備
        out_image = masked_image
        # 面積・重心計算付きのラベリング処理を行う
        num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(dilation_image)
        # 最大のラベルは画面全体を覆う黒なので不要．データを削除
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        center = np.delete(center, 0, 0)
        if num_labels >= 1:
            # 面積最大のインデックスを取得
            max_index = np.argmax(stats[:,4])
            #print max_index
            # 面積最大のラベルのx,y,w,h,面積s,重心位置mx,myを得る
            x = stats[max_index][0]
            y = stats[max_index][1]
            w = stats[max_index][2]
            h = stats[max_index][3]
            s = stats[max_index][4]
            mx = int(center[max_index][0])
            my = int(center[max_index][1])
            print("(x,y)=%d,%d (w,h)=%d,%d s=%d (mx,my)=%d,%d"%(x, y, w, h, s, mx, my) )
            # ラベルを囲うバウンディングボックスを描画
            cv2.rectangle(out_image, (x, y), (x+w, y+h), (255, 0, 255))
            # 重心位置の座標を表示
            # cv2.putText(out_image, "%d,%d"%(mx,my), (x-15, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
            cv2.putText(out_image, "%d"%(s), (x, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
            # a：左右，b：前後，c：上下，d：ヨー角
            if flag == 1:
                # 左右旋回のdだけが変化する．
                dx = 1.0 * (240 - mx)       # 画面中心との差分
                # 旋回方向の不感帯を設定
                d = 0.0 if abs(dx) < 30.0 else dx   # 少し敏感に±30未満ならゼロにする
                d = -d
                
                # 直角コーナー対応: 旋回量が大きい時は前進速度bを落として旋回を優先する
                base_speed = 30
                # 旋回量(dx)に応じて減速。dxが240に近い(端にある)と速度はほぼ0になる。
                auto_b = base_speed - (abs(dx) * 0.15)
                auto_b = 30 if auto_b > 30 else auto_b
                auto_b = 0 if auto_b < 0 else auto_b
                b = auto_b
                
                # 旋回方向のソフトウェアリミッタ(±80を超えないように)
                d =  80 if d >  80.0 else d
                d = -80 if d < -80.0 else d
                print('dx=%f, b=%f, d=%f'%(dx, b, d) )
                sock.sendto(('rc %s %s %s %s'%(int(a), int(b), int(c), int(d))).encode(encoding="utf-8"), TELLO_ADDRESS )
        # (X)ウィンドウに表示
        out_image = masked_image
        # 画面にバッテリー残量と最後のコマンドを表示（デバッグ用）
        cv2.putText(out_image, battery_text, (10, 20), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
        cv2.putText(out_image, "Cmd: " + command_text, (10, 50), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
        cv2.putText(out_image, status_text, (10, 80), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
        cv2.imshow('OpenCV Window', out_image)  # ウィンドウに表示するイメージを変えれば色々表示できる
        # (Y)OpenCVウィンドウでキー入力を1ms待つ
        key = cv2.waitKey(1)

        # escキーで終了
        if key == 27:
            break
        # wキーで前進
        elif key == ord('w'):
            forward()
            command_text = "Forward"
        # sキーで後進
        elif key == ord('s'):
            back()
            command_text = "Back"
        # aキーで左進
        elif key == ord('a'):
            left()
            command_text = "Left"
        # dキーで右進
        elif key == ord('d'):
            right()
            command_text = "Right"
        # tキーで離陸
        elif key == ord('t'):
            takeoff()
            command_text = "Take off"
        # lキーで着陸
        elif key == ord('l'):
            land()
            command_text = "Land"
        # rキーで上昇
        elif key == ord('r'):
            up()
            command_text = "Up"
        # cキーで下降
        elif key == ord('c'):
            down()
            command_text = "Down"
        # qキーで左回りに回転
        elif key == ord('q'):
            ccw()
            command_text = "Ccw"
        # eキーで右回りに回転
        elif key == ord('e'):
            cw()
            command_text = "Cw"
        # 追跡モードをON
        elif key == ord('1'):
            flag = 1
        # 追跡モードをOFF
        elif key == ord('2'):
            flag = 0
            sock.sendto('rc 0 0 0 0'.encode(encoding="utf-8"), TELLO_ADDRESS )
        elif key == ord('y'):           # 前進速度をキー入力で可変
            b = b + 10
            if b > 100:
                b = 100
        elif key == ord('h'):
            b = b - 10
            if b < 0:
                b = 0
        # (Z)5秒おきに'command'を送って、死活チェックを通す
        current_time = time.time()  # 現在時刻を取得
        if current_time - pre_time > 5.0 :  # 前回時刻から5秒以上経過しているか？
            sock.sendto('command'.encode(encoding="utf-8"), TELLO_ADDRESS)   # 'command'送信
            pre_time = current_time         # 前回時刻を更新
except( KeyboardInterrupt, SystemExit):    # Ctrl+cが押されたら離脱
    print( "SIGINTを検知" )
# cap.release()
cv2.destroyAllWindows()
# ビデオストリーミング停止
sock.sendto('streamoff'.encode('utf-8'), TELLO_ADDRESS)