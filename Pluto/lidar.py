from pyrplidar import PyRPlidar
import threading
import time

LIDAR_PORT = '/dev/ttyUSB0'
LIDAR_BAUDRATE = 115200

_latest_scan = []       # list of (quality, angle, distance_mm)
_scan_lock = threading.Lock()
_lidar = None
_thread = None


def get_scan():
    """Return a copy of the most recent full scan."""
    with _scan_lock:
        return list(_latest_scan)


def _scan_loop():
    global _latest_scan
    # Retry start_scan in case the motor hasn't fully spun up yet
    scan_generator = None
    for attempt in range(5):
        try:
            scan_generator = _lidar.start_scan()
            break
        except Exception as e:
            print(f"[LIDAR] start_scan attempt {attempt + 1} failed: {e}, retrying...")
            time.sleep(1)
    if scan_generator is None:
        print("[LIDAR] Failed to start scan after 5 attempts.")
        return
    current = []
    count = 0
    for measurement in scan_generator():
        count += 1
        if measurement.quality > 0 and measurement.distance > 0:
            current.append((measurement.quality, measurement.angle, measurement.distance))
        if len(current) >= 360:
            with _scan_lock:
                _latest_scan = current
            current = []


def start():
    global _lidar, _thread
    _lidar = PyRPlidar()
    _lidar.connect(port=LIDAR_PORT, baudrate=LIDAR_BAUDRATE, timeout=3)
    if _lidar.lidar_serial._serial is None:
        raise RuntimeError(f"[LIDAR] Failed to open serial port {LIDAR_PORT} — check permissions (sudo usermod -aG dialout $USER)")
    # Reset to clear any stale state / sync mismatch
    try:
        _lidar.stop()
        _lidar.reset()
    except Exception:
        pass
    time.sleep(1)
    info = _lidar.get_info()
    health = _lidar.get_health()
    print(f"[LIDAR] Info: {info}")
    print(f"[LIDAR] Health: {health}")
    _lidar.set_motor_pwm(660)  # 660 is default PWM for A1
    time.sleep(2)  # let motor spin up
    _thread = threading.Thread(target=_scan_loop, daemon=True)
    _thread.start()
    print(f"[LIDAR] Scanning on {LIDAR_PORT}")


def stop():
    if _lidar:
        _lidar.stop()
        _lidar.set_motor_pwm(0)
        _lidar.disconnect()
        print("[LIDAR] Stopped.")


if __name__ == '__main__':
    start()
    try:
        while True:
            scan = get_scan()
            if scan:
                closest = min(scan, key=lambda x: x[2])
                print(f"[LIDAR] Closest: {closest[2]:.0f} mm @ {closest[1]:.1f}°  ({len(scan)} points)")
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop()
