from dbus import SystemBus, Interface
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
import subprocess
import argparse


# rotate screen using xrandr
def rotate_screen(screen, orientation):
    rotation = 'normal'
    if orientation == 'left-up':
        rotation = 'left'
    elif orientation == 'right-up':
        rotation = 'right'
    elif orientation == 'bottom-up':
        rotation = 'inverted'

    subprocess.call(["xrandr", "--output", screen, "--rotate", rotation])


def properties_changed_handler(interface, changed, invalidated):
    if 'AccelerometerOrientation' in changed:
        rotate_screen(args.screen, changed['AccelerometerOrientation'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rotates the screen using Xrandr and iio-sensors-proxy')
    parser.add_argument('screen', help='sets the screen that should be rotated')
    args = parser.parse_args()

    DBusGMainLoop(set_as_default=True)
    bus = SystemBus()
    sensorproxy = bus.get_object('net.hadess.SensorProxy', '/net/hadess/SensorProxy')
    hasaccelerometer = sensorproxy.Get('net.hadess.SensorProxy', 'HasAccelerometer',
                                       dbus_interface='org.freedesktop.DBus.Properties')
    if hasaccelerometer == 1:
        sensorproxyinterface = Interface(sensorproxy, 'net.hadess.SensorProxy')
        sensorproxyinterface.ClaimAccelerometer()

        bus.add_signal_receiver(handler_function=properties_changed_handler, signal_name='PropertiesChanged',
                                dbus_interface='org.freedesktop.DBus.Properties', bus_name='net.hadess.SensorProxy')

        loop = GLib.MainLoop()
        try:
            loop.run()
        except KeyboardInterrupt:
            sensorproxyinterface.ReleaseAccelerometer()
