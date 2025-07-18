import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import time
import os
from datetime import datetime

class PulseGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Arduino Pulse Generator")
        master.attributes('-fullscreen', True)

        self.pulse_width_ms = 1000
        self.unit = 'ms'
        self.current_input = ""
        self.serial_port = None

        self.font_main = ("Consolas", 16, "bold")
        self.font_button = ("Consolas", 20, "bold")
        self.font_status = ("Consolas", 14, "bold")

        self.status = tk.Label(master, text="Ready", fg="blue", font=self.font_status)
        self.status.grid(row=0, column=0, columnspan=4, pady=10, sticky="w")

        self.exit_button = tk.Button(master, text="Exit", font=("Consolas", 14, "bold"),
                                     command=self.on_close, bg="#d9534f", fg="white")
        self.exit_button.grid(row=0, column=4, padx=10, pady=10, sticky="ne")

        display_frame = tk.Frame(master)
        display_frame.grid(row=1, column=0, columnspan=5, padx=20, pady=10, sticky="ew")
        display_frame.columnconfigure(0, weight=3)
        display_frame.columnconfigure(1, weight=1)
        display_frame.columnconfigure(2, weight=2)
        display_frame.columnconfigure(3, weight=3)

        self.display = tk.Entry(display_frame, font=self.font_button, justify='right')
        self.display.grid(row=0, column=0, sticky="ew")
        self.update_display()

        self.unit_label = tk.Label(display_frame, text='ms', font=self.font_main)
        self.unit_label.grid(row=0, column=1, sticky="w")

        tk.Label(display_frame, text="Serial Port:", font=self.font_main).grid(row=0, column=2, sticky="e")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(display_frame, textvariable=self.port_var, state="readonly")
        self.port_combo.grid(row=0, column=3, sticky="ew")
        self.port_combo.bind("<<ComboboxSelected>>", self.connect_serial)
        self.port_combo.option_add("*TCombobox*Listbox.font", "Consolas 14")

        self.button_frame = tk.Frame(master)
        self.button_frame.grid(row=2, column=0, columnspan=5, padx=20, pady=10, sticky="nsew")
        self.create_keypad()

        action_frame = tk.Frame(master)
        action_frame.grid(row=3, column=0, columnspan=5, pady=20, sticky="ew")
        tk.Button(action_frame, text="Apply", font=self.font_main, command=self.apply_input).grid(row=0, column=0, padx=10, sticky="ew")
        tk.Button(action_frame, text="Start", font=self.font_main, command=self.send_pulse).grid(row=0, column=1, padx=10, sticky="ew")
        tk.Button(action_frame, text="Shutdown Pi", font=self.font_main, command=self.shutdown_pi).grid(row=0, column=2, padx=10, sticky="ew")
        tk.Button(action_frame, text="ON", font=self.font_main, bg="green", command=self.send_on).grid(row=0, column=3, padx=10, sticky="ew")
        tk.Button(action_frame, text="OFF", font=self.font_main, bg="red", command=self.send_off).grid(row=0, column=4, padx=10, sticky="ew")
        self.onoff_state = tk.StringVar(value="Current: OFF")
        tk.Label(action_frame, textvariable=self.onoff_state, font=self.font_main).grid(row=1, column=0, columnspan=5, pady=10)

        for i in range(5):
            master.columnconfigure(i, weight=1)
        for i in range(4):
            master.rowconfigure(i, weight=1)

        all_ports = self.get_serial_ports()
        self.port_combo['values'] = [p[0] for p in all_ports]
        self.port_var.set("")
        self.try_auto_connect()

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [(port.device, port.description) for port in ports]

    def try_auto_connect(self):
        ports = self.get_serial_ports()
        for device, desc in ports:
            if "Arduino" in desc or "ttyACM" in device or "ttyUSB" in device:
                try:
                    self.port_var.set(device)
                    self.connect_serial(port=device)
                    return
                except:
                    continue
        self.status.config(text="Auto-connect failed. Please select manually.", fg="orange")

    def connect_serial(self, event=None, port=None): # Arduino와 USB 연결, command를 보내는 용도 (ON/OFF, 특정 시간 동안 ON)
        if event:
            port = self.port_var.get()
        try:
            self.serial_port = serial.Serial(port, 9600, timeout=2)
            time.sleep(2)
            self.status.config(text=f"Connected to {port}", fg="green")
        except serial.SerialException as e:
            self.status.config(text=f"Connection failed: {e}", fg="red")

    def create_keypad(self):
        keys = [['7', '8', '9'],
                ['4', '5', '6'],
                ['1', '2', '3'],
                ['0', 'CLR', 'MS/S']]

        for r, row in enumerate(keys):
            for c, key in enumerate(row):
                btn = tk.Button(self.button_frame, text=key, font=self.font_button,
                                command=lambda k=key: self.key_press(k))
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

        for i in range(4):
            self.button_frame.rowconfigure(i, weight=1)
        for i in range(3):
            self.button_frame.columnconfigure(i, weight=1)

    def key_press(self, key):
        if key == 'CLR':
            self.current_input = ""
        elif key == 'MS/S':
            self.unit = 's' if self.unit == 'ms' else 'ms'
            self.unit_label.config(text=self.unit)
        else:
            self.current_input += key
        self.update_display()

    def update_display(self):
        self.display.delete(0, tk.END)
        self.display.insert(0, self.current_input)

    def apply_input(self):
        try:
            val = int(self.current_input)
            self.pulse_width_ms = val * 1000 if self.unit == 's' else val # 사용자가 s를 선택해도 ms로 변환하여 전송
            self.status.config(text=f"Pulse set to {self.pulse_width_ms} ms", fg="green")
        except ValueError:
            self.status.config(text="Invalid input!", fg="red")

    def send_pulse(self): # USB로 연결된 Arduino에 문자열 전송(예: pulse_1000ms)
        if not self.serial_port or not self.serial_port.is_open:
            self.status.config(text="Serial not connected", fg="red")
            return

        if self.onoff_state.get() == "Current: ON":
            self.status.config(text="Pulse blocked: Currently ON", fg="orange")
            return

        try:
            now = datetime.now().strftime("%H:%M:%S")
            command = f"pulse_{self.pulse_width_ms}ms\n"
            self.serial_port.write(command.encode())
            self.status.config(text=f"Pulse sent at {now} for {self.pulse_width_ms} ms", fg="blue")
        except Exception as e:
            self.status.config(text=f"Send failed: {e}", fg="red")

    def send_on(self): # USB로 연결된 Arduino에 ON 문자열 전송 - 계속해서 LED ON
        if not self.serial_port or not self.serial_port.is_open:
            self.status.config(text="Serial not connected", fg="red")
            return
        try:
            self.serial_port.write(b'on\n')
            self.status.config(text="ON command sent", fg="blue")
            self.onoff_state.set("Current: ON")
        except Exception as e:
            self.status.config(text=f"Send failed: {e}", fg="red")

    def send_off(self): # USB로 연결된 Arduino에 OFF 문자열 전송 - LED OFF
        if not self.serial_port or not self.serial_port.is_open:
            self.status.config(text="Serial not connected", fg="red")
            return
        try:
            self.serial_port.write(b'off\n')
            self.status.config(text="OFF command sent", fg="blue")
            self.onoff_state.set("Current: OFF")
        except Exception as e:
            self.status.config(text=f"Send failed: {e}", fg="red")

    def shutdown_pi(self):
        self.cleanup()
        os.system("sudo shutdown now")

    def cleanup(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def on_close(self):
        self.cleanup()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PulseGeneratorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
