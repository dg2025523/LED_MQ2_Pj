
from machine import Pin, ADC, I2C
from neopixel import NeoPixel
from huskylensPythonLibrary import HuskyLensLibrary
import dht
import time

# ======================================
# 교실 환기 타이밍 알리미 + 허스키렌즈
# 학습하지 않은 얼굴도 감지
# ======================================

# 1. RGB LED (D16 = GP16)
TIMING = (280, 515, 515, 745)
LED_COUNT = 10
led = NeoPixel(Pin(16), LED_COUNT, timing=TIMING)

GREEN = (0, 60, 0)
YELLOW = (60, 45, 0)
RED = (60, 0, 0)
OFF = (0, 0, 0)

# 2. 센서
mq2 = ADC(Pin(26))        # MQ-2 : A0
sensor = dht.DHT11(Pin(5))  # DHT11 : SPI0 CS

# 3. 허스키렌즈 (I2C1)
i2c = I2C(
    1,
    sda=Pin(6),
    scl=Pin(7),
    freq=50000
)

if 0x32 not in i2c.scan():
    raise RuntimeError("허스키렌즈 연결 확인 필요")

husky = HuskyLensLibrary("I2C")
husky.face_recognition_mode()
time.sleep(0.5)

# 4. 시간 설정
SENSOR_INTERVAL = 2000
HUSKY_INTERVAL = 300
BLINK_INTERVAL = 400
PERSON_HOLD = 3000

# 5. 상태 변수
level = 0
person_detected = False
last_person_seen = None
husky_error = False

last_sensor = time.ticks_ms() - SENSOR_INTERVAL
last_husky = time.ticks_ms() - HUSKY_INTERVAL
last_blink = time.ticks_ms()

blink_on = False
last_color = None


# ======================================
# LED 제어
# ======================================

def fill(color):
    global last_color

    if color == last_color:
        return

    for i in range(LED_COUNT):
        led[i] = color

    led.write()
    last_color = color


# ======================================
# 센서별 상태
# 0 = 정상, 1 = 주의, 2 = 위험
# ======================================

def gas_level(value):
    if value <= 7000:
        return 0
    elif value <= 8500:
        return 1
    return 2


def temp_level(value):
    if value >= 32:
        return 2
    elif value >= 28:
        return 1
    return 0


def hum_level(value):
    if value >= 85:
        return 2
    elif value >= 70:
        return 1
    return 0


# ======================================
# 종합 환기 상태 판단
# ======================================

def ventilation_level(levels):

    # 하나라도 위험하면 빨간색
    if 2 in levels:
        return 2

    # 주의가 2개 이상이면 빨간색
    if levels.count(1) >= 2:
        return 2

    # 주의가 1개면 노란색
    if 1 in levels:
        return 1

    return 0


# ======================================
# 프로그램 시작
# ======================================

fill(OFF)

print("============================")
print("교실 환기 타이밍 알리미 시작")
print("허스키렌즈 얼굴 감지 모드")
print("============================")

try:
    while True:

        now = time.ticks_ms()

        # --------------------------
        # 1. 허스키렌즈 얼굴 감지
        # --------------------------
        if time.ticks_diff(
            now, last_husky
        ) >= HUSKY_INTERVAL:

            last_husky = now

            try:
                blocks = husky.command_request_blocks()

                # ID가 0이어도 얼굴로 인정
                # 얼굴 블록이 하나라도 있으면 감지
                if isinstance(blocks, list):
                    face_found = any(
                        isinstance(block, (list, tuple))
                        and len(block) >= 5
                        and block[2] > 0
                        and block[3] > 0
                        for block in blocks
                    )

                    if face_found:
                        last_person_seen = now

                    husky_error = False

            except Exception as e:
                husky_error = True
                print("허스키렌즈 오류:", e)

            # 3초 동안 얼굴 감지 유지
            person_detected = (
                not husky_error
                and last_person_seen is not None
                and time.ticks_diff(
                    now, last_person_seen
                ) < PERSON_HOLD
            )

        # --------------------------
        # 2. 가스, 온도, 습도 측정
        # --------------------------
        if time.ticks_diff(
            now, last_sensor
        ) >= SENSOR_INTERVAL:

            last_sensor = now

            gas = mq2.read_u16()
            levels = [gas_level(gas)]

            try:
                sensor.measure()

                temp = sensor.temperature()
                hum = sensor.humidity()

                levels.append(temp_level(temp))
                levels.append(hum_level(hum))

                print("온도:", temp, "C")
                print("습도:", hum, "%")

            except OSError as e:
                print("DHT11 오류:", e)
                print("가스값으로 임시 판정")

            level = ventilation_level(levels)

            print("----------------------------")
            print("가스값:", gas)
            print("주의 센서 수:", levels.count(1))
            print("환기 단계:", level)
            print("얼굴 감지:", person_detected)
            print("----------------------------")

        # --------------------------
        # 3. LED 제어
        # --------------------------

        # 얼굴이 없으면 LED 끄기
        if not person_detected:
            fill(OFF)
            blink_on = False
            last_blink = now

        # 얼굴이 있고 정상 상태
        elif level == 0:
            fill(GREEN)

        # 얼굴이 있고 주의 상태
        elif level == 1:
            fill(YELLOW)

        # 얼굴이 있고 환기 필요 상태
        else:
            if time.ticks_diff(
                now, last_blink
            ) >= BLINK_INTERVAL:

                last_blink = now
                blink_on = not blink_on

            if blink_on:
                fill(RED)
            else:
                fill(OFF)

        time.sleep_ms(50)

except KeyboardInterrupt:
    fill(OFF)
    print("프로그램 종료")
