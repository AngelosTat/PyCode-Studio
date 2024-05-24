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
from kivy.uix.scrollview import ScrollView
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from threading import Thread
from kivy.clock import Clock
from kivy.config import Config
from plyer import notification
from io import StringIO
from os import path, makedirs
import sys

from PyPlex import UltraComplexScriptInterpreter

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

VERSION = "v2.0.0"

class CodeEditor(App):
    def build(self):
        self.notifications_enabled = False
        self.pyplex_interpreter = UltraComplexScriptInterpreter()
        self.icon = "logo.png"
        self.title = "PyPlex Studio " + VERSION
        action_bar = ActionBar()
        action_view = ActionView()
        action_previous = ActionPrevious(title="PyPlex Studio", with_previous=False, app_icon="logo.png")
        action_save = ActionButton(text="Save", on_press=self.save_file)
        action_new_tab = ActionButton(text="New Tab", on_press=self.create_new_tab)
        action_settings = ActionButton(text="Settings", on_press=self.open_settings_popup)
        action_view.add_widget(action_previous)
        action_view.add_widget(action_save)
        action_view.add_widget(action_new_tab)
        action_view.add_widget(action_settings)
        action_bar.add_widget(action_view)
        self.tabbed_panel = TabbedPanel(do_default_tab=False)
        self.create_new_tab()
        self.output_area = TextInput(readonly=True, multiline=True)
        output_scroll = ScrollView()
        output_scroll.add_widget(self.output_area)
        self.execute_button = Button(text="Execute", on_press=self.execute_code)
        self.input_area = TextInput(hint_text="User input", multiline=False)
        input_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
        input_layout.add_widget(Label(text="Input:"))
        input_layout.add_widget(self.input_area)
        input_layout.add_widget(self.execute_button)
        self.current_line_label = Label(text="Line: 1, Total Characters: 0", size_hint=(1, 0.1))
        self.file_destination_label = Label(text="Python file destination:")
        self.file_destination_input = TextInput(hint_text="Enter file path here", multiline=False)
        self.load_file_button = Button(text="Load File", on_press=self.load_file)
        file_layout = BoxLayout(orientation="vertical", size_hint=(0.25, 1))
        file_layout.add_widget(self.file_destination_label)
        file_layout.add_widget(self.file_destination_input)
        file_layout.add_widget(self.load_file_button)
        main_content_layout = BoxLayout(orientation="vertical")
        main_content_layout.add_widget(action_bar)
        main_content_layout.add_widget(self.tabbed_panel)
        main_content_layout.add_widget(self.current_line_label)
        main_content_layout.add_widget(input_layout)
        main_content_layout.add_widget(output_scroll)
        layout = BoxLayout(orientation="horizontal")
        layout.add_widget(file_layout)
        layout.add_widget(main_content_layout)
        self.input_area.bind(text=self.on_text)
        return layout

    def load_file(self, instance):
        file_path = self.file_destination_input.text
        try:
            with open(file_path, "r") as file:
                file_contents = file.read()
                file_name = path.basename(file_path)
                self.create_new_tab(file_name=file_name, file_content=file_contents)
        except FileNotFoundError:
            self.notify_error("File not found. Please check the file path.")
        except Exception as e:
            self.notify_error(f"An error occurred while loading the file: {str(e)}")

    def open_settings_popup(self, instance):
        popup_content = BoxLayout(orientation="vertical")
        close_button = Button(text="Close", on_press=self.close_settings_popup)
        switch = Switch(active=self.notifications_enabled)
        switch.bind(active=self.update_notifications_state)
        popup_content.add_widget(Label(text="Enable Notifications"))
        popup_content.add_widget(switch)
        popup_content.add_widget(close_button)
        window_width, window_height = Window.size
        popup_width = window_width / 1.25
        popup_height = window_height / 1.25
        self.settings_popup = Popup(title="Settings", content=popup_content, size_hint=(None, None), size=(popup_width, popup_height))
        self.settings_popup.open()

    def create_new_tab(self, instance=None, file_name="Untitled", file_content=""):
        tab = TabbedPanelItem(text=file_name)
        input_area = TextInput(multiline=True)
        input_area.text = file_content
        input_area.bind(text=self.on_text)
        code_scroll = ScrollView()
        code_scroll.add_widget(input_area)
        tab.content = code_scroll
        tab.input_area = input_area
        self.tabbed_panel.add_widget(tab)
        self.tabbed_panel.switch_to(tab)

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
        current_tab = self.tabbed_panel.current_tab
        code = current_tab.input_area.text
        user_input = self.input_area.text

        def execute():
            try:
                stdout = StringIO()
                sys.stdout = stdout
                sys.stdin = StringIO(user_input)
                self.pyplex_interpreter.interpret(code)
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
            if self.notifications_enabled:
                self.notify_error(output)
        else:
            self.output_area.foreground_color = (0, 0, 0, 1)
        self.output_area.text = output

    def save_file(self, instance):
        desktop_path = self.get_desktop_path()
        folder_path = path.join(desktop_path, "PyPlex Studio Projects")
        if not path.exists(folder_path):
            makedirs(folder_path)
        current_tab = self.tabbed_panel.current_tab
        file_name = current_tab.text
        if not file_name.endswith(".py"):
            file_name += ".py"
        file_path = path.join(folder_path, file_name)
        with open(file_path, "w") as file:
            file.write(current_tab.input_area.text)
        print(f"File saved at: {file_path}")

    def get_desktop_path(self):
        if platform == "win":
            return path.join(path.expanduser("~"), "Desktop")
        else:
            return path.expanduser("~")

    def notify_error(self, error_message):
        if platform == 'win':
            notification.notify(title='Error', message=error_message, app_name='PyPlex Studio')
        elif platform == 'linux':
            notification.notify(title='Error', message=error_message, app_name='PyPlex Studio')
        elif platform == 'macosx':
            notification.notify(title='Error', message=error_message, app_name='PyPlex Studio')

if __name__ == "__main__":
    CodeEditor().run()
