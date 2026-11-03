
from machine import Pin, ADC
import dht
import time

# =====================================
# 교실 환기 타이밍 알리미
# Raspberry Pi Pico 2 W / MicroPython
# =====================================

# 1. 센서 핀 설정
gas_sensor = ADC(Pin(26))
dht_sensor = dht.DHT11(Pin(17))

# 2. RGB LED 핀 설정
red = Pin(13, Pin.OUT)
green = Pin(14, Pin.OUT)
blue = Pin(15, Pin.OUT)

# 공통 캐소드: False
# 공통 애노드: True
COMMON_ANODE = False

# 3. 시연용 임계값
GAS_GREEN_MAX = 7000
GAS_YELLOW_MAX = 8500

TEMP_NORMAL_MIN = 18
TEMP_NORMAL_MAX = 28
TEMP_DANGER_MIN = 16
TEMP_DANGER_MAX = 32

HUM_NORMAL_MIN = 30
HUM_NORMAL_MAX = 70
HUM_DANGER_MIN = 20
HUM_DANGER_MAX = 80

# 4. LED 제어 함수
def set_led(r, g, b):
    if COMMON_ANODE:
        red.value(1 - r)
        green.value(1 - g)
        blue.value(1 - b)
    else:
        red.value(r)
        green.value(g)
        blue.value(b)

def led_green():
    set_led(0, 1, 0)

def led_yellow():
    set_led(1, 1, 0)

def led_red():
    set_led(1, 0, 0)

def led_off():
    set_led(0, 0, 0)

# 5. 가스 상태 판단
def check_gas(value):
    if value <= GAS_GREEN_MAX:
        return 0
    elif value <= GAS_YELLOW_MAX:
        return 1
    else:
        return 2

# 6. 온도 상태 판단
def check_temperature(temp):
    if temp < TEMP_DANGER_MIN or temp > TEMP_DANGER_MAX:
        return 2
    elif temp < TEMP_NORMAL_MIN or temp > TEMP_NORMAL_MAX:
        return 1
    else:
        return 0

# 7. 습도 상태 판단
def check_humidity(hum):
    if hum < HUM_DANGER_MIN or hum > HUM_DANGER_MAX:
        return 2
    elif hum < HUM_NORMAL_MIN or hum > HUM_NORMAL_MAX:
        return 1
    else:
        return 0

# 8. 메인 프로그램
print("교실 환기 타이밍 알리미 시작!")
print("MQ-2 센서 예열 및 안정화 중...")

led_off()
time.sleep(20)

last_temp = None
last_hum = None

while True:
    try:
        # 가스 센서 값 읽기
        gas_value = gas_sensor.read_u16()

        # DHT11 온습도 읽기
        try:
            dht_sensor.measure()
            last_temp = dht_sensor.temperature()
            last_hum = dht_sensor.humidity()
        except OSError:
            print("DHT11 측정 오류 - 재시도 예정")

        # 가스 상태
        gas_level = check_gas(gas_value)

        # 온습도 상태
        if last_temp is not None and last_hum is not None:
            temp_level = check_temperature(last_temp)
            hum_level = check_humidity(last_hum)

            # 가장 높은 위험 단계 선택
            final_level = max(
                gas_level,
                temp_level,
                hum_level
            )
        else:
            # 온습도 데이터가 없으면 안전상 주의 표시
            final_level = max(gas_level, 1)

        # LED 색상 결정
        if final_level == 0:
            led_green()
            status = "정상 - 환기 상태 양호"

        elif final_level == 1:
            led_yellow()
            status = "주의 - 환기 권장"

        else:
            led_red()
            status = "위험 - 환기 필요"

        # Thonny Shell 출력
        print("----------------------------")
        print("가스 ADC 값:", gas_value)

        if last_temp is not None:
            print("온도:", last_temp, "도")
            print("습도:", last_hum, "%")
        else:
            print("온습도 측정 대기 중")

        print("상태:", status)

        # 3초마다 측정
        time.sleep(3)

    except KeyboardInterrupt:
        led_off()
        print("프로그램 종료")
        break

    except Exception as e:
        led_off()
        print("오류 발생:", e)
        time.sleep(3)
