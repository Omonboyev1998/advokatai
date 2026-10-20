[app]

# (str) Title of your application
title = Advokat AI

# (str) Package name
package.name = advokatai

# (str) Package domain (needed for android/ios packaging)
package.domain = uz.advokat

# (str) Source code where the application main.py lives
source.dir = mobile

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,txt

# (list) List of directory to exclude
source.exclude_dirs = tests, bin, venv, build, dist, reports, .git, __pycache__

# (str) Application versioning
version = 5.7.0

# (list) Application requirements
requirements = python3,kivy==2.3.0,requests,urllib3,certifi

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (str) Icon of the application
icon.filename = %(source.dir)s/face.png

# (str) Presplash of the application
presplash.filename = %(source.dir)s/face.png

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
