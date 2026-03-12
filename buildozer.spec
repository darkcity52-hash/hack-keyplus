[app]
title = Hack Keyboard Pro
package.name = hackkeyboard
package.domain = org.darkcity52
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,otf,json
version = 1.0.0
requirements = python3,kivy,pyjnius,android
presplash.filename = %(source.dir)s/splash.png
icon.filename = %(source.dir)s/icon.png
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.enable_androidx = True
android.javac_version = 11

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
