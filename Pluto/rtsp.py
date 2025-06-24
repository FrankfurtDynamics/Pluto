import cv2

# USB webcam device (usually 0)
camera_index = 0

# GStreamer pipeline to stream over RTSP via UDP to a local port
# You can change host=0.0.0.0 to a specific IP if needed
gst_str = (
    'appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast '
    '! rtph264pay config-interval=1 pt=96 ! udpsink host=224.1.1.1 port=5000 auto-multicast=true'
)

# Open the webcam
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Start GStreamer pipeline as output
out = cv2.VideoWriter(
    gst_str,
    cv2.CAP_GSTREAMER,
    0,  # FourCC not needed for GStreamer
    30.0,  # Frame rate
    (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
)

if not out.isOpened():
    print("Error: Could not open output stream.")
    exit()

print("Streaming... Press CTRL+C to stop.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        out.write(frame)

except KeyboardInterrupt:
    print("Streaming stopped.")

finally:
    cap.release()
    out.release()
    cv2.destroyAllWindows()
