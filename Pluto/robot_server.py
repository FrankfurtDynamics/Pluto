import pygame
import serial
import time
import threading
import asyncio
import websockets
import json
import http.server
import socketserver
import os
import subprocess
import socket

# ─── Shared serial lock ──────────────────────────────────────────────────────
serial_lock = threading.Lock()


# ─── Xbox Controller ─────────────────────────────────────────────────────────
class XboxControllerReader:
    def __init__(self, ser):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            raise Exception("No joystick found.")

        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        self.deadzone = 0.1
        self.ser = ser
        self.stop_button_pressed = False

    def read_controller_input(self):
        pygame.event.pump()
        input_data = {}
        for i in range(self.controller.get_numaxes()):
            value = round(self.controller.get_axis(i), 2)
            input_data[f"Axis_{i}"] = self.apply_deadzone(value)
        for i in range(self.controller.get_numbuttons()):
            input_data[f"Button_{i}"] = self.controller.get_button(i)
        return input_data

    def apply_deadzone(self, value):
        return 0.0 if abs(value) < self.deadzone else value

    def start_reading(self):
        while True:
            input_data = self.read_controller_input()

            if input_data.get('Button_0', 0) == 1:
                self.stop_button_pressed = True
            elif input_data.get('Button_0', 0) == 0:
                self.stop_button_pressed = False

            if self.stop_button_pressed:
                send_command(self.ser, 'P')
            else:
                x = input_data['Axis_0']
                y = input_data['Axis_1']
                cmd = joystick_to_command(x, y, self.deadzone)
                if cmd:
                    send_command(self.ser, cmd)

            time.sleep(0.1)


# ─── Shared helpers ───────────────────────────────────────────────────────────
def joystick_to_command(x_value, y_value, deadzone=0.1):
    command = ''
    if abs(x_value) > deadzone or abs(y_value) > deadzone:
        if y_value < -deadzone:
            command = 'W'
        elif y_value > deadzone:
            command = 'S'
        if x_value < -deadzone:
            command += 'A'
        elif x_value > deadzone:
            command += 'D'
    return command


def send_command(ser, command):
    """Thread-safe serial write. V commands include a trailing newline."""
    with serial_lock:
        try:
            payload = command + ('\n' if command.startswith('V') else '')
            ser.write(payload.encode())
            print(f"[CMD] {command}")
        except serial.SerialException as e:
            print(f"[ERR] Serial write failed: {e}")


# ─── MJPEG Camera Stream ─────────────────────────────────────────────────────
class MjpegHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence access logs

    def do_GET(self):
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            cmd = [
                'libcamera-vid',
                '-t', '0',
                '--codec', 'mjpeg',
                '--width', '640',
                '--height', '480',
                '--framerate', '15',
                '-o', '-',
                '--nopreview',
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            buf = b''
            try:
                while True:
                    chunk = proc.stdout.read(4096)
                    if not chunk:
                        break
                    buf += chunk
                    # find complete JPEG frames
                    while True:
                        start = buf.find(b'\xff\xd8')
                        end = buf.find(b'\xff\xd9')
                        if start == -1 or end == -1 or end < start:
                            break
                        frame = buf[start:end + 2]
                        buf = buf[end + 2:]
                        try:
                            self.wfile.write(
                                b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\r\n' +
                                frame + b'\r\n'
                            )
                            self.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError):
                            break
            finally:
                proc.terminate()
        else:
            self.send_error(404)


def run_camera_server(port=8090):
    server = socketserver.ThreadingTCPServer(('', port), MjpegHandler)
    server.daemon_threads = True
    print(f"[CAM] MJPEG stream at http://0.0.0.0:{port}/stream")
    server.serve_forever()


# ─── WebSocket Server ─────────────────────────────────────────────────────────
connected_clients = set()

async def ws_handler(websocket):
    connected_clients.add(websocket)
    print(f"[WS] Client connected: {websocket.remote_address}")
    try:
        async for raw in websocket:
            try:
                msg = json.loads(raw)
                cmd = msg.get('command', '')
                upper = cmd.upper()
                # Movement commands
                if upper in ('W', 'A', 'S', 'D', 'WA', 'WD', 'SA', 'SD', 'P', ''):
                    if upper:
                        send_command(ser_global, upper)
                    await websocket.send(json.dumps({'ack': upper}))
                # Lights toggle: L
                elif upper == 'L':
                    send_command(ser_global, 'L')
                    await websocket.send(json.dumps({'ack': 'L'}))
                # Speed: V0–V255
                elif upper.startswith('T') and upper[1:].isdigit():
                    speed = max(0, min(255, int(upper[1:])))
                    send_command(ser_global, f'V{speed}')
                    await websocket.send(json.dumps({'ack': f'V{speed}'}))
                else:
                    await websocket.send(json.dumps({'error': 'Unknown command'}))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({'error': 'Invalid JSON'}))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        print(f"[WS] Client disconnected")


async def start_ws_server(host='0.0.0.0', port=8765):
    async with websockets.serve(ws_handler, host, port):
        print(f"[WS] WebSocket server listening on ws://{host}:{port}")
        await asyncio.Future()  # run forever


def run_ws_in_thread():
    asyncio.run(start_ws_server())


# ─── Static HTTP Server (serves index.html) ───────────────────────────────────
def run_http_server(port=8080):
    webconfig_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webconfig")
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args, directory=webconfig_dir, **kwargs
    )
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"[HTTP] Serving UI at http://0.0.0.0:{port}")
        httpd.serve_forever()


# ─── Main ─────────────────────────────────────────────────────────────────────
ser_global = None

class ArduinoController:
    def __init__(self):
        global ser_global
        self.port = '/dev/ttyACM0'
        self.baud_rate = 9600

        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            ser_global = self.ser
        except serial.SerialException as e:
            print(f"[ERR] Could not open serial port: {e}")
            return

        # Xbox controller thread (optional — catches joystick not found)
        try:
            self.controller_reader = XboxControllerReader(self.ser)
            self.controller_thread = threading.Thread(
                target=self.controller_reader.start_reading, daemon=True)
            self.controller_thread.start()
            print("[CTRL] Xbox controller thread started.")
        except Exception as e:
            print(f"[WARN] Xbox controller unavailable: {e}")

        # WebSocket thread
        ws_thread = threading.Thread(target=run_ws_in_thread, daemon=True)
        ws_thread.start()

        # Camera stream thread
        cam_thread = threading.Thread(target=lambda: run_camera_server(8090), daemon=True)
        cam_thread.start()

        # HTTP thread
        http_thread = threading.Thread(target=lambda: run_http_server(8080), daemon=True)
        http_thread.start()


if __name__ == "__main__":
    controller = ArduinoController()
    print("[MAIN] Robot server running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[MAIN] Exiting...")
