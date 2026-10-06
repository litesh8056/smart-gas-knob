import math
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget


# ==========================================================
# ANDROID BLUETOOTH
# ==========================================================

try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission

    ANDROID_AVAILABLE = True

except Exception:
    ANDROID_AVAILABLE = False


# ==========================================================
# REGULATOR
# ==========================================================

class Regulator(Widget):

    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.touching = False

        self.bind(
            pos=self.redraw,
            size=self.redraw,
            angle=self.redraw
        )

    # ======================================================
    # DRAW
    # ======================================================

    def redraw(self, *args):

        self.canvas.clear()

        cx = self.center_x
        cy = self.center_y

        radius = min(self.width, self.height) * 0.38

        with self.canvas:

            # Shadow
            Color(0.75, 0.77, 0.80, 1)

            Ellipse(
                pos=(
                    cx - radius - dp(6),
                    cy - radius - dp(6)
                ),
                size=(
                    2 * radius + dp(12),
                    2 * radius + dp(12)
                )
            )

            # Outer regulator
            Color(0.94, 0.95, 0.96, 1)

            Ellipse(
                pos=(
                    cx - radius,
                    cy - radius
                ),
                size=(
                    2 * radius,
                    2 * radius
                )
            )

            Color(0.78, 0.81, 0.85, 1)

            Line(
                circle=(
                    cx,
                    cy,
                    radius
                ),
                width=dp(2)
            )

            # Scale ring
            scale_radius = radius * 0.89

            Color(0.88, 0.89, 0.91, 1)

            Ellipse(
                pos=(
                    cx - scale_radius,
                    cy - scale_radius
                ),
                size=(
                    2 * scale_radius,
                    2 * scale_radius
                )
            )

            # Tick marks
            for a in range(0, 181, 5):

                theta = math.radians(a)

                if a % 30 == 0:
                    r1 = radius * 0.84
                    r2 = radius * 0.70
                    width = dp(4)

                elif a % 10 == 0:
                    r1 = radius * 0.84
                    r2 = radius * 0.75
                    width = dp(2.5)

                else:
                    r1 = radius * 0.84
                    r2 = radius * 0.79
                    width = dp(1.5)

                x1 = cx + r1 * math.cos(theta)
                y1 = cy + r1 * math.sin(theta)

                x2 = cx + r2 * math.cos(theta)
                y2 = cy + r2 * math.sin(theta)

                Color(0.30, 0.32, 0.35, 1)

                Line(
                    points=[
                        x1,
                        y1,
                        x2,
                        y2
                    ],
                    width=width
                )

            # Main knob
            knob_radius = radius * 0.63

            Color(0.46, 0.48, 0.51, 1)

            Ellipse(
                pos=(
                    cx - knob_radius,
                    cy - knob_radius
                ),
                size=(
                    2 * knob_radius,
                    2 * knob_radius
                )
            )

            Color(0.33, 0.35, 0.38, 1)

            Line(
                circle=(
                    cx,
                    cy,
                    knob_radius
                ),
                width=dp(2)
            )

            # Inner knob
            inner_radius = knob_radius * 0.84

            Color(0.52, 0.54, 0.57, 1)

            Ellipse(
                pos=(
                    cx - inner_radius,
                    cy - inner_radius
                ),
                size=(
                    2 * inner_radius,
                    2 * inner_radius
                )
            )

            # Indicator
            theta = math.radians(self.angle)

            indicator_length = knob_radius * 0.76

            ix = (
                cx
                + indicator_length * math.cos(theta)
            )

            iy = (
                cy
                + indicator_length * math.sin(theta)
            )

            Color(0.97, 0.98, 0.99, 1)

            Line(
                points=[
                    cx,
                    cy,
                    ix,
                    iy
                ],
                width=dp(6)
            )

            Ellipse(
                pos=(
                    ix - dp(5),
                    iy - dp(5)
                ),
                size=(
                    dp(10),
                    dp(10)
                )
            )

            # Center
            Color(0.43, 0.45, 0.47, 1)

            Ellipse(
                pos=(
                    cx - dp(30),
                    cy - dp(30)
                ),
                size=(
                    dp(60),
                    dp(60)
                )
            )

            Color(0.50, 0.52, 0.54, 1)

            Ellipse(
                pos=(
                    cx - dp(22),
                    cy - dp(22)
                ),
                size=(
                    dp(44),
                    dp(44)
                )
            )

    # ======================================================
    # CALCULATE ANGLE
    # ======================================================

    def calculate_angle(self, x, y):

        dx = x - self.center_x
        dy = y - self.center_y

        distance = math.sqrt(
            dx * dx + dy * dy
        )

        if distance < dp(40):
            return self.angle

        # Only upper semicircle
        if y < self.center_y:
            return self.angle

        angle = math.degrees(
            math.atan2(dy, dx)
        )

        if angle < 0:
            return self.angle

        if angle > 180:
            return self.angle

        return max(
            0,
            min(
                180,
                int(round(angle))
            )
        )

    # ======================================================
    # TOUCH DOWN
    # ======================================================

    def on_touch_down(self, touch):

        if self.collide_point(
            touch.x,
            touch.y
        ):

            self.touching = True

            self.angle = self.calculate_angle(
                touch.x,
                touch.y
            )

            return True

        return super().on_touch_down(touch)

    # ======================================================
    # TOUCH MOVE
    # ======================================================

    def on_touch_move(self, touch):

        if self.touching:

            self.angle = self.calculate_angle(
                touch.x,
                touch.y
            )

            return True

        return super().on_touch_move(touch)

    # ======================================================
    # TOUCH UP
    # ======================================================

    def on_touch_up(self, touch):

        if self.touching:

            self.touching = False

            app = App.get_running_app()

            app.send_angle(
                self.angle
            )

            return True

        return super().on_touch_up(touch)


