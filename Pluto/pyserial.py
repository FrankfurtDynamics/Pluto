import tkinter as tk
import serial

class ArduinoController:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino Controller")

        # Set the serial port and baud rate
        self.port = '/dev/ttyUSB0'  # Replace 'COMx' with the actual serial port of your Arduino
        self.baud_rate = 9600

        # Create a label to display the messages
        self.message_label = tk.Label(self.root, text="Messages: ")
        self.message_label.pack()

        # Initialize the dictionary to track button states
        self.button_states = {'W': False, 'A': False, 'S': False, 'D': False}

        # Open the serial port
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
        except serial.SerialException as e:
            print(f"Error: {e}")
            # Uncomment the next line if you want to exit the script when there is an error
            # self.root.destroy()
            return

        # Dictionary to track the currently pressed key
        self.current_key = None

        # Register key events
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        # Stop button
        self.stop_button = tk.Button(self.root, text="Stop Motors", command=self.stop_motors)
        self.stop_button.pack()

        # Periodically update the label with current messages
        self.root.after(100, self.update_message_label)

    def key_press(self, event):
        key = event.char.upper()
        if key in self.button_states and not self.button_states[key]:
            self.button_states[key] = True
            self.send_signal(key)

    def key_release(self, event):
        key = event.char.upper()
        if key in self.button_states and self.button_states[key]:
            self.button_states[key] = False
            self.send_signal('STOP')

    def send_signal(self, command):
        self.ser.write(command.encode())

    def update_message_label(self):
        current_messages = [cmd for cmd, state in self.button_states.items() if state]
        self.message_label.config(text=f"Messages: {', '.join(current_messages)}")
        self.root.after(100, self.update_message_label)

    def stop_motors(self):
        self.button_states = {'W': False, 'A': False, 'S': False, 'D': False}
        self.send_signal('STOP')

if __name__ == "__main__":
    root = tk.Tk()
    controller = ArduinoController(root)
    if root._windowingsystem == 'win32':
        root.protocol("WM_DELETE_WINDOW", root.iconify)
    root.mainloop()
