import tkinter as tk
import pygame
import serial
import time

class XboxControllerReader:
    def __init__(self, ser):
        pygame.init()
        pygame.joystick.init()

        # Check if any joysticks are connected
        if pygame.joystick.get_count() == 0:
            raise Exception("No joystick found.")

        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        # Deadzone threshold
        self.deadzone = 0.1
        self.ser = ser

        # Map buttons to commands
        self.button_commands = {
            0: 'A',  # Example: Map button 0 (A button) to command 'A'
            # Add more button mappings as needed
        }

        # Track the state of the stop button
        self.stop_button_pressed = False

    def read_controller_input(self):
        pygame.event.pump()

        input_data = {}

        for i in range(self.controller.get_numaxes()):
            axis = f"Axis_{i}"
            value = round(self.controller.get_axis(i), 2)
            # Apply deadzone to joystick values
            input_data[axis] = self.apply_deadzone(value)

        for i in range(self.controller.get_numbuttons()):
            button = f"Button_{i}"
            value = self.controller.get_button(i)
            input_data[button] = value

        return input_data

    def apply_deadzone(self, value):
        # Apply deadzone to joystick values
        return 0.0 if abs(value) < self.deadzone else value

    def start_reading(self):
        while True:
            input_data = self.read_controller_input()

            # Check for stop button press and release
            if input_data.get('Button_0', 0) == 1:
                self.stop_button_pressed = True
            elif input_data.get('Button_0', 0) == 0:
                self.stop_button_pressed = False

            # Send stop command to Arduino only if the stop button is pressed
            if self.stop_button_pressed:
                self.send_stop_command()
            else:
                # Send joystick values to Arduino
                self.send_joystick_values(input_data['Axis_0'], input_data['Axis_1'])

            # Continue with the rest of your code...

            time.sleep(0.1)  # Adjust the sleep duration based on your requirements

    def send_stop_command(self):
        # Send stop command to Arduino
        self.ser.write('P'.encode())

    def send_joystick_values(self, x_value, y_value):
        # Convert joystick values to WASD control commands
        command = ''

        # Check the X and Y values to determine the movement command
        if abs(x_value) > self.deadzone or abs(y_value) > self.deadzone:
            if y_value < -self.deadzone:
                command = 'W'
            elif y_value > self.deadzone:
                command = 'S'

            if x_value < -self.deadzone:
                command += 'A'
            elif x_value > self.deadzone:
                command += 'D'

        # Send command to Arduino
        if command:
            self.ser.write(command.encode())

class ArduinoController:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino Controller")

        # Set the serial port and baud rate
        self.port = '/dev/ttyACM1'  # Replace 'COMx' with the actual serial port of your Arduino
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

        # Start reading Xbox controller input
        self.controller_reader.start_reading()

if __name__ == "__main__":
    root = tk.Tk()
    controller = ArduinoController(root)
    if root._windowingsystem == 'win32':
        root.protocol("WM_DELETE_WINDOW", root.iconify)
    root.mainloop()
