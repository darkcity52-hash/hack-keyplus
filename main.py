from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.clipboard import Clipboard
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.animation import Animation
from kivy.storage.jsonstore import JsonStore
from kivy.utils import get_color_from_hex
import os

# --- CONFIGURACIÓN DE TEMAS (mejorados) ---
THEMES = {
    "Matrix": {
        "bg": "#050f05",
        "key_bg": "#0a1f0a",
        "key_color": "#00ff40",
        "active": "#00ff40",
        "txt_bg": "#0a1f0a",
        "txt_color": "#00ff40",
        "suggestion_bg": "#0f2b0f"
    },
    "Cyberpunk": {
        "bg": "#0d0221",
        "key_bg": "#1e0b3c",
        "key_color": "#00f0ff",
        "active": "#ff00aa",
        "txt_bg": "#1a0b2e",
        "txt_color": "#00f0ff",
        "suggestion_bg": "#2a1452"
    },
    "Blood": {
        "bg": "#1a0000",
        "key_bg": "#330000",
        "key_color": "#ff4d4d",
        "active": "#ff9999",
        "txt_bg": "#2b0000",
        "txt_color": "#ff6666",
        "suggestion_bg": "#4d0000"
    }
}

# Diccionario simple (puedes ampliarlo)
DICCIONARIO = [
    "the", "and", "for", "you", "are", "hack", "code", "python",
    "kivy", "matrix", "cyber", "blood", "keyboard", "app", "android",
    "hola", "mundo", "programacion", "teclado", "oneplus"
]

# Layouts del teclado
KEYS_LAYOUT = [
    [("ESC",1), ("F1",1), ("F2",1), ("F3",1), ("F4",1), ("F5",1), ("F6",1), ("F7",1), ("F8",1), ("F9",1), ("F10",1), ("F11",1), ("F12",1)],
    [("1",1), ("2",1), ("3",1), ("4",1), ("5",1), ("6",1), ("7",1), ("8",1), ("9",1), ("0",1), ("-",1), ("=",1), ("⌫",2)],
    [("Q",1), ("W",1), ("E",1), ("R",1), ("T",1), ("Y",1), ("U",1), ("I",1), ("O",1), ("P",1), ("[",1), ("]",1), ("\\",1)],
    [("A",1), ("S",1), ("D",1), ("F",1), ("G",1), ("H",1), ("J",1), ("K",1), ("L",1), (";",1), ("'",1), ("⏎",2)],
    [("⇧",1.5), ("Z",1), ("X",1), ("C",1), ("V",1), ("B",1), ("N",1), ("M",1), (",",1), (".",1), ("/",1), ("⇧",1.5)],
    [("CTRL",1.2), ("ALT",1), ("123",1.2), ("SPACE",4), ("COPY",1), ("PASTE",1), ("CLEAR",1.2)]
]

SYMBOLS_LAYOUT = [
    [("`",1), ("~",1), ("!",1), ("@",1), ("#",1), ("$",1), ("%",1), ("^",1), ("&",1), ("*",1), ("(",1), (")",1), ("⌫",2)],
    [("-",1), ("_",1), ("=",1), ("+",1), ("[",1), ("]",1), ("{",1), ("}",1), ("\\",1), ("|",1), (";",1), (":",1)],
    [("'",1), ('"',1), (",",1), ("<",1), (".",1), (">",1), ("/",1), ("?",1), ("·",1), ("€",1), ("£",1), ("¥",1)],
    [("⇧",1.5), ("ABC",3), ("SPACE",5), ("COPY",1), ("PASTE",1), ("⌫",1.5)]
]

SHIFT_MAP = {
    "1":"!","2":"@","3":"#","4":"$","5":"%","6":"^","7":"&","8":"*","9":"(","0":")",
    "-":"_","=":"+","[":"{","]":"}","\\":"|",";":":","'":'"',",":"<",".":">","/":"?",
    "`":"~","€":"£","·":"•"
}

# --- VIBRACIÓN ANDROID ---
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Vibrator = PythonActivity.mActivity.getSystemService(Context.VIBRATOR_SERVICE)
    HAS_VIBRATOR = True
except:
    HAS_VIBRATOR = False

def vibrate(enable=True):
    if HAS_VIBRATOR and enable:
        try:
            Vibrator.vibrate(25)
        except:
            pass

