import socket
import threading
import cv2
import time
import os
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
# トラックバーを作るため，まず最初にウィンドウを生成
cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
# トラックバーのコールバック関数は何もしない空の関数
# コールバック関数（トラックバーが変更されたときに呼ばれる関数）
def on_trackbar(val):
    global out_image
    if out_image is not None:
        # 二値化
        ret, dst = cv2.threshold(out_image, val, 255, cv2.THRESH_BINARY)
        # 画像の表示
        cv2.imshow(window_title, dst)

#############################################

# 赤色検出と四角形コースの1周判定パラメータ
# OpenCVのHは0～179。赤は境界をまたぐため2範囲を合成する。
H_MIN, H_MAX = 0, 10
S_MIN, S_MAX = 100, 255
V_MIN, V_MAX = 100, 255
RED_H_MIN_2, RED_H_MAX_2 = 170, 179

TRACE_SPEED = 25
STRAIGHT_DISTANCE_SEQUENCE_CM = [350, 340, 330, 330]
MIN_STRAIGHT_DISTANCE_CM = STRAIGHT_DISTANCE_SEQUENCE_CM[0]
TURN_UNLOCK_MARGIN_CM = 130
EARLY_TURN_DX_THRESHOLD = 60
EARLY_TURN_WIDTH_THRESHOLD = 300
TURN_SPEED = 10
FORCE_TURN_FORWARD_SPEED = 0
CORNER_FORCE_TURN_SECONDS = 2.0
AFTER_TURN_SPEED = 10
AFTER_TURN_SECONDS = 2.0
CORNER_AREA_THRESHOLD = 15000
CORNER_WIDTH_THRESHOLD = 300
LOST_SEARCH_SPEED = 5
LOST_SEARCH_YAW = 50
MAX_LOST_FRAMES = 45
TRACE_LOG_INTERVAL = 1.0
NEAR_TURN_TRACE_LOG_INTERVAL = 0.25
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "drone_linetrace_trace.log")
DEADBAND = 25
YAW_GAIN = 1.2
YAW_LIMIT = 100
MIN_RED_AREA = 300
MIN_LAP_SECONDS = 8.0
# Telloのrcコマンドではdの正方向が時計回り。
CLOCKWISE_YAW_SIGN = 1
CORNER_YAW_THRESHOLD = 55
STRAIGHT_YAW_THRESHOLD = 20
STRAIGHT_CONFIRM_FRAMES = 8
TOTAL_CORNERS = 4

#############################################


# トラックバーの生成
cv2.createTrackbar("H_min", window_title, H_MIN, 179, on_trackbar)
cv2.createTrackbar("H_max", window_title, H_MAX, 179, on_trackbar)     # Hueの最大値は179
cv2.createTrackbar("S_min", window_title, S_MIN, 255, on_trackbar)
cv2.createTrackbar("S_max", window_title, S_MAX, 255, on_trackbar)
cv2.createTrackbar("V_min", window_title, V_MIN, 255, on_trackbar)
cv2.createTrackbar("V_max", window_title, V_MAX, 255, on_trackbar)
a = b = c = d = 0   # rcコマンドの初期値を入力
b = TRACE_SPEED      # 赤線追跡時の前進速度
flag = 0
lap_started_at = None
corner_count = 0
in_corner = False
straight_frame_count = 0
lap_completed = False
turn_unlocked = False
estimated_distance = 0.0
last_trace_time = None
next_turn_allowed_distance = MIN_STRAIGHT_DISTANCE_CM
corner_turn_started_at = None
lost_frame_count = 0
last_trace_log_at = 0.0
stop_logged = False
after_turn_until = 0.0

def write_log(message):
    line = f"{time.strftime('%H:%M:%S')} {message}"
    print(line)
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(line + "\n")

def log_event(name, **fields):
    details = " ".join(f"{key}={value}" for key, value in fields.items())
    if details:
        write_log(f"======== {name} {details} ========")
    else:
        write_log(f"======== {name} ========")

