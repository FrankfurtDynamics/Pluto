from rplidar import RPLidar
import threading

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
    try:
        for scan in _lidar.iter_scans():
            with _scan_lock:
                _latest_scan = [(q, a, d) for q, a, d in scan if q > 0]
    except Exception as e:
        print(f"[LIDAR] Scan loop error: {e}")


def start():
    global _lidar, _thread
    _lidar = RPLidar(LIDAR_PORT, baudrate=LIDAR_BAUDRATE)
    info = _lidar.get_info()
    health = _lidar.get_health()
    print(f"[LIDAR] Info: {info}")
    print(f"[LIDAR] Health: {health}")
    _thread = threading.Thread(target=_scan_loop, daemon=True)
    _thread.start()
    print(f"[LIDAR] Scanning on {LIDAR_PORT}")


def stop():
    if _lidar:
        _lidar.stop()
        _lidar.stop_motor()
        _lidar.disconnect()
        print("[LIDAR] Stopped.")


if __name__ == '__main__':
    import time
    start()
    try:
        while True:
            scan = get_scan()
            if scan:
                # Print the closest object
                closest = min(scan, key=lambda x: x[2])
                print(f"[LIDAR] Closest: {closest[2]:.0f} mm @ {closest[1]:.1f}°  ({len(scan)} points)")
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop()
