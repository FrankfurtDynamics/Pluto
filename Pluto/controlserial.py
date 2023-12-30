import pygame
import json
import time

class XboxControllerReader:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        # Check if any joysticks are connected
        if pygame.joystick.get_count() == 0:
            raise Exception("No joystick found.")

        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

    def read_controller_input(self):
        pygame.event.pump()

        input_data = {}

        for i in range(self.controller.get_numaxes()):
            axis = f"Axis_{i}"
            value = round(self.controller.get_axis(i), 2)
            input_data[axis] = value

        return input_data

    def print_input(self):
        input_data = self.read_controller_input()
        print(json.dumps(input_data, indent=4))

    def start_reading(self):
        while True:
            self.print_input()
            time.sleep(0.1)  # Adjust the sleep duration based on your requirements

if __name__ == "__main__":
    try:
        controller_reader = XboxControllerReader()
        controller_reader.start_reading()
    except Exception as e:
        print(f"Error: {e}")