# --- PANTALLA DE ARRANQUE (SPLASH) ---
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        splash_path = os.path.join('assets', 'splash.png')
        if os.path.exists(splash_path):
            self.logo = Image(source=splash_path, allow_stretch=True, size_hint=(0.5, 0.5), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        else:
            self.logo = Label(text="HACK KEYBOARD", font_size=dp(40), color=(0,1,0,1))
        
        self.layout.add_widget(self.logo)
        self.label = Label(text="Cargando...", opacity=0, font_size=dp(20), color=(0.5,0.5,0.5,1))
        self.layout.add_widget(self.label)
        self.add_widget(self.layout)
        
    def on_enter(self):
        anim_zoom = Animation(size_hint=(1.2, 1.2), duration=1.5, t='out_expo')
        anim_fade = Animation(opacity=0, duration=0.8)
        anim_zoom.bind(on_complete=lambda *args: anim_fade.start(self.logo))
        anim_fade.bind(on_complete=self.go_to_keyboard)
        anim_zoom.start(self.logo)
        Animation(opacity=1, duration=0.5).start(self.label)

    def go_to_keyboard(self, *args):
        self.manager.current = 'keyboard'

# --- PANTALLA DEL TECLADO ---
class KeyboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.current_layout = 'main'  # 'main' o 'symbols'
        self.caps_lock = False
        self.last_shift_time = 0
        self.clipboard_history = []
        
        # Cargar configuración guardada
        self.app.load_settings()
        
        # Layout principal
        self.root_layout = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(2))
        
        # Barra superior
        self.build_top_bar()
        
        # Área de texto
        self.display = TextInput(
            size_hint_y=0.3,
            background_color=get_color_from_hex(THEMES[self.app.current_theme]['txt_bg']),
            foreground_color=get_color_from_hex(THEMES[self.app.current_theme]['txt_color']),
            cursor_color=get_color_from_hex(THEMES[self.app.current_theme]['txt_color']),
            font_name='RobotoMono',
            font_size=dp(18),
            multiline=True
        )
        self.root_layout.add_widget(self.display)
        
        # Banda de sugerencias
        self.suggestions_box = BoxLayout(size_hint_y=0.07, spacing=dp(5))
        self.suggestion_buttons = []
        for i in range(3):
            btn = Button(
                text='', 
                background_color=(0.2,0.2,0.2,0.8),
                color=(1,1,1,1),
                font_size=dp(12)
            )
            btn.bind(on_press=self.use_suggestion)
            self.suggestion_buttons.append(btn)
            self.suggestions_box.add_widget(btn)
        self.root_layout.add_widget(self.suggestions_box)
        
        # Teclado
        self.keyboard_container = BoxLayout(orientation='vertical', spacing=dp(3))
        self.root_layout.add_widget(self.keyboard_container)
        
        self.build_keyboard(self.current_layout)
        
        # Bind para actualizar sugerencias al cambiar texto
        self.display.bind(text=self.update_suggestions)
        
        self.add_widget(self.root_layout)

    def build_top_bar(self):
        bar = BoxLayout(size_hint_y=0.06, spacing=dp(5))
        btn_settings = Button(text='⚙ AJUSTES', font_size=dp(12), background_color=(0.2,0.2,0.2,1))
        btn_settings.bind(on_press=self.open_settings)
        btn_clip = Button(text='📋 HISTORIAL', font_size=dp(12), background_color=(0.1,0.3,0.1,1))
        btn_clip.bind(on_press=self.show_clipboard_history)
        bar.add_widget(btn_settings)
        bar.add_widget(btn_clip)
        self.root_layout.add_widget(bar)

    def build_keyboard(self, layout_type='main'):
        self.keyboard_container.clear_widgets()
        self.keys_list = []
        
        layout = KEYS_LAYOUT if layout_type == 'main' else SYMBOLS_LAYOUT
        
        for row_data in layout:
            row_layout = BoxLayout(spacing=dp(3))
            for key_label, width_mult in row_data:
                btn = Button(
                    text=key_label,
                    font_size=dp(14) * self.app.key_size,
                    background_normal='',
                    background_down='',
                    markup=True,
                    size_hint_x=width_mult,
                    on_press=self.on_key_press,
                    on_release=self.on_key_release
                )
                self._apply_btn_theme(btn, self.app.current_theme)
                self.keys_list.append(btn)
                row_layout.add_widget(btn)
            self.keyboard_container.add_widget(row_layout)

    def _apply_btn_theme(self, instance, theme_name):
        t = THEMES[theme_name]
        instance.background_color = get_color_from_hex(t['key_bg'])
        instance.color = get_color_from_hex(t['key_color'])
        # Efecto de relieve
        instance.background_normal = ''
        instance.background_down = ''
        instance.border = (2,2,2,2)

    def on_key_press(self, instance):
        vibrate(self.app.vibration_enabled)
        t = THEMES[self.app.current_theme]
        instance.background_color = get_color_from_hex(t['active'])
        instance.color = (0,0,0,1)
        
        key = instance.text
        if key == "⇧":
            self.handle_shift()
            return
        if key == "123":
            self.switch_layout('symbols')
            return
        if key == "ABC":
            self.switch_layout('main')
            return
        if key == "CTRL":
            return
        if key == "COPY":
            self.copy_to_clipboard()
            return
        if key == "PASTE":
            self.paste_from_clipboard()
            return
        
        # Procesar teclas normales
        if key == "⌫":
            self.display.text = self.display.text[:-1]
        elif key == "SPACE":
            self.display.text += " "
        elif key == "⏎":
            self.display.text += "\n"
        elif key == "CLEAR":
            self.display.text = ""
        elif key in SHIFT_MAP and (self.app.shift_active or self.caps_lock):
            self.display.text += SHIFT_MAP[key]
            if not self.caps_lock:
                self.app.shift_active = False
        elif len(key) == 1:
            char = key.upper() if (self.app.shift_active or self.caps_lock) else key.lower()
            self.display.text += char
            if not self.caps_lock:
                self.app.shift_active = False

    def on_key_release(self, instance):
        t = THEMES[self.app.current_theme]
        if instance.text == "⇧" and (self.app.shift_active or self.caps_lock):
            # Mantener color especial si shift activo o caps lock
            instance.background_color = (0,0.5,0.2,1) if self.app.shift_active else get_color_from_hex(t['key_bg'])
        else:
            instance.background_color = get_color_from_hex(t['key_bg'])
        instance.color = get_color_from_hex(t['key_color'])

    def handle_shift(self):
        import time
        now = time.time()
        if now - self.last_shift_time < 0.3:  # Doble toque
            self.caps_lock = not self.caps_lock
            self.app.shift_active = self.caps_lock
            self.last_shift_time = 0
        else:
            self.app.shift_active = not self.app.shift_active
            self.last_shift_time = now

    def switch_layout(self, layout):
        self.current_layout = layout
        self.build_keyboard(layout)

    def copy_to_clipboard(self):
        text = self.display.text
        if text:
            Clipboard.copy(text)
            self.clipboard_history.insert(0, text)
            if len(self.clipboard_history) > 5:
                self.clipboard_history.pop()
            self.show_temp_message("Copiado")

    def paste_from_clipboard(self):
        text = Clipboard.paste()
        if text:
            self.display.text += text

    def show_clipboard_history(self, instance):
        if not self.clipboard_history:
            self.show_temp_message("Historial vacío")
            return
        content = BoxLayout(orientation='vertical', spacing=dp(5))
        for item in self.clipboard_history:
            btn = Button(text=item[:20] + "..." if len(item) > 20 else item, size_hint_y=None, height=dp(40))
            btn.bind(on_press=lambda x, t=item: self.paste_history(t))
            content.add_widget(btn)
        popup = Popup(title="Historial", content=content, size_hint=(0.9, 0.6))
        popup.open()

    def paste_history(self, text):
        self.display.text += text

    def show_temp_message(self, msg):
        original_color = self.display.background_color
        self.display.background_color = (0,0.5,0,1)
        self.display.hint_text = msg
        Clock.schedule_once(lambda dt: self.restore_display(original_color), 0.5)

    def restore_display(self, original_color):
        self.display.background_color = original_color
        self.display.hint_text = ''

    def update_suggestions(self, instance, value):
        # Obtener última palabra
        words = value.split()
        if not words:
            self.clear_suggestions()
            return
        last_word = words[-1]
        if not last_word:
            self.clear_suggestions()
            return
        
        # Buscar coincidencias
        matches = [w for w in DICCIONARIO if w.startswith(last_word.lower()) and w != last_word.lower()]
        matches = matches[:3]
        
        for i, btn in enumerate(self.suggestion_buttons):
            if i < len(matches):
                btn.text = matches[i]
                btn.opacity = 1
            else:
                btn.text = ''
                btn.opacity = 0

    def clear_suggestions(self):
        for btn in self.suggestion_buttons:
            btn.text = ''
            btn.opacity = 0

    def use_suggestion(self, instance):
        if instance.text:
            words = self.display.text.split()
            if words:
                words[-1] = instance.text
                self.display.text = ' '.join(words) + ' '
            else:
                self.display.text += instance.text + ' '
            self.clear_suggestions()

    def open_settings(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Tamaño teclas
        content.add_widget(Label(text="Tamaño de Teclas", size_hint_y=0.1, color=(1,1,1,1)))
        slider = Slider(min=0.7, max=1.5, value=self.app.key_size, size_hint_y=0.1)
        slider.bind(value=lambda inst, val: self.change_size(val))
        content.add_widget(slider)
        
        # Temas
        content.add_widget(Label(text="Tema", size_hint_y=0.1, color=(1,1,1,1)))
        themes_btns = BoxLayout(size_hint_y=0.15, spacing=5)
        for name in THEMES:
            b = Button(text=name)
            b.bind(on_press=lambda x, n=name: self.change_theme(n))
            themes_btns.add_widget(b)
        content.add_widget(themes_btns)
        
        # Vibración
        vib_box = BoxLayout(size_hint_y=0.1)
        vib_label = Label(text="Vibración:", color=(1,1,1,1))
        vib_btn = Button(text="ON" if self.app.vibration_enabled else "OFF")
        vib_btn.bind(on_press=self.toggle_vibration)
        vib_box.add_widget(vib_label)
        vib_box.add_widget(vib_btn)
        content.add_widget(vib_box)
        
        popup = Popup(title="Ajustes", content=content, size_hint=(0.9, 0.6))
        popup.open()

    def toggle_vibration(self, instance):
        self.app.vibration_enabled = not self.app.vibration_enabled
        instance.text = "ON" if self.app.vibration_enabled else "OFF"
        self.app.save_settings()

    def change_theme(self, name):
        self.app.current_theme = name
        self.apply_theme()
        self.app.save_settings()

    def change_size(self, val):
        self.app.key_size = val
        for btn in self.keys_list:
            btn.font_size = dp(14) * val
        self.app.save_settings()

    def apply_theme(self):
        t = THEMES[self.app.current_theme]
        bg = get_color_from_hex(t['bg'])
        Window.clearcolor = bg
        self.display.background_color = get_color_from_hex(t['txt_bg'])
        self.display.foreground_color = get_color_from_hex(t['txt_color'])
        self.display.cursor_color = get_color_from_hex(t['txt_color'])
        for btn in self.keys_list:
            self._apply_btn_theme(btn, self.app.current_theme)

# --- APP PRINCIPAL ---
class HackKeyboardApp(App):
    current_theme = StringProperty("Matrix")
    key_size = NumericProperty(1.0)
    shift_active = BooleanProperty(False)
    vibration_enabled = BooleanProperty(True)
    
    def build(self):
        # Cargar configuración al iniciar
        self.store = JsonStore('settings.json')
        self.load_settings()
        
        Window.clearcolor = get_color_from_hex(THEMES[self.current_theme]['bg'])
        
        sm = ScreenManager(transition=FadeTransition(duration=0.5))
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(KeyboardScreen(name='keyboard'))
        
        return sm

    def load_settings(self):
        if self.store.exists('settings'):
            data = self.store.get('settings')
            self.current_theme = data.get('theme', 'Matrix')
            self.key_size = data.get('key_size', 1.0)
            self.vibration_enabled = data.get('vibration', True)

    def save_settings(self):
        self.store.put('settings', 
                       theme=self.current_theme, 
                       key_size=self.key_size,
                       vibration=self.vibration_enabled)

if __name__ == '__main__':
    HackKeyboardApp().run()
