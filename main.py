
from machine import Pin, ADC
from neopixel import NeoPixel
import dht
import time

# =====================================
# 교실 환기 타이밍 알리미 - 최종 버전
# Raspberry Pi Pico 2 W / MicroPython
# =====================================

# 1. WS2813 RGB LED 설정
TIMING = (280, 515, 515, 745)
LED_PIN = 16
LED_COUNT = 10

led = NeoPixel(
    Pin(LED_PIN),
    LED_COUNT,
    timing=TIMING
)

# 2. MQ-2 가스 센서 (A0)
mq2 = ADC(Pin(26))

# 3. DHT11 온습도 센서 (SPI0 CS)
sensor = dht.DHT11(Pin(5))

# 4. LED 색상 및 밝기
GREEN = (0, 60, 0)
YELLOW = (60, 45, 0)
RED = (60, 0, 0)
OFF = (0, 0, 0)

# 5. 시연용 임계값
GAS_GREEN_MAX = 7000
GAS_YELLOW_MAX = 8500

TEMP_YELLOW = 28
TEMP_RED = 32

HUM_YELLOW = 70
HUM_RED = 85

# 측정 간격 (초)
INTERVAL = 2


# =====================================
# LED 제어 함수
# =====================================

def fill(color):
    for i in range(LED_COUNT):
        led[i] = color
    led.write()


# =====================================
# 가스 상태 판정
# =====================================

def gas_level(gas):
    if gas <= GAS_GREEN_MAX:
        return 0
    elif gas <= GAS_YELLOW_MAX:
        return 1
    else:
        return 2


# =====================================
# 온도 상태 판정
# =====================================

def temp_level(temp):
    if temp >= TEMP_RED:
        return 2
    elif temp >= TEMP_YELLOW:
        return 1
    else:
        return 0


# =====================================
# 습도 상태 판정
# =====================================

def hum_level(hum):
    if hum >= HUM_RED:
        return 2
    elif hum >= HUM_YELLOW:
        return 1
    else:
        return 0


# =====================================
# 메인 프로그램
# =====================================

fill(OFF)

print("============================")
print("교실 환기 타이밍 알리미 시작")
print("============================")

try:
    while True:

        # 1. 가스 센서 측정
        gas = mq2.read_u16()
        level = gas_level(gas)

        # 2. 온습도 센서 측정
        try:
            sensor.measure()

            temp = sensor.temperature()
            hum = sensor.humidity()

            # 세 센서 중 가장 높은 경고 단계
            level = max(
                level,
                temp_level(temp),
                hum_level(hum)
            )

            dht_status = "정상"

        except OSError as e:
            temp = None
            hum = None
            dht_status = "측정 오류: {}".format(e)

            # 오류 시 가스값만으로 LED 결정

        # 3. LED 색상 결정
        if level == 0:
            fill(GREEN)
            status = "초록색 - 정상"

        elif level == 1:
            fill(YELLOW)
            status = "노란색 - 환기 권장"

        else:
            fill(RED)
            status = "빨간색 - 환기 알림"

        # 4. Thonny Shell 출력
        print("----------------------------")
        print("가스값:", gas)

        if temp is not None:
            print("온도:", temp, "C")
            print("습도:", hum, "%")
        else:
            print("온습도 측정 실패")

        print("DHT11:", dht_status)
        print("LED 상태:", status)
        print("----------------------------")

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    fill(OFF)
    print("프로그램 종료")
