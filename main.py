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
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.animation import Animation

# --- CONFIGURACIÓN DE TEMAS ---
THEMES = {
    "Matrix": {
        "bg": (0.02, 0.02, 0.02, 1),
        "key_bg": (0.05, 0.15, 0.05, 1),
        "key_color": (0, 1, 0.25, 1),
        "active": (0, 1, 0.25, 1),
        "txt_bg": (0.01, 0.05, 0.01, 1),
        "txt_color": (0, 1, 0.25, 1)
    },
    "Cyberpunk": {
        "bg": (0.02, 0.0, 0.08, 1),
        "key_bg": (0.1, 0.0, 0.25, 1),
        "key_color": (0, 0.9, 1, 1),
        "active": (1, 0, 0.6, 1),
        "txt_bg": (0.02, 0.0, 0.1, 1),
        "txt_color": (0, 0.9, 1, 1)
    },
    "Blood": {
        "bg": (0.05, 0.0, 0.0, 1),
        "key_bg": (0.2, 0.0, 0.0, 1),
        "key_color": (1, 0.1, 0.1, 1),
        "active": (1, 0.3, 0.3, 1),
        "txt_bg": (0.05, 0.0, 0.0, 1),
        "txt_color": (1, 0.2, 0.2, 1)
    }
}

KEYS_LAYOUT = [
    [("ESC",1), ("F1",1), ("F2",1), ("F3",1), ("F4",1), ("F5",1), ("F6",1), ("F7",1), ("F8",1), ("F9",1), ("F10",1), ("F11",1), ("F12",1)],
    [("1",1), ("2",1), ("3",1), ("4",1), ("5",1), ("6",1), ("7",1), ("8",1), ("9",1), ("0",1), ("-",1), ("=",1), ("⌫",2)],
    [("Q",1), ("W",1), ("E",1), ("R",1), ("T",1), ("Y",1), ("U",1), ("I",1), ("O",1), ("P",1), ("[",1), ("]",1)],
    [("A",1), ("S",1), ("D",1), ("F",1), ("G",1), ("H",1), ("J",1), ("K",1), ("L",1), (";",1), ("'",1), ("⏎",2)],
    [("⇧",1.5), ("Z",1), ("X",1), ("C",1), ("V",1), ("B",1), ("N",1), ("M",1), (",",1), (".",1), ("/",1), ("⇧",1.5)],
    [("CTRL",1.5), ("ALT",1), ("SPACE",6), ("COPY",1), ("CLEAR",1.5)]
]

