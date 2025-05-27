import tkinter as tk
import RPi.GPIO as GPIO
import time
import os

PIN = 18  # BCM 기준 핀 번호

class PulseGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("GPIO Pulse Generator")
        master.attributes('-fullscreen', True)  # 전체 화면

        self.pulse_width_ms = 1000  # 기본 1000ms
        self.unit = 'ms'  # 기본 단위
        self.current_input = ""

        # 상태 표시
        self.status = tk.Label(master, text="Ready", fg="blue", font=("Arial", 18))
        self.status.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

        # 입력창
        self.display = tk.Entry(master, font=("Arial", 24), justify='right')
        self.display.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        # 숫자 키패드 프레임
        self.button_frame = tk.Frame(master)
        self.button_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.create_keypad()

        # 동작 버튼 프레임
        action_frame = tk.Frame(master)
        action_frame.grid(row=3, column=0, columnspan=3, pady=20, sticky="ew")

        tk.Button(action_frame, text="Apply", font=("Arial", 20), command=self.apply_input).grid(row=0, column=0, padx=10, sticky="ew")
        tk.Button(action_frame, text="Start", font=("Arial", 20), command=self.send_pulse).grid(row=0, column=1, padx=10, sticky="ew")
        tk.Button(action_frame, text="Shutdown Pi", font=("Arial", 20), command=self.shutdown_pi).grid(row=0, column=2, padx=10, sticky="ew")

        for i in range(3):
            action_frame.columnconfigure(i, weight=1)

        # 전체 행/열 비율 조정
        for i in range(4):
            master.rowconfigure(i, weight=1)
        for i in range(3):
            master.columnconfigure(i, weight=1)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.LOW)

    def create_keypad(self):
        keys = [['7', '8', '9'], ['4', '5', '6'], ['1', '2', '3'], ['0', 'CLR', 'MS/S']]

        for r, row in enumerate(keys):
            for c, key in enumerate(row):
                btn = tk.Button(self.button_frame, text=key, font=("Arial", 24),
                                command=lambda k=key: self.key_press(k))
                btn.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

        # 키패드 그리드 확장
        for i in range(4):
            self.button_frame.rowconfigure(i, weight=1)
        for i in range(3):
            self.button_frame.columnconfigure(i, weight=1)

    def key_press(self, key):
        if key == 'CLR':
            self.current_input = ""
        elif key == 'MS/S':
            self.unit = 's' if self.unit == 'ms' else 'ms'
        else:
            self.current_input += key
        self.update_display()

    def update_display(self):
        suffix = ' s' if self.unit == 's' else ' ms'
        self.display.delete(0, tk.END)
        self.display.insert(0, self.current_input + suffix)

    def apply_input(self):
        try:
            val = int(self.current_input)
            if self.unit == 's':
                self.pulse_width_ms = val * 1000
            else:
                self.pulse_width_ms = val
            self.status.config(text=f"Pulse set to {self.pulse_width_ms} ms", fg="green")
        except ValueError:
            self.status.config(text="Invalid input!", fg="red")

    def send_pulse(self):
        self.status.config(text=f"Pulse sent: {self.pulse_width_ms} ms", fg="blue")
        GPIO.output(PIN, GPIO.HIGH)
        self.master.update()  # GUI 갱신
        time.sleep(self.pulse_width_ms / 1000.0)
        GPIO.output(PIN, GPIO.LOW)

    def shutdown_pi(self):
        self.cleanup()
        os.system("sudo shutdown now")

    def cleanup(self):
        GPIO.output(PIN, GPIO.LOW)
        GPIO.cleanup()

    def on_close(self):
        self.cleanup()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PulseGeneratorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
