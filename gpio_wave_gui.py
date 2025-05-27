import tkinter as tk
import RPi.GPIO as GPIO
import time
import os
from datetime import datetime

PIN = 18  # GPIO BCM 핀 번호

class PulseGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("GPIO Pulse Generator")
        self.master.state('zoomed')  # 창 최대화, 작업표시줄 보임

        self.pulse_width_ms = 1000
        self.unit = 'ms'
        self.current_input = ""

        self.font_main = ("Consolas", 20, "bold")
        self.font_button = ("Consolas", 24, "bold")
        self.font_status = ("Consolas", 16, "bold")

        self.status = tk.Label(master, text="Ready", fg="blue", font=self.font_status)
        self.status.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

        self.display = tk.Entry(master, font=self.font_button, justify='right')
        self.display.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        self.update_display()

        self.button_frame = tk.Frame(master)
        self.button_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.create_keypad()

        action_frame = tk.Frame(master)
        action_frame.grid(row=3, column=0, columnspan=3, pady=20, sticky="ew")
        tk.Button(action_frame, text="Apply", font=self.font_main, command=self.apply_input).grid(row=0, column=0, padx=10, sticky="ew")
        tk.Button(action_frame, text="Start", font=self.font_main, command=self.send_pulse).grid(row=0, column=1, padx=10, sticky="ew")
        tk.Button(action_frame, text="Shutdown Pi", font=self.font_main, command=self.shutdown_pi).grid(row=0, column=2, padx=10, sticky="ew")

        for i in range(3):
            action_frame.columnconfigure(i, weight=1)
        for i in range(4):
            master.rowconfigure(i, weight=1)
        for i in range(3):
            master.columnconfigure(i, weight=1)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.LOW)

    def create_keypad(self):
        keys = [['7', '8', '9'],
                ['4', '5', '6'],
                ['1', '2', '3'],
                ['0', 'CLR', 'MS/S']]

        for r, row in enumerate(keys):
            for c, key in enumerate(row):
                btn = tk.Button(self.button_frame, text=key, font=self.font_button,
                                command=lambda k=key: self.key_press(k))
                btn.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

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
            self.pulse_width_ms = val * 1000 if self.unit == 's' else val
            self.status.config(text=f"Pulse set to {self.pulse_width_ms} ms", fg="green")
        except ValueError:
            self.status.config(text="Invalid input!", fg="red")

    def send_pulse(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.status.config(text=f"Pulse sent at {now} for {self.pulse_width_ms} ms", fg="blue")
        GPIO.output(PIN, GPIO.HIGH)

        start = time.perf_counter()
        target = self.pulse_width_ms / 1000.0
        while (time.perf_counter() - start) < target:
            pass  # busy-wait로 정확한 시간 유지

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
