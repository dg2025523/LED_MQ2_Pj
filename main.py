
from machine import Pin, ADC
import dht
import time

# -----------------------------
# 1. 센서 설정
# -----------------------------

# MQ-2 가스 센서
gas_sensor = ADC(Pin(26))

# DHT11 온습도 센서
temp_sensor = dht.DHT11(Pin(17))

# RGB LED 핀 설정
red_led = Pin(14, Pin.OUT)
green_led = Pin(15, Pin.OUT)
blue_led = Pin(16, Pin.OUT)

# 공통 음극형 LED는 False
# 공통 양극형 LED는 True
COMMON_ANODE = False


# -----------------------------
# 2. 온도·습도 기준
# -----------------------------

TEMP_MIN = 18
TEMP_MAX = 28

HUM_MIN = 30
HUM_MAX = 70


# -----------------------------
# 3. LED 제어
# -----------------------------

def set_led(red, green, blue):
    if COMMON_ANODE:
        red = not red
        green = not green
        blue = not blue

    red_led.value(int(red))
    green_led.value(int(green))
    blue_led.value(int(blue))


def show_green():
    set_led(False, True, False)


def show_yellow():
    set_led(True, True, False)


def show_red():
    set_led(True, False, False)


def show_off():
    set_led(False, False, False)


# -----------------------------
# 4. 프로그램 시작
# -----------------------------

show_off()

print("교실 환기 타이밍 알리미 시작")


# -----------------------------
# 5. 반복 측정
# -----------------------------

while True:

    # 가스값 읽기
    gas_value = gas_sensor.read_u16()

    # 온도와 습도 읽기
    try:
        temp_sensor.measure()
        temperature = temp_sensor.temperature()
        humidity = temp_sensor.humidity()
        dht_ok = True

    except OSError as error:
        temperature = None
        humidity = None
        dht_ok = False
        print("온습도 센서 오류:", error)

    # 온도·습도 범위 확인
    environment_outside = False

    if dht_ok:
        if (temperature < TEMP_MIN or
            temperature > TEMP_MAX or
            humidity < HUM_MIN or
            humidity > HUM_MAX):
            environment_outside = True

    # -----------------------------
    # 6. LED 색상 결정
    # -----------------------------

    # 가스값이 8500 초과: 빨간색
    if gas_value > 8500:
        status = "환기 상태 확인"
        show_red()

    # 가스값이 7000 초과~8500 이하: 노란색
    elif gas_value > 7000:
        status = "환경 확인 필요"
        show_yellow()

    # 온습도 센서 오류: 노란색
    elif not dht_ok:
        status = "온습도 센서 확인"
        show_yellow()

    # 온도·습도가 설정 범위를 벗어남: 노란색
    elif environment_outside:
        status = "온도·습도 확인"
        show_yellow()

    # 나머지: 초록색
    else:
        status = "측정값 양호"
        show_green()

    # -----------------------------
    # 7. 측정값 출력
    # -----------------------------

    print("----------------------")
    print("가스 센서값:", gas_value)

    if dht_ok:
        print("온도:", temperature, "도")
        print("습도:", humidity, "%")
    else:
        print("온도: 측정 오류")
        print("습도: 측정 오류")

    print("현재 상태:", status)

    time.sleep(2)
