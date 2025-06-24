import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

Gst.init(None)

class RTSPServer:
    def __init__(self):
        self.server = GstRtspServer.RTSPServer()
        self.factory = GstRtspServer.RTSPMediaFactory()

        # Define GStreamer pipeline to read from /dev/video0 and encode to H264
        self.factory.set_launch(
            '( v4l2src device=/dev/video0 ! videoconvert ! video/x-raw,format=I420 '
            '! x264enc speed-preset=ultrafast tune=zerolatency bitrate=500 '
            '! rtph264pay name=pay0 pt=96 )'
        )
        self.factory.set_shared(True)
        self.server.get_mount_points().add_factory("/test", self.factory)

        self.server.attach(None)
        print("RTSP Server is live at rtsp://<your-pi-ip>:8554/test")

if __name__ == '__main__':
    server = RTSPServer()
    loop = GObject.MainLoop()
    loop.run()