def straight_distance_for_corner(corner_index):
    index = min(corner_index, len(STRAIGHT_DISTANCE_SEQUENCE_CM) - 1)
    return STRAIGHT_DISTANCE_SEQUENCE_CM[index]

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
        bgr_image = small_image[200:359,0:479]              # 注目する領域(ROI)を(0,200)-(479,359)で切り取る
        # cv2.imshow('test Window', bgr_image)
        hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)  # BGR画像 -> HSV画像
        # hsv_image = bgr_image
        # cv2.imshow('test Window', hsv_image)
        # トラックバーの値を取る
        h_min = cv2.getTrackbarPos("H_min", window_title)
        h_max = cv2.getTrackbarPos("H_max", window_title)
        s_min = cv2.getTrackbarPos("S_min", window_title)
        s_max = cv2.getTrackbarPos("S_max", window_title)
        v_min = cv2.getTrackbarPos("V_min", window_title)
        v_max = cv2.getTrackbarPos("V_max", window_title)
        on_trackbar(h_min)
        on_trackbar(h_max)
        on_trackbar(s_min)
        on_trackbar(s_max)
        on_trackbar(v_min)
        on_trackbar(v_max)
        # 赤はH=0付近とH=179付近に分かれるので、2つのマスクを合成する。
        red_mask_1 = cv2.inRange(
            hsv_image,
            (h_min, s_min, v_min),
            (h_max, s_max, v_max)
        )
        red_mask_2 = cv2.inRange(
            hsv_image,
            (RED_H_MIN_2, s_min, v_min),
            (RED_H_MAX_2, s_max, v_max)
        )
        bin_image = cv2.bitwise_or(red_mask_1, red_mask_2)
        kernel = np.ones((9,9),np.uint8)
        dilation_image = cv2.morphologyEx(bin_image, cv2.MORPH_CLOSE, kernel)
        #erosion_image = cv2.erode(dilation_image,kernel,iterations = 1)    # 収縮
        # bitwise_andで元画像にマスクをかける -> マスクされた部分の色だけ残る
        masked_image = cv2.bitwise_and(hsv_image, hsv_image, mask=dilation_image)
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
            # 詳細な座標ログは[TRACE]に集約する。
            # ラベルを囲うバウンディングボックスを描画
            cv2.rectangle(out_image, (x, y), (x+w, y+h), (255, 0, 255))
            # 重心位置の座標を表示
            # cv2.putText(out_image, "%d,%d"%(mx,my), (x-15, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
            cv2.putText(out_image, "%d"%(s), (x, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
            # a：左右，b：前後，c：上下，d：ヨー角
            if flag == 1 and s >= MIN_RED_AREA:
                if lap_started_at is None:
                    lap_started_at = time.time()
                    last_trace_time = lap_started_at
                    estimated_distance = 0.0
                    next_turn_allowed_distance = MIN_STRAIGHT_DISTANCE_CM
                    lost_frame_count = 0
                    stop_logged = False
                    log_event("TRACE START", speed=TRACE_SPEED, first_turn_distance_cm=MIN_STRAIGHT_DISTANCE_CM)
                lost_frame_count = 0
                stop_logged = False

                # a=c=0，直線はb=40、角では前進を落として旋回を強める。
                # 左右旋回のdだけが変化する．
                # 前進速度のbはキー入力で変える．
                elapsed = time.time() - lap_started_at
                dx = 1.0 * (mx - 240)       # 画面中心との差分
                # 旋回方向の不感帯を設定
                d = 0.0 if abs(dx) < DEADBAND else dx * YAW_GAIN
                # 旋回方向のソフトウェアリミッタ
                d =  YAW_LIMIT if d >  YAW_LIMIT else d
                d = -YAW_LIMIT if d < -YAW_LIMIT else d

                corner_candidate = (
                    s >= CORNER_AREA_THRESHOLD
                    or w >= CORNER_WIDTH_THRESHOLD
                )
                near_turn_distance = (
                    estimated_distance >= next_turn_allowed_distance - TURN_UNLOCK_MARGIN_CM
                )
                early_turn_candidate = (
                    not in_corner
                    and corner_count < TOTAL_CORNERS
                    and near_turn_distance
                    and (abs(dx) >= EARLY_TURN_DX_THRESHOLD or w >= EARLY_TURN_WIDTH_THRESHOLD)
                )

                if in_corner:
                    force_turn_elapsed = time.time() - corner_turn_started_at
                    if force_turn_elapsed < CORNER_FORCE_TURN_SECONDS:
                        b = FORCE_TURN_FORWARD_SPEED
                        d = CLOCKWISE_YAW_SIGN * YAW_LIMIT
                    else:
                        in_corner = False
                        straight_frame_count = 0
                        next_distance = straight_distance_for_corner(corner_count)
                        next_turn_allowed_distance = estimated_distance + next_distance
                        turn_unlocked = False
                        lost_frame_count = 0
                        stop_logged = False
                        after_turn_until = time.time() + AFTER_TURN_SECONDS
                        b = AFTER_TURN_SPEED
                        d = 0
                        log_event(
                            "TURN END",
                            corner=f"{corner_count}/{TOTAL_CORNERS}",
                            elapsed=f"{elapsed:.1f}s",
                            mx=mx,
                            my=my,
                            area=s,
                            width=w,
                            speed=int(b),
                            yaw=int(d),
                            next_distance_cm=next_distance,
                            next_turn_distance_cm=f"{next_turn_allowed_distance:.0f}",
                        )
                elif estimated_distance < next_turn_allowed_distance and not early_turn_candidate:
                    b = AFTER_TURN_SPEED if time.time() < after_turn_until else TRACE_SPEED
                    d = 0
                else:
                    if not turn_unlocked:
                        turn_unlocked = True
                        log_event(
                            "TURN UNLOCK",
                            reason="early-corner" if early_turn_candidate else "distance",
                            elapsed=f"{elapsed:.1f}s",
                            distance_cm=f"{estimated_distance:.0f}",
                            corner=f"{corner_count + 1}/{TOTAL_CORNERS}",
                            required_cm=f"{next_turn_allowed_distance:.0f}",
                        )
                    if early_turn_candidate:
                        log_event(
                            "EARLY TURN",
                            dx=f"{dx:+.1f}",
                            width=w,
                            area=s,
                            distance_cm=f"{estimated_distance:.0f}",
                            required_cm=f"{next_turn_allowed_distance:.0f}",
                        )
                    if not in_corner and (corner_candidate or early_turn_candidate):
                        in_corner = True
                        straight_frame_count = 0
                        corner_turn_started_at = time.time()
                        corner_count += 1
                        turn_reason = "early-corner" if early_turn_candidate and not corner_candidate else "visual"
                        log_event(
                            "TURN START",
                            reason=turn_reason,
                            corner=f"{corner_count}/{TOTAL_CORNERS}",
                            elapsed=f"{elapsed:.1f}s",
                            mx=mx,
                            my=my,
                            area=s,
                            width=w,
                            speed=FORCE_TURN_FORWARD_SPEED,
                            yaw=YAW_LIMIT,
                        )
                        b = FORCE_TURN_FORWARD_SPEED
                        d = CLOCKWISE_YAW_SIGN * YAW_LIMIT

                    if not in_corner:
                        normal_speed = AFTER_TURN_SPEED if time.time() < after_turn_until else TRACE_SPEED
                        b = TURN_SPEED if abs(d) >= CORNER_YAW_THRESHOLD else normal_speed

                now = time.time()
                if last_trace_time is not None:
                    estimated_distance += max(0, b) * (now - last_trace_time)
                last_trace_time = now

                trace_log_interval = (
                    NEAR_TURN_TRACE_LOG_INTERVAL
                    if near_turn_distance or in_corner
                    else TRACE_LOG_INTERVAL
                )
                if time.time() - last_trace_log_at >= trace_log_interval:
                    write_log('[TRACE] dx=%+.1f b=%d d=%d dist=%d/%d area=%d w=%d mx=%d my=%d corner=%d/%d lost=%d near=%d early=%d in_turn=%d'%(
                        dx, b, d, estimated_distance, next_turn_allowed_distance,
                        s, w, mx, my, corner_count, TOTAL_CORNERS, lost_frame_count,
                        1 if near_turn_distance else 0,
                        1 if early_turn_candidate else 0,
                        1 if in_corner else 0,
                    ))
                    last_trace_log_at = time.time()
                sock.sendto(('rc %s %s %s %s'%(int(a), int(b), int(c), int(d))).encode(encoding="utf-8"), TELLO_ADDRESS )

                # 4つ目の角を抜けて直線へ戻ったら1周完了。
                if (
                    corner_count >= TOTAL_CORNERS
                    and not in_corner
                    and elapsed >= MIN_LAP_SECONDS
                ):
                    flag = 0
                    lap_completed = True
                    command_text = "Lap completed"
                    sock.sendto('rc 0 0 0 0'.encode(encoding="utf-8"), TELLO_ADDRESS)
                    print("1周完了：停止しました。Lキーで着陸してください")
            elif flag == 1:
                lost_frame_count += 1
                if lost_frame_count == 1:
                    log_event("RED LOST", reason="small-area", area=s, min_area=MIN_RED_AREA, dist=f"{estimated_distance:.0f}")
                near_turn_distance = estimated_distance >= next_turn_allowed_distance - TURN_UNLOCK_MARGIN_CM
                if near_turn_distance and not in_corner:
                    in_corner = True
                    straight_frame_count = 0
                    corner_turn_started_at = time.time()
                    corner_count += 1
                    log_event(
                        "TURN START",
                        reason="red-lost",
                        corner=f"{corner_count}/{TOTAL_CORNERS}",
                        speed=FORCE_TURN_FORWARD_SPEED,
                        yaw=YAW_LIMIT,
                        dist=f"{estimated_distance:.0f}",
                    )

                if in_corner:
                    force_turn_elapsed = time.time() - corner_turn_started_at
                    if force_turn_elapsed < CORNER_FORCE_TURN_SECONDS:
                        b = FORCE_TURN_FORWARD_SPEED
                        d = CLOCKWISE_YAW_SIGN * YAW_LIMIT
                    else:
                        in_corner = False
                        straight_frame_count = 0
                        next_distance = straight_distance_for_corner(corner_count)
                        next_turn_allowed_distance = estimated_distance + next_distance
                        turn_unlocked = False
                        lost_frame_count = 0
                        stop_logged = False
                        after_turn_until = time.time() + AFTER_TURN_SECONDS
                        b = AFTER_TURN_SPEED
                        d = 0
                        log_event(
                            "TURN END",
                            reason="red-lost",
                            corner=f"{corner_count}/{TOTAL_CORNERS}",
                            speed=int(b),
                            yaw=int(d),
                            next_distance_cm=next_distance,
                            next_turn_distance_cm=f"{next_turn_allowed_distance:.0f}",
                        )
                    sock.sendto(('rc %s %s %s %s'%(int(a), int(b), int(c), int(d))).encode(encoding="utf-8"), TELLO_ADDRESS)
                    command_text = "Turning"
                elif lost_frame_count <= MAX_LOST_FRAMES:
                    b = LOST_SEARCH_SPEED
                    d = CLOCKWISE_YAW_SIGN * LOST_SEARCH_YAW
                    sock.sendto(('rc %s %s %s %s'%(int(a), int(b), int(c), int(d))).encode(encoding="utf-8"), TELLO_ADDRESS)
                    command_text = "Searching red"
                else:
                    sock.sendto('rc 0 0 0 0'.encode(encoding="utf-8"), TELLO_ADDRESS)
                    command_text = "Red line lost"
                    if not stop_logged:
                        log_event("STOP", reason="red-lost", lost_frames=lost_frame_count, dist=f"{estimated_distance:.0f}")
                        stop_logged = True
        elif flag == 1:
            lost_frame_count += 1
            if lost_frame_count == 1:
                log_event("RED LOST", reason="no-label", dist=f"{estimated_distance:.0f}")
            near_turn_distance = estimated_distance >= next_turn_allowed_distance - TURN_UNLOCK_MARGIN_CM
            if near_turn_distance and not in_corner:
                in_corner = True
                straight_frame_count = 0
                corner_turn_started_at = time.time()
                corner_count += 1
                log_event(
                    "TURN START",
                    reason="red-lost",
                    corner=f"{corner_count}/{TOTAL_CORNERS}",
                    speed=FORCE_TURN_FORWARD_SPEED,
                    yaw=YAW_LIMIT,
                    dist=f"{estimated_distance:.0f}",
                )

            if in_corner:
                force_turn_elapsed = time.time() - corner_turn_started_at
                if force_turn_elapsed < CORNER_FORCE_TURN_SECONDS:
                    b = FORCE_TURN_FORWARD_SPEED
                    d = CLOCKWISE_YAW_SIGN * YAW_LIMIT
                else:
                    in_corner = False
                    straight_frame_count = 0
                    next_distance = straight_distance_for_corner(corner_count)
                    next_turn_allowed_distance = estimated_distance + next_distance
                    turn_unlocked = False
                    lost_frame_count = 0
                    stop_logged = False
                    after_turn_until = time.time() + AFTER_TURN_SECONDS
                    b = AFTER_TURN_SPEED
                    d = 0
                    log_event(
                        "TURN END",
                        reason="red-lost",
                        corner=f"{corner_count}/{TOTAL_CORNERS}",
                        speed=int(b),
                        yaw=int(d),
                        next_distance_cm=next_distance,
                        next_turn_distance_cm=f"{next_turn_allowed_distance:.0f}",
                    )
                sock.sendto(('rc %s %s %s %s'%(int(a), int(b), int(c), int(d))).encode(encoding="utf-8"), TELLO_ADDRESS)
                command_text = "Turning"
            elif lost_frame_count <= MAX_LOST_FRAMES:
                b = LOST_SEARCH_SPEED
                d = CLOCKWISE_YAW_SIGN * LOST_SEARCH_YAW
                sock.sendto(('rc %s %s %s %s'%(int(a), int(b), int(c), int(d))).encode(encoding="utf-8"), TELLO_ADDRESS)
                command_text = "Searching red"
            else:
                sock.sendto('rc 0 0 0 0'.encode(encoding="utf-8"), TELLO_ADDRESS)
                command_text = "Red line lost"
                if not stop_logged:
                    log_event("STOP", reason="red-lost", lost_frames=lost_frame_count, dist=f"{estimated_distance:.0f}")
                    stop_logged = True

        status = (
            "LAP COMPLETE"
            if lap_completed
            else (f"TRACING RED  CORNERS:{corner_count}/{TOTAL_CORNERS}" if flag == 1 else "READY")
        )
        cv2.putText(
            out_image, status, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 255), 2, cv2.LINE_AA
        )
        # (X)ウィンドウに表示
        out_image = masked_image
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
            lap_started_at = None
            corner_count = 0
            in_corner = False
            straight_frame_count = 0
            lap_completed = False
            turn_unlocked = False
            estimated_distance = 0.0
            last_trace_time = None
            next_turn_allowed_distance = MIN_STRAIGHT_DISTANCE_CM
            corner_turn_started_at = None
            lost_frame_count = 0
            last_trace_log_at = 0.0
            stop_logged = False
            after_turn_until = 0.0
            b = TRACE_SPEED
            command_text = "Tracing red"
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
sock.sendto('rc 0 0 0 0'.encode(encoding="utf-8"), TELLO_ADDRESS)
# cap.release()
cv2.destroyAllWindows()
# ビデオストリーミング停止
sock.sendto('streamoff'.encode('utf-8'), TELLO_ADDRESS)
