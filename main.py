from kivy.utils import platform
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserListView
from threading import Thread
from kivy.clock import Clock
from plyer import notification
from io import StringIO
from os import path, makedirs
import sys

VERSION = "v1.2.0"

class CodeEditor(App):
    def build(self):
        self.notifications_enabled = False
        self.icon = "logo.png"
        self.title = "PyCode Studio " + VERSION
        self.text_input = TextInput(multiline=True)
        self.output_area = TextInput(readonly=True, multiline=True)
        self.execute_button = Button(text="Execute", on_press=self.execute_code)
        self.save_button = Button(text="Save", on_press=self.save_file)
        self.title_button = Label(text="Your Custom Layout Here")
        self.settings_button = Button(text="Settings", on_press=self.open_settings_popup)
        self.input_area = TextInput(readonly=False, multiline=False)
        self.current_line_label = Label(text="Line: 1, Total Characters: 0", size_hint=(1, 0.1))
        self.file_destination_label = Label(text="Python file destination:")
        self.file_destination_input = TextInput(hint_text="Enter file path here", multiline=False)
        self.load_file_button = Button(text="Load File", on_press=self.load_file)
        top_bar_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
        top_bar_layout.add_widget(self.save_button)
        top_bar_layout.add_widget(self.title_button)
        top_bar_layout.add_widget(self.settings_button)
        input_area_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
        input_area_layout.add_widget(Label(text="Input:"))
        input_area_layout.add_widget(self.input_area)
        input_area_layout.add_widget(self.execute_button)
        top_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
        top_layout.add_widget(Label(text="PyCode Studio"))
        main_content_layout = BoxLayout(orientation="vertical")
        main_content_layout.add_widget(top_layout)
        main_content_layout.add_widget(top_bar_layout)
        main_content_layout.add_widget(self.text_input)
        main_content_layout.add_widget(self.current_line_label)
        main_content_layout.add_widget(input_area_layout)
        main_content_layout.add_widget(self.output_area)
        left_side_layout = BoxLayout(orientation="vertical", size_hint=(0.25, 1))
        left_side_layout = BoxLayout(orientation="vertical", size_hint=(0.25, 1))
        left_side_layout.add_widget(Label())
        file_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.4))
        file_layout.add_widget(self.file_destination_label)
        file_layout.add_widget(self.file_destination_input)
        file_layout.add_widget(self.load_file_button)
        left_side_layout.add_widget(file_layout)
        layout = BoxLayout(orientation="horizontal")
        layout.add_widget(left_side_layout)
        layout.add_widget(main_content_layout)
        self.text_input.bind(text=self.on_text)
        return layout

    def load_file(self, instance):
        file_path = self.file_destination_input.text
        try:
            with open(file_path, "r") as file:
                file_contents = file.read()
                self.text_input.text = file_contents
        except FileNotFoundError:
            print("File not found. Please check the file path.")

    def open_settings_popup(self, instance):
        popup_content = BoxLayout(orientation="vertical")
        close_button = Button(text="Close", on_press=self.close_settings_popup)
        switch = Switch(active=self.notifications_enabled)
        switch.bind(active=self.update_notifications_state)
        popup_content.add_widget(Label(text="Settings"))
        popup_content.add_widget(switch)
        popup_content.add_widget(close_button)
        window_width, window_height = Window.size
        popup_width = window_width / 1.25
        popup_height = window_height / 1.25
        self.settings_popup = Popup(title="Settings", content=popup_content, size_hint=(None, None), size=(popup_width, popup_height))
        self.settings_popup.open()

    def update_notifications_state(self, instance, active):
        self.notifications_enabled = active

    def close_settings_popup(self, instance):
        self.settings_popup.dismiss()

    def on_text(self, instance, value):
        cursor_pos = instance.cursor_index()
        line_num = instance.text[:cursor_pos].count("\n") + 1
        total_chars = len(instance.text)
        self.current_line_label.text = f"Line: {line_num}, Total Characters: {total_chars}"

    def execute_code(self, instance):
        code = self.text_input.text
        user_input = self.input_area.text

        def execute():
            try:
                stdout = StringIO()
                sys.stdout = stdout
                sys.stdin = StringIO(user_input)
                exec(code)
                output = stdout.getvalue()
                Clock.schedule_once(lambda dt: self.update_output(output))
            except Exception as e:
                error_message = "Error: " + str(e)
                Clock.schedule_once(lambda dt: self.update_output(error_message))
                self.notify_error(error_message)
            finally:
                sys.stdout = sys.__stdout__
        Thread(target=execute).start()

    def update_output(self, output):
        if output.startswith("Error:"):
            self.output_area.foreground_color = (1, 0, 0, 1)
        else:
            self.output_area.foreground_color = (0, 0, 0, 1)
        self.output_area.text = output

    def save_file(self, instance):
        desktop_path = self.get_desktop_path()
        folder_path = path.join(desktop_path, "PyCode Studio Projects")
        if not path.exists(folder_path):
            makedirs(folder_path)
        file_path = path.join(folder_path, "main.py")
        with open(file_path, "w") as file:
            file.write(self.text_input.text)
        print(f"File saved at: {file_path}")

    def get_desktop_path(self):
        if platform == "win":
            return path.join(path.expanduser("~"), "Desktop")
        else:
            return path.expanduser("~")

    def notify_error(self, error_message):
        if self.notifications_enabled:
            if platform == 'win':
                notification.notify(
                    title='Error',
                    message=error_message,
                    app_name='Katastro5 Python Editor'
                )
            elif platform == 'linux':
                notification.notify(
                    title='Error',
                    message=error_message,
                    app_name='Katastro5 Python Editor'
                )
            elif platform == 'macosx':
                notification.notify(
                    title='Error',
                    message=error_message,
                    app_name='Katastro5 Python Editor'
                )

if __name__ == "__main__":
    CodeEditor().run()
