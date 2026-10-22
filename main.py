
from machine import Pin, ADC
import dht
import time

# 가스 센서
gas_sensor = ADC(Pin(26))

# DHT11 온습도 센서
temp_sensor = dht.DHT11(Pin(17))

# RGB LED (공통 음극형 기준)
led_red = Pin(14, Pin.OUT)
led_green = Pin(15, Pin.OUT)
led_blue = Pin(16, Pin.OUT)

def set_led(color):
    led_red.value(1 if color == "red" else 0)
    led_green.value(1 if color in ("green", "yellow") else 0)
    led_blue.value(0)

CAUTION_LEVEL = 18000
DANGER_LEVEL = 30000

while True:
    try:
        # 가스 센서 측정
        gas_value = gas_sensor.read_u16()

        # 온도와 습도 측정
        temp_sensor.measure()
        temperature = temp_sensor.temperature()
        humidity = temp_sensor.humidity()

        # 가스 센서값에 따라 LED 색상 결정
        if gas_value >= DANGER_LEVEL:
            status = "환기 권장"
            set_led("red")
        elif gas_value >= CAUTION_LEVEL:
            status = "상태 확인"
            set_led("yellow")
        else:
            status = "측정값 양호"
            set_led("green")

        # 결과 출력
        print("가스 센서값:", gas_value)
        print("온도:", temperature, "°C")
        print("습도:", humidity, "%")
        print("상태:", status)
        print("----------------------")

    except OSError as e:
        print("센서 읽기 오류:", e)

    time.sleep(2)
