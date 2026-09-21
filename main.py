from machine import Pin, ADC
from neopixel import NeoPixel
import time

# ==========================================
# MQ-2 가스 센서 설정
# ==========================================
mq2 = ADC(Pin(26))       # GP26 = ADC0


# ==========================================
# WS2813 네오픽셀 설정
# ==========================================
TIMING = (280, 515, 515, 745)

LED_COUNT = 10           # 사용하는 LED 개수에 맞게 변경
led = NeoPixel(Pin(16), LED_COUNT, timing=TIMING)


# ==========================================
# 환기 기준값
# 센서의 실제 환경에 맞게 조절
# ==========================================
GOOD_LIMIT = 9000       # 이보다 작으면 좋음
CAUTION_LIMIT = 12000    # 이보다 작으면 주의
                           # 30000 이상이면 환기 필요


# ==========================================
# LED 밝기 설정
# ==========================================
BRIGHTNESS = 0.4         # 40% 밝기


# ==========================================
# LED 색상 함수
# ==========================================
def set_led_color(r, g, b):
    r = int(r * BRIGHTNESS)
    g = int(g * BRIGHTNESS)
    b = int(b * BRIGHTNESS)

    for i in range(LED_COUNT):
        led[i] = (r, g, b)

    led.write()


# ==========================================
# LED 끄기
# ==========================================
def led_off():
    for i in range(LED_COUNT):
        led[i] = (0, 0, 0)

    led.write()


# ==========================================
# 시작 시 LED 테스트
# ==========================================
set_led_color(0, 255, 0)
time.sleep(1)

set_led_color(255, 255, 0)
time.sleep(1)

set_led_color(255, 0, 0)
time.sleep(1)

led_off()


# ==========================================
# 메인 프로그램
# ==========================================
danger_blink = False

while True:

    # MQ-2 센서값 읽기
    sensor_value = mq2.read_u16()

    print("MQ-2 센서값:", sensor_value)


    # --------------------------------------
    # 1. 좋음
    # --------------------------------------
    if sensor_value < GOOD_LIMIT:

        set_led_color(0, 255, 0)

        danger_blink = False


    # --------------------------------------
    # 2. 주의
    # --------------------------------------
    elif sensor_value < CAUTION_LIMIT:

        set_led_color(255, 180, 0)

        danger_blink = False


    # --------------------------------------
    # 3. 환기 필요
    # --------------------------------------
    else:

        # 빨간색으로 깜빡이기
        set_led_color(255, 0, 0)
        time.sleep(0.5)

        led_off()
        time.sleep(0.5)


    # 1초마다 측정
    time.sleep(1)

