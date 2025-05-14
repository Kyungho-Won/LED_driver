import RPi.GPIO as GPIO
import time
import threading
import tkinter as tk

PIN = 18  # GPIO BCM 번호

class GPIOWaveGUI:
    def __init__(self, master):
        self.master = master
        master.title("GPIO Square Wave Generator")

        self.freq_label = tk.Label(master, text="Frequency (Hz):")
        self.freq_label.grid(row=0, column=0, padx=5, pady=5)

        self.freq_entry = tk.Entry(master)
        self.freq_entry.insert(0, "1.0")
        self.freq_entry.grid(row=0, column=1, padx=5, pady=5)

        self.set_button = tk.Button(master, text="Set Frequency", command=self.set_frequency)
        self.set_button.grid(row=0, column=2, padx=5, pady=5)

        self.start_button = tk.Button(master, text="Start", command=self.start_wave)
        self.start_button.grid(row=1, column=0, padx=5, pady=5)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_wave)
        self.stop_button.grid(row=1, column=1, padx=5, pady=5)

        self.status = tk.Label(master, text="Status: Ready", fg="blue")
        self.status.grid(row=2, column=0, columnspan=3, pady=10)

        self.frequency = 1.0  # Default frequency
        self.running = False
        self.thread = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.LOW)

    def set_frequency(self):
        try:
            freq = float(self.freq_entry.get())
            if freq <= 0:
                raise ValueError
            self.frequency = freq
            self.status.config(text=f"Frequency set to {freq:.2f} Hz", fg="green")
        except ValueError:
            self.status.config(text="Invalid frequency!", fg="red")

    def start_wave(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.generate_wave)
            self.thread.start()
            self.status.config(text="Wave generation started", fg="blue")

    def stop_wave(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
        GPIO.output(PIN, GPIO.LOW)
        self.status.config(text="Wave generation stopped", fg="black")

    def generate_wave(self):
        half_period = 1.0 / (2 * self.frequency)
        state = False
        next_toggle = time.perf_counter()

        while self.running:
            now = time.perf_counter()
            if now >= next_toggle:
                state = not state
                GPIO.output(PIN, state)
                next_toggle += half_period
            time.sleep(0.001)

    def on_close(self):
        self.stop_wave()
        GPIO.cleanup()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GPIOWaveGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
