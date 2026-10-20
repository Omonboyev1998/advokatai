# [app]
title = Advokat AI
package.name = advokatai
package.domain = uz.advokat
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,db,docx
source.exclude_dirs = tests, bin, venv, build, dist, reports, .git

version = 5.7.0

# (list) Application requirements
requirements = python3,kivy==2.3.0,requests,urllib3,certifi

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33
android.minapi = 24
android.ndk = 25b

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme
android.manifest.theme = @android:style/Theme.DeviceDefault.Light.NoActionBar

[buildozer]
log_level = 2
warn_on_root = 1
