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

        # Index of the LT button
        self.lt_button_index = 2  # Change this to the correct index for your controller

    def read_controller_input(self):
        pygame.event.pump()

        input_data = {}

        for i in range(self.controller.get_numaxes()):
            axis = f"Axis_{i}"
            value = round(self.controller.get_axis(i), 2)
            # Apply deadzone to joystick values
            input_data[axis] = self.apply_deadzone(value)

        buttons = [self.controller.get_button(i) for i in range(self.controller.get_numbuttons())]

        input_data['LT'] = buttons[self.lt_button_index]

        return input_data

    def apply_deadzone(self, value):
        # Apply deadzone to joystick values
        return 0.0 if abs(value) < self.deadzone else value

    def start_reading(self):
        while True:
            input_data = self.read_controller_input()

            # Send 'E' when LT button is pressed
            if input_data['LT']:
                self.ser.write('E'.encode())
            else:
                # Send WASD commands based on joystick values
                x_value = input_data['Axis_0']
                y_value = input_data['Axis_1']

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

            # Continue with the rest of your code...

            time.sleep(0.1)  # Adjust the sleep duration based on your requirements

class ArduinoController:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino Controller")

        # Set the serial port and baud rate
        self.port = '/dev/ttyACM0'  # Replace with the actual serial port of your Arduino
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
