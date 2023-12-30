import tkinter as tk
import pygame
import serial
import time
import threading

class XboxControllerReader:
    # ... (unchanged)

class ArduinoController:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino Controller")

        # Set the serial port and baud rate
        self.port = '/dev/ttyACM0'  # Replace 'COMx' with the actual serial port of your Arduino
        self.baud_rate = 9600

        # Open the serial port
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
        except serial.SerialException as e:
            print(f"Error: {e}")
            # Uncomment the next line if you want to exit the script when there is an error
            # self.root.destroy()
            return

        # Initialize the Xbox controller reader
        self.controller_reader = XboxControllerReader(self.ser)

        # Create a thread for reading Xbox controller input
        self.controller_thread = threading.Thread(target=self.controller_reader.start_reading)
        self.controller_thread.daemon = True  # Set the thread as a daemon so that it terminates when the main program finishes

        # Start the thread
        self.controller_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    controller = ArduinoController(root)
    if root._windowingsystem == 'win32':
        root.protocol("WM_DELETE_WINDOW", root.iconify)
    root.mainloop()
