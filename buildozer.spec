[app]
title = Hack Keyboard Pro
package.name = hackkeyboard
package.domain = org.darkcity52
source.dir = .
source.include_exts = py,png,jpg,kv
version = 1.0
requirements = python3,kivy,pyjnius
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

# CRUCIAL: Solo compilar para 64 bits para evitar fallos de memoria en GitHub
android.archs = arm64-v8a

# Permisos
android.permissions = VIBRATE

# Iconos y Splash (Asegúrate de que las imágenes estén en la carpeta assets)
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/splash.png

[buildozer]
log_level = 2
warn_on_root = 1
