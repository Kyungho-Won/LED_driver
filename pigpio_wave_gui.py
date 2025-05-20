import pigpio
import tkinter as tk

PIN = 18  # 하드웨어 PWM 핀 추천 (GPIO 18 등)

class PWMController:
    def __init__(self, master):
        self.master = master
        master.title("PWM Generator with pigpio")

        self.pi = pigpio.pi()
        self.freq = 200  # 기본 주파수
        self.running = False

        # GUI 구성
        tk.Label(master, text="Frequency (Hz):").grid(row=0, column=0, padx=5, pady=5)
        self.freq_entry = tk.Entry(master)
        self.freq_entry.insert(0, str(self.freq))
        self.freq_entry.grid(row=0, column=1, padx=5, pady=5)

        self.set_button = tk.Button(master, text="Set Frequency", command=self.set_frequency)
        self.set_button.grid(row=0, column=2, padx=5, pady=5)

        self.start_button = tk.Button(master, text="Start", command=self.start_pwm)
        self.start_button.grid(row=1, column=0, padx=5, pady=5)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_pwm)
        self.stop_button.grid(row=1, column=1, padx=5, pady=5)

        master.protocol("WM_DELETE_WINDOW", self.cleanup)

    def set_frequency(self):
        try:
            self.freq = int(self.freq_entry.get())
            if self.running:
                self.pi.set_PWM_frequency(PIN, self.freq)
        except ValueError:
            print("Invalid frequency")

    def start_pwm(self):
        self.running = True
        self.pi.set_PWM_frequency(PIN, self.freq)
        self.pi.set_PWM_dutycycle(PIN, 128)  # 50% duty (128/255)
        print(f"Started PWM at {self.freq} Hz")

    def stop_pwm(self):
        self.running = False
        self.pi.set_PWM_dutycycle(PIN, 0)
        print("Stopped PWM")

    def cleanup(self):
        self.stop_pwm()
        self.pi.stop()
        self.master.destroy()

# GUI 실행
root = tk.Tk()
app = PWMController(root)
root.mainloop()
