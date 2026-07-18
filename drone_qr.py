import socket
import threading
import cv2
import time
import numpy as np
from pynput import keyboard


RC_SPEED = 40
pressed_keys = set()
pressed_keys_lock = threading.Lock()
control_running = True


def on_key_press(key):
    try:
        char = key.char.lower()
    except AttributeError:
        if key == keyboard.Key.left:
            char = 'left_arrow'
        elif key == keyboard.Key.right:
            char = 'right_arrow'
        elif key == keyboard.Key.up:
            char = 'up_arrow'
        elif key == keyboard.Key.down:
            char = 'down_arrow'
        else:
            return

    if char in {'w', 's', 'a', 'd', 'up_arrow', 'down_arrow', 'left_arrow', 'right_arrow'}:
        with pressed_keys_lock:
            pressed_keys.add(char)


def on_key_release(key):
    try:
        char = key.char.lower()
    except AttributeError:
        if key == keyboard.Key.left:
            char = 'left_arrow'
        elif key == keyboard.Key.right:
            char = 'right_arrow'
        elif key == keyboard.Key.up:
            char = 'up_arrow'
        elif key == keyboard.Key.down:
            char = 'down_arrow'
        else:
            return

    with pressed_keys_lock:
        pressed_keys.discard(char)


def keyboard_control():
    """押されているキーに応じた連続制御コマンドを20Hzで送る。"""
    global command_text

    while control_running:
        with pressed_keys_lock:
            keys = pressed_keys.copy()

        # rc: 左右、前後、上下、旋回（各 -100 ～ 100）
        lr = RC_SPEED * (('d' in keys) - ('a' in keys))
        fb = RC_SPEED * (('w' in keys) - ('s' in keys))
        ud = RC_SPEED * (('up_arrow' in keys) - ('down_arrow' in keys))
        yaw = RC_SPEED * (('right_arrow' in keys) - ('left_arrow' in keys))

        try:
            sock.sendto(f'rc {lr} {fb} {ud} {yaw}'.encode('utf-8'), TELLO_ADDRESS)
        except OSError:
            pass

        active = [name for key, name in (
            ('w', 'Forward'), ('s', 'Back'), ('a', 'Left'), ('d', 'Right'),
            ('up_arrow', 'Up(Up)'), ('down_arrow', 'Down(Down)'), ('left_arrow', 'Ccw(Left)'), ('right_arrow', 'Cw(Right)')
        ) if key in keys]
        if active:
            command_text = '+'.join(active)
        elif command_text in {
            'Forward', 'Back', 'Left', 'Right', 'Up', 'Down', 'Ccw', 'Cw'
        } or '+' in command_text:
            command_text = 'Stop'

        time.sleep(0.05)

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
            sent = sock.sendto('takeoff'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
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
            sent = sock.sendto('forward 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 後に進む(0cm)
def back():
        try:
            sent = sock.sendto('back 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 右に進む(0cm)
def right():
        try:
            sent = sock.sendto('right 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 左に進む(0cm)
def left():
        try:
            sent = sock.sendto('left 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
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
def set_speed(n=40):
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
ask_thread.setDaemon(True)
ask_thread.start()

# 受信用スレッドの作成
recv_thread = threading.Thread(target=udp_receiver, args=())
recv_thread.daemon = True
recv_thread.start()

# コマンドモード
sock.sendto('command'.encode('utf-8'), TELLO_ADDRESS)

time.sleep(1)

# キーの押下・解放を監視し、連続制御を開始
key_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
key_listener.start()
control_thread = threading.Thread(target=keyboard_control, daemon=True)
control_thread.start()

# カメラ映像のストリーミング開始
sock.sendto('streamon'.encode('utf-8'), TELLO_ADDRESS)

time.sleep(1)

if cap is None:
    cap = cv2.VideoCapture(TELLO_CAMERA_ADDRESS)

if not cap.isOpened():
    cap.open(TELLO_CAMERA_ADDRESS)
# cap = cv2.VideoCapture(0)

time.sleep(1)

# 最新フレームを常に取得し続ける裏側スレッド（映像のラグ解消・操縦性向上）
latest_frame = None
def video_capture_thread():
    global latest_frame
    while True:
        ret, frame = cap.read()
        if ret:
            latest_frame = frame
        else:
            time.sleep(0.01)

vcap_thread = threading.Thread(target=video_capture_thread)
vcap_thread.daemon = True
vcap_thread.start()
cnt_frame = 0

# qrコード読み取り用のインスタンス
qcd = cv2.QRCodeDetector()


while True:
    frame = latest_frame
    cnt_frame += 1

    # 動画フレームが空ならスキップ
    if frame is None or frame.size == 0:
        time.sleep(0.01)
        continue

    # カメラ映像のサイズを半分にする
    frame_height, frame_width = frame.shape[:2]
    frame_resized = cv2.resize(frame, (frame_width//3, frame_height//3))
    frame_output = frame_resized

    # qrコードの読み取り
    if cnt_frame % 5 == 0:
        retval, decoded_info, points, straight_qrcode = qcd.detectAndDecodeMulti(frame_resized)
        if retval:
            frame_qrdet = cv2.polylines(frame_resized, points.astype(int), True, (0, 255, 0), 3)
            frame_ouput = frame_qrdet

        if len(decoded_info) != 0:
            print(f"読み取り結果(result)：{decoded_info}")




    # 送信したコマンドを表示
    cv2.putText(frame_output,
            text="Cmd:" + command_text,
            org=(10, 20),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # バッテリー残量を表示
    cv2.putText(frame_output,
            text=battery_text,
            org=(10, 40),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # 飛行時間を表示
    cv2.putText(frame_output,
            text=time_text,
            org=(10, 60),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # ステータスを表示
    cv2.putText(frame_output,
            text=status_text,
            org=(10, 80),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # 現在の速度設定を表示
    cv2.putText(frame_output,
            text=f"Speed: {RC_SPEED}",
            org=(10, 100),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 255),
            thickness=1,
            lineType=cv2.LINE_4)
    # カメラ映像を画面に表示
    cv2.imshow('Tello Camera View', frame_output)

    # キー入力を取得
    key = cv2.waitKey(1)

    # escキーで終了
    if key == 27:
        break
    # tキーで離陸
    elif key == ord('t'):
        takeoff()
        command_text = "Take off"
    # lキーで着陸
    elif key == ord('l'):
        land()
        command_text = "Land"
    # uキーで速度アップ
    elif key == ord('u'):
        RC_SPEED = min(100, RC_SPEED + 10)
        command_text = "Speed Up"
    # jキーで速度ダウン
    elif key == ord('j'):
        RC_SPEED = max(10, RC_SPEED - 10)
        command_text = "Speed Down"

control_running = False
key_listener.stop()
control_thread.join(timeout=0.2)
sock.sendto('rc 0 0 0 0'.encode('utf-8'), TELLO_ADDRESS)
cap.release()
cv2.destroyAllWindows()

# ビデオストリーミング停止
sock.sendto('streamoff'.encode('utf-8'), TELLO_ADDRESS)
