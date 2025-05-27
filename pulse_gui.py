import tkinter as tk
import RPi.GPIO as GPIO
import time
import os

PIN = 18  # GPIO BCM 번호

class PulseGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("GPIO Pulse Generator")
        master.attributes('-fullscreen', True)  # 전체화면 모드

        self.pulse_width_ms = 1000  # 기본 1000ms
        self.unit = 'ms'  # 기본 단위
        self.current_input = ""

        self.status = tk.Label(master, text="Ready", fg="blue", font=("Arial", 18))
        self.status.pack(pady=20)

        self.display = tk.Entry(master, font=("Arial", 24), justify='right')
        self.display.pack(pady=10, fill='x', padx=20)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack()
        self.create_keypad()

        action_frame = tk.Frame(master)
        action_frame.pack(pady=20)
        tk.Button(action_frame, text="Apply", font=("Arial", 18), width=10, command=self.apply_input).grid(row=0, column=0, padx=10)
        tk.Button(action_frame, text="Start", font=("Arial", 18), width=10, command=self.send_pulse).grid(row=0, column=1, padx=10)
        tk.Button(action_frame, text="Shutdown Pi", font=("Arial", 18), width=14, command=self.shutdown_pi).grid(row=0, column=2, padx=10)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.LOW)

    def create_keypad(self):
        keys = [['7', '8', '9'], ['4', '5', '6'], ['1', '2', '3'], ['0', 'CLR', 'MS/S']]
        for r, row in enumerate(keys):
            for c, key in enumerate(row):
                btn = tk.Button(self.button_frame, text=key, font=("Arial", 18), width=6, height=2,
                                command=lambda k=key: self.key_press(k))
                btn.grid(row=r, column=c, padx=5, pady=5)

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
