import cv2

camera_index = 0

gst_str = (
    'appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast '
    '! rtph264pay config-interval=1 pt=96 ! udpsink host=224.1.1.1 port=5000 auto-multicast=true'
)

print("[DEBUG] Opening webcam...")
cap = cv2.VideoCapture('/dev/video0')

if not cap.isOpened():
    print("[ERROR] Could not open webcam.")import cv2

# Use device path for the webcam
device_path = '/dev/video0'

# Replace with the IP address of the VLC machine
vlc_ip = '192.168.178.89'  

gst_str = (
    'appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast '
    '! rtph264pay config-interval=1 pt=96 ! udpsink host={} port=5000'.format(vlc_ip)
)

print("[DEBUG] Opening webcam...")
cap = cv2.VideoCapture(device_path)

if not cap.isOpened():
    print("[ERROR] Could not open webcam.")
    exit(1)
else:
    print("[DEBUG] Webcam opened successfully.")

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
fps = fps if fps > 0 else 30

print(f"[DEBUG] Frame width: {frame_width}, Frame height: {frame_height}, FPS: {fps}")

print("[DEBUG] Initializing GStreamer VideoWriter...")
out = cv2.VideoWriter(
    gst_str,
    cv2.CAP_GSTREAMER,
    0,
    fps,
    (frame_width, frame_height)
)

if not out.isOpened():
    print("[ERROR] Could not open video writer.")
    cap.release()
    exit(1)
else:
    print("[DEBUG] Video writer opened successfully. Streaming started.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        out.write(frame)
        print("[DEBUG] Frame written to stream.")

except KeyboardInterrupt:
    print("\n[INFO] Streaming stopped by user.")

finally:
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("[DEBUG] Released all resources. Exiting.")

    exit(1)
else:
    print("[DEBUG] Webcam opened successfully.")

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
fps = fps if fps > 0 else 30  # fallback to 30 if FPS is 0 or invalid

print(f"[DEBUG] Frame width: {frame_width}, Frame height: {frame_height}, FPS: {fps}")

print("[DEBUG] Initializing GStreamer VideoWriter...")
out = cv2.VideoWriter(
    gst_str,
    cv2.CAP_GSTREAMER,
    0,
    fps,
    (frame_width, frame_height)
)

if not out.isOpened():
    print("[ERROR] Could not open video writer.")
    cap.release()
    exit(1)
else:
    print("[DEBUG] Video writer opened successfully. Streaming started.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        out.write(frame)
        print("[DEBUG] Frame written to stream.")

except KeyboardInterrupt:
    print("\n[INFO] Streaming stopped by user.")

finally:
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("[DEBUG] Released all resources. Exiting.")