# ==========================================================
# MAIN APP
# ==========================================================

class SmartGasKnobApp(App):

    def build(self):

        self.title = "Smart Gas Knob Control System"

        self.bluetooth_socket = None
        self.connected_device = None
        self.last_sent_angle = None

        # --------------------------------------------------
        # ROOT
        # --------------------------------------------------

        root = BoxLayout(
            orientation="vertical",
            padding=[
                dp(18),
                dp(10)
            ],
            spacing=dp(4)
        )

        # --------------------------------------------------
        # TOP BLUE LINE
        # --------------------------------------------------

        top_line = Widget(
            size_hint_y=None,
            height=dp(5)
        )

        with top_line.canvas:

            Color(
                0.145,
                0.388,
                0.922,
                1
            )

            Rectangle(
                pos=(
                    0,
                    0
                ),
                size=(
                    dp(600),
                    dp(5)
                )
            )

        root.add_widget(
            top_line
        )

        # --------------------------------------------------
        # BADGE
        # --------------------------------------------------

        badge = Label(
            text="ANALOG REGULATOR",
            font_size=dp(12),
            bold=True,
            color=(
                0.16,
                0.46,
                0.85,
                1
            ),
            size_hint_y=None,
            height=dp(35)
        )

        root.add_widget(badge)

        # --------------------------------------------------
        # TITLE
        # --------------------------------------------------

        title = Label(
            text="Gas Stove Level",
            font_size=dp(25),
            bold=True,
            color=(
                0.09,
                0.13,
                0.20,
                1
            ),
            size_hint_y=None,
            height=dp(45)
        )

        root.add_widget(title)

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        self.status_label = Label(
            text="○  STOVE STANDBY",
            font_size=dp(15),
            color=(
                0.54,
                0.58,
                0.64,
                1
            ),
            size_hint_y=None,
            height=dp(35)
        )

        root.add_widget(
            self.status_label
        )

        # --------------------------------------------------
        # ANGLE
        # --------------------------------------------------

        self.angle_label = Label(
            text="0°",
            font_size=dp(23),
            bold=True,
            color=(
                0.09,
                0.13,
                0.20,
                1
            ),
            size_hint_y=None,
            height=dp(40)
        )

        root.add_widget(
            self.angle_label
        )

        # --------------------------------------------------
        # REGULATOR
        # --------------------------------------------------

        self.regulator = Regulator(
            size_hint_y=1
        )

        self.regulator.bind(
            angle=self.angle_changed
        )

        root.add_widget(
            self.regulator
        )

        # --------------------------------------------------
        # SCALE
        # --------------------------------------------------

        scale = Label(
            text="0°       30°       60°       90°       120°       150°       180°",
            font_size=dp(11),
            color=(
                0.25,
                0.27,
                0.30,
                1
            ),
            size_hint_y=None,
            height=dp(25)
        )

        root.add_widget(scale)

        # --------------------------------------------------
        # BLUETOOTH STATUS
        # --------------------------------------------------

        self.bluetooth_status = Label(
            text="Bluetooth: Disconnected",
            font_size=dp(14),
            color=(
                0.40,
                0.43,
                0.48,
                1
            ),
            size_hint_y=None,
            height=dp(35)
        )

        root.add_widget(
            self.bluetooth_status
        )

        # --------------------------------------------------
        # CONNECT BUTTON
        # --------------------------------------------------

        self.connect_button = Button(
            text="Connect to HC-05",
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(55),
            background_normal="",
            background_color=(
                0.145,
                0.388,
                0.922,
                1
            )
        )

        self.connect_button.bind(
            on_release=self.connect_hc05
        )

        root.add_widget(
            self.connect_button
        )

        # Android permission
        if ANDROID_AVAILABLE:
            self.request_bluetooth_permissions()

        return root

    # ======================================================
    # ANGLE CHANGED
    # ======================================================

    def angle_changed(
        self,
        instance,
        value
    ):

        angle = int(value)

        self.angle_label.text = (
            f"{angle}°"
        )

        if angle == 0:

            self.status_label.text = (
                "○  STOVE STANDBY"
            )

            self.status_label.color = (
                0.54,
                0.58,
                0.64,
                1
            )

        else:

            self.status_label.text = (
                f"●  LEVEL {angle}°"
            )

            self.status_label.color = (
                0.145,
                0.388,
                0.922,
                1
            )

    # ======================================================
    # PERMISSIONS
    # ======================================================

    def request_bluetooth_permissions(self):

        try:

            permissions = []

            if hasattr(
                Permission,
                "BLUETOOTH_CONNECT"
            ):
                permissions.append(
                    Permission.BLUETOOTH_CONNECT
                )

            if hasattr(
                Permission,
                "BLUETOOTH_SCAN"
            ):
                permissions.append(
                    Permission.BLUETOOTH_SCAN
                )

            if permissions:

                request_permissions(
                    permissions
                )

        except Exception as error:

            print(
                "Permission error:",
                error
            )

    # ======================================================
    # CONNECT HC-05
    # ======================================================

    def connect_hc05(self, *args):

        if not ANDROID_AVAILABLE:

            self.bluetooth_status.text = (
                "Bluetooth works on Android APK"
            )

            return

        self.bluetooth_status.text = (
            "Bluetooth: Connecting..."
        )

        self.connect_button.text = (
            "Connecting..."
        )

        threading.Thread(
            target=self.bluetooth_worker,
            daemon=True
        ).start()

    # ======================================================
    # BLUETOOTH WORKER
    # ======================================================

    def bluetooth_worker(self):

        try:

            BluetoothAdapter = autoclass(
                "android.bluetooth.BluetoothAdapter"
            )

            UUID = autoclass(
                "java.util.UUID"
            )

            adapter = (
                BluetoothAdapter.getDefaultAdapter()
            )

            if adapter is None:

                self.update_connection_status(
                    "Bluetooth not available",
                    False
                )

                return

            if not adapter.isEnabled():

                self.update_connection_status(
                    "Turn Bluetooth ON",
                    False
                )

                return

            paired_devices = (
                adapter.getBondedDevices()
            )

            device = None

            iterator = (
                paired_devices.iterator()
            )

            while iterator.hasNext():

                current_device = (
                    iterator.next()
                )

                name = (
                    current_device.getName()
                )

                if name:

                    name = str(name)

                    if (
                        "HC-05"
                        in name.upper()
                        or
                        "HC05"
                        in name.upper()
                    ):

                        device = (
                            current_device
                        )

                        break

            if device is None:

                self.update_connection_status(
                    "HC-05 not paired",
                    False
                )

                return

            # HC-05 SPP UUID
            uuid = UUID.fromString(
                "00001101-0000-1000-8000-00805F9B34FB"
            )

            socket = (
                device
                .createRfcommSocketToServiceRecord(
                    uuid
                )
            )

            socket.connect()

            self.bluetooth_socket = socket
            self.connected_device = device

            self.update_connection_status(
                "Connected to HC-05",
                True
            )

        except Exception as error:

            print(
                "Bluetooth error:",
                error
            )

            self.bluetooth_socket = None

            self.connected_device = None

            self.update_connection_status(
                "Connection failed",
                False
            )

    # ======================================================
    # UPDATE BLUETOOTH STATUS
    # ======================================================

    def update_connection_status(
        self,
        text,
        connected
    ):

        def update(dt):

            self.bluetooth_status.text = (
                "Bluetooth: " + text
            )

            if connected:

                self.bluetooth_status.color = (
                    0.08,
                    0.50,
                    0.20,
                    1
                )

                self.connect_button.text = (
                    "✓  HC-05 Connected"
                )

                self.connect_button.background_color = (
                    0.08,
                    0.65,
                    0.25,
                    1
                )

            else:

                self.bluetooth_status.color = (
                    0.75,
                    0.15,
                    0.15,
                    1
                )

                self.connect_button.text = (
                    "Connect to HC-05"
                )

                self.connect_button.background_color = (
                    0.145,
                    0.388,
                    0.922,
                    1
                )

        Clock.schedule_once(
            update
        )

    # ======================================================
    # SEND ANGLE
    # ======================================================

    def send_angle(self, angle):

        angle = int(angle)

        if angle < 0 or angle > 180:
            return

        if angle == self.last_sent_angle:
            return

        if self.bluetooth_socket is None:
            return

        threading.Thread(
            target=self.send_bluetooth,
            args=(angle,),
            daemon=True
        ).start()

    # ======================================================
    # SEND BLUETOOTH
    # ======================================================

    def send_bluetooth(self, angle):

        try:

            data = f"{angle}\n"

            output_stream = (
                self.bluetooth_socket
                .getOutputStream()
            )

            output_stream.write(
                data.encode("ascii")
            )

            output_stream.flush()

            self.last_sent_angle = angle

            print(
                "Sent:",
                angle
            )

        except Exception as error:

            print(
                "Send error:",
                error
            )

            self.bluetooth_socket = None

            self.connected_device = None

            self.update_connection_status(
                "Disconnected",
                False
            )

    # ======================================================
    # CLOSE
    # ======================================================

    def on_stop(self):

        try:

            if self.bluetooth_socket:

                self.bluetooth_socket.close()

        except Exception:
            pass


# ==========================================================
# START
# ==========================================================

if __name__ == "__main__":

    SmartGasKnobApp().run()
    
