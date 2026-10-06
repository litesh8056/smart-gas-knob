[app]

title = Smart Gas Knob Control System
package.name = smartgasknob
package.domain = org.smartgas

source.dir = .
source.main = main.py

version = 1.0

requirements = python3,kivy,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN

android.api = 35
android.minapi = 23

android.archs = arm64-v8a,armeabi-v7a

android.entrypoint = org.kivy.android.PythonActivity

p4a.optimize_python = 1

log_level = 2


[buildozer]

build_dir = .buildozer
bin_dir = bin
log_level = 2