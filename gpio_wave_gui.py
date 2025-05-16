import RPi.GPIO as GPIO
import time
import tkinter as tk

PIN = 18  # GPIO BCM 

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
        self.duty_cycle = 50  # 50% duty cycle
        self.pwm = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.OUT)
