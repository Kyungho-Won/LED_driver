import RPi.GPIO as GPIO
import time

# === 설정 ===
PIN = 18
FREQ_HZ = 4  # 원하는 주파수 [Hz] 단위
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

# === 내부 계산 ===
period = 1.0 / FREQ_HZ          # 전체 주기 [s]
half_period = period / 2        # HIGH or LOW 유지 시간
state = False                   # 시작 상태 (LOW)
next_toggle = time.perf_counter()

try:
    while True:
        now = time.perf_counter()
        if now >= next_toggle:
            state = not state
            GPIO.output(PIN, state)
            print(f"{'HIGH' if state else 'LOW'} @ {now:.3f}s")
            next_toggle += half_period

        time.sleep(0.001)  # CPU 점유 줄이기

except KeyboardInterrupt:
    GPIO.cleanup()