SHIFT_MAP = {
    "1":"!","2":"@","3":"#","4":"$","5":"%","6":"^",
    "7":"&","8":"*","9":"(","0":")","-":"_","=":"+",
    "[":"{","]":"}","\\":"|",";":":","'":'"',",":"<",".":">","/":"?",
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

def vibrate():
    if HAS_VIBRATOR:
        try: Vibrator.vibrate(25)
        except: pass

# --- PANTALLA DE ARRANQUE (SPLASH SCREEN ANIMADA) ---
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        # Intentamos cargar tu imagen, si no está, usamos una por defecto
        try:
            self.logo = Image(
                source='assets/splash.png', 
                allow_stretch=True,
                size_hint=(0.5, 0.5), 
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
        except:
            self.logo = Image(
                source='data/logo/kivy-icon-512.png', 
                allow_stretch=True,
                size_hint=(0.5, 0.5), 
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            
        self.layout.add_widget(self.logo)
        
        self.label = Label(text="Cargando...", opacity=0, font_size='20sp', color=(0.5, 0.5, 0.5, 1))
        self.layout.add_widget(self.label)
        
        self.add_widget(self.layout)
        
    def on_enter(self):
        # Animación: Zoom -> Fade -> Cambio de pantalla
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
        
        self.root_layout = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(2))
        
        # 1. Barra Superior
        self.build_top_bar()
        
        # 2. Área de Texto
        self.display = TextInput(
            size_hint_y=0.3,
            background_color=THEMES[self.app.current_theme]['txt_bg'],
            foreground_color=THEMES[self.app.current_theme]['txt_color'],
            cursor_color=THEMES[self.app.current_theme]['txt_color'],
            font_name='RobotoMono',
            font_size=dp(18),
            multiline=True
        )
        self.root_layout.add_widget(self.display)

        # 3. Teclado
        self.keyboard_container = BoxLayout(orientation='vertical', spacing=dp(3))
        self.root_layout.add_widget(self.keyboard_container)
        
        self.build_keyboard()
        self.add_widget(self.root_layout)

    def build_top_bar(self):
        bar = BoxLayout(size_hint_y=0.06, spacing=dp(5))
        
        btn_settings = Button(text='⚙ AJUSTES', font_size=dp(12), background_color=(0.2,0.2,0.2,1))
        btn_settings.bind(on_press=self.open_settings)
        
        btn_copy = Button(text='📋 COPIAR', font_size=dp(12), background_color=(0.1,0.3,0.1,1))
        btn_copy.bind(on_press=self.copy_text)
        
        bar.add_widget(btn_settings)
        bar.add_widget(btn_copy)
        self.root_layout.add_widget(bar)

    def build_keyboard(self):
        self.keyboard_container.clear_widgets()
        self.keys_list = []

        for row_data in KEYS_LAYOUT:
            row_layout = BoxLayout(spacing=dp(3))
            for key_label, width_mult in row_data:
                btn = Button(
                    text=key_label,
                    font_size=dp(14),
                    background_normal='',
                    background_down='',
                    markup=True,
                    size_hint_x=width_mult
                )
                btn.apply_theme = lambda instance, t_name=self.app.current_theme: self._apply_btn_theme(instance, t_name)
                btn.apply_theme(btn)
                
                btn.bind(on_press=self.on_key_press)
                btn.bind(on_release=self.on_key_release)
                
                self.keys_list.append(btn)
                row_layout.add_widget(btn)
            self.keyboard_container.add_widget(row_layout)

    def _apply_btn_theme(self, instance, theme_name):
        t = THEMES[theme_name]
        instance.background_color = t['key_bg']
        instance.color = t['key_color']

    def on_key_press(self, instance):
        vibrate()
        t = THEMES[self.app.current_theme]
        instance.background_color = t['active']
        instance.color = (0,0,0,1)

        key = instance.text
        if key == "⇧":
            self.app.shift_active = not self.app.shift_active
            instance.background_color = (0, 0.5, 0.2, 1) if self.app.shift_active else t['key_bg']
            instance.color = (1,1,1,1)
            return
        if key == "CTRL": return

        if key == "⌫":
            self.display.text = self.display.text[:-1]
        elif key == "SPACE":
            self.display.text += " "
        elif key == "⏎":
            self.display.text += "\n"
        elif key == "COPY":
            self.copy_text(None)
        elif key == "CLEAR":
            self.display.text = ""
        elif key in SHIFT_MAP and self.app.shift_active:
            self.display.text += SHIFT_MAP[key]
            self.app.shift_active = False
        elif len(key) == 1:
            char = key.upper() if self.app.shift_active else key.lower()
            self.display.text += char
            self.app.shift_active = False

    def on_key_release(self, instance):
        t = THEMES[self.app.current_theme]
        if instance.text == "⇧" and self.app.shift_active: return
        instance.background_color = t['key_bg']
        instance.color = t['key_color']

    def copy_text(self, instance):
        Clipboard.copy(self.display.text)
        original_color = self.display.background_color
        self.display.background_color = (0, 0.5, 0, 1)
        Clock.schedule_once(lambda dt: setattr(self.display, 'background_color', original_color), 0.2)

    def open_settings(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text="Tamaño de Teclas", size_hint_y=0.1, color=(1,1,1,1)))
        slider = Slider(min=0.7, max=1.3, value=self.app.key_size, size_hint_y=0.1)
        content.add_widget(slider)
        
        content.add_widget(Label(text="Temas", size_hint_y=0.1, color=(1,1,1,1)))
        themes_btns = BoxLayout(size_hint_y=0.2, spacing=5)
        for name in THEMES:
            b = Button(text=name)
            b.bind(on_press=lambda x, n=name: self.change_theme(n))
            themes_btns.add_widget(b)
        content.add_widget(themes_btns)
        
        popup = Popup(title="Ajustes", content=content, size_hint=(0.85, 0.5))
        popup.open()
        slider.bind(value=lambda inst, val: self.change_size(val))
        
    def change_theme(self, name):
        self.app.current_theme = name
        Window.clearcolor = THEMES[name]['bg']
        t = THEMES[name]
        self.display.background_color = t['txt_bg']
        self.display.foreground_color = t['txt_color']
        self.display.cursor_color = t['txt_color']
        for key_btn in self.keys_list:
            key_btn.apply_theme(key_btn, name)
            
    def change_size(self, val):
        self.app.key_size = val
        for key_btn in self.keys_list:
            key_btn.font_size = dp(14) * val

# --- APP PRINCIPAL ---
class HackKeyboardApp(App):
    current_theme = StringProperty("Matrix")
    key_size = NumericProperty(1.0)
    shift_active = BooleanProperty(False)

    def build(self):
        Window.clearcolor = THEMES[self.current_theme]['bg']
        
        sm = ScreenManager(transition=FadeTransition(duration=0.5))
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(KeyboardScreen(name='keyboard'))
        
        return sm

if __name__ == '__main__':
    HackKeyboardApp().run()x
