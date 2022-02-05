import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from pathlib import Path
from widgets import ScrollFrame, ConnectionFrame
from MQTT_manager import PROTOCOL_LOOKUP, SSL_LIST
import uuid
from functools import  partial

MQTT_VERSION_LIST = list(PROTOCOL_LOOKUP.keys())


def validate_int(d, i, P, s, S, v, V, W):
    try:
        int(S)
    except Exception:
        return False
    return True


def validate_name(name, name_list):
    if name not in name_list:
        return name

    template = name + " {}"
    index = 1
    while template.format(index) in name_list:
        index += 1
    return template.format(index)


class ConfigurationWindow(tk.Toplevel):
    def __init__(self, master=None, config_handler=None, config_update_callback=None):
        super().__init__(master=master)
        self.master = master
        self.config_handler = config_handler
        self.currently_selected_connection = None
        self.currently_selected_connection_dict = {}
        self.config_update_callback = config_update_callback

        self.title("Connection configuration")
        width = 1000
        height = 600
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(alignstr)

        self.protocol("WM_DELETE_WINDOW", self.on_destroy)
        vcmd = (self.register(validate_int),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # Connections frame
        self.connections_frame = ttk.Frame(self, relief="sunken")
        self.connections_frame.pack(side=tk.LEFT, anchor="w", fill="y", padx=3, pady=3)
        self.connections_listbox = ScrollFrame(self.connections_frame)
        self.connections_listbox.pack(fill='both', padx=3, pady=3, expand=1)
        self.add_connection_button = ttk.Button(self.connections_frame)
        self.add_connection_button["text"] = "Add"
        self.add_connection_button.pack(padx=3, pady=3, side="right")
        self.add_connection_button["command"] = self.new_connection
        self.remove_connection_button = ttk.Button(self.connections_frame)
        self.remove_connection_button["text"] = "Remove"
        self.remove_connection_button["command"] = self.on_remove
        self.remove_connection_button.pack(padx=3, pady=3, side="right")

        # Connection configuration frame
        self.connection_configuration_frame = ttk.Frame(self, relief="groove", borderwidth=2)
        self.connection_configuration_frame.pack(side=tk.RIGHT, fill="both", pady=3, padx=3, expand=1)

        # Profile name
        self.profile_name_frame = ttk.Frame(self.connection_configuration_frame)
        self.profile_name_frame.pack(fill="x")
        self.profile_label = ttk.Label(self.profile_name_frame, width=20)
        self.profile_label["anchor"] = "e"
        self.profile_label["text"] = "Profile name"
        self.profile_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.profile_name_input = ttk.Entry(self.profile_name_frame)
        self.profile_name_input.pack(side=tk.LEFT, padx=2)

        # Broker address
        self.broker_address_frame = ttk.Frame(self.connection_configuration_frame)
        self.broker_address_frame.pack(fill="x")
        self.broker_label = ttk.Label(self.broker_address_frame, width=20)
        self.broker_label["anchor"] = "e"
        self.broker_label["text"] = "Broker address"
        self.broker_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.broker_address_input = ttk.Entry(self.broker_address_frame, background="white")
        self.broker_address_input.pack(side=tk.LEFT, padx=2)

        # Broker port
        self.broker_port_frame = ttk.Frame(self.connection_configuration_frame)
        self.broker_port_frame.pack(fill="x")
        self.broker_port_label = ttk.Label(self.broker_port_frame, width=20)
        self.broker_port_label["anchor"] = "e"
        self.broker_port_label["text"] = "Broker port"
        self.broker_port_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.broker_port_name_input = ttk.Entry(self.broker_port_frame)
        self.broker_port_name_input.configure(validate="all", validatecommand=vcmd)
        self.broker_port_name_input.pack(side=tk.LEFT, padx=2)

        # Client ID
        self.client_id_frame = ttk.Frame(self.connection_configuration_frame)
        self.client_id_frame.pack(fill="x")
        self.client_id_label = ttk.Label(self.client_id_frame, width=20)
        self.client_id_label["anchor"] = "e"
        self.client_id_label["text"] = "Client ID"
        self.client_id_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.client_id_input = ttk.Entry(self.client_id_frame)
        self.client_id_input.pack(side=tk.LEFT, padx=2)
        self.client_id_generate_button = ttk.Button(self.client_id_frame)
        self.client_id_generate_button["text"] = "Generate client ID"
        self.client_id_generate_button["command"] = self.on_generate_client_id
        self.client_id_generate_button.pack(side=tk.LEFT, padx=2, pady=2)

        # username
        self.username_frame = ttk.Frame(self.connection_configuration_frame)
        self.username_frame.pack(fill="x")
        self.username_label = ttk.Label(self.username_frame, width=20)
        self.username_label["anchor"] = "e"
        self.username_label["text"] = "Username"
        self.username_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.username_input = ttk.Entry(self.username_frame)
        self.username_input.pack(side=tk.LEFT, padx=2)

        # password
        self.password_frame = ttk.Frame(self.connection_configuration_frame)
        self.password_frame.pack(fill="x")
        self.password_label = ttk.Label(self.password_frame, width=20)
        self.password_label["anchor"] = "e"
        self.password_label["text"] = "Password"
        self.password_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.password_input = ttk.Entry(self.password_frame)
        self.password_input.pack(side=tk.LEFT, padx=2)

        # timeout
        self.timeout_frame = ttk.Frame(self.connection_configuration_frame)
        self.timeout_frame.pack(fill="x")
        self.timeout_label = ttk.Label(self.timeout_frame, width=20)
        self.timeout_label["anchor"] = "e"
        self.timeout_label["text"] = "Timeout"
        self.timeout_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.timeout_input = ttk.Entry(self.timeout_frame)
        self.timeout_input.configure(validate="all", validatecommand=vcmd)
        self.timeout_input.pack(side=tk.LEFT, padx=2)

        # keepalive
        self.keepalive_frame = ttk.Frame(self.connection_configuration_frame)
        self.keepalive_frame.pack(fill="x")
        self.keepalive_label = ttk.Label(self.keepalive_frame, width=20)
        self.keepalive_label["anchor"] = "e"
        self.keepalive_label["text"] = "Keepalive"
        self.keepalive_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.keepalive_input = ttk.Entry(self.keepalive_frame)
        self.keepalive_input.configure(validate="all", validatecommand=vcmd)
        self.keepalive_input.pack(side=tk.LEFT, padx=2)

        # MQTT version
        self.version_frame = ttk.Frame(self.connection_configuration_frame)
        self.version_frame.pack(fill="x")
        self.version_label = ttk.Label(self.version_frame, width=20)
        self.version_label["anchor"] = "e"
        self.version_label["text"] = "MQTT version"
        self.version_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.version_input = ttk.Combobox(self.version_frame)
        self.version_input.pack(side=tk.LEFT, padx=2)
        self.version_input["values"] = MQTT_VERSION_LIST
        self.version_input.current(1)
        self.version_input["state"] = "readonly"

        # SSL
        self.ssl_state_frame = ttk.Frame(self.connection_configuration_frame)
        self.ssl_state_frame.pack(fill="x")
        self.ssl_state_label = ttk.Label(self.ssl_state_frame, width=20)
        self.ssl_state_label["anchor"] = "e"
        self.ssl_state_label["text"] = "SSL"
        self.ssl_state_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.ssl_state_input = ttk.Combobox(self.ssl_state_frame)
        self.ssl_state_input.pack(side=tk.LEFT, padx=2)
        self.ssl_state_input["values"] = SSL_LIST

        self.ssl_state_input["state"] = "readonly"

        # ca file
        self.ca_file_frame = ttk.Frame(self.connection_configuration_frame)
        self.ca_file_frame.pack(fill="x")
        self.ca_file_label = ttk.Label(self.ca_file_frame, width=20)
        self.ca_file_label["anchor"] = "e"
        self.ca_file_label["text"] = "CA file"
        self.ca_file_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.ca_file_input = ttk.Entry(self.ca_file_frame, width=40)
        self.ca_file_input.pack(side=tk.LEFT, padx=2)
        self.ca_browser_button = ttk.Button(self.ca_file_frame, width=3)
        self.ca_browser_button["text"] = "..."
        self.ca_browser_button["command"] = partial(self.browse_file, target_entry=self.ca_file_input)
        self.ca_browser_button.pack(side=tk.LEFT, padx=2, pady=2)

        # client cert
        self.cl_cert_file_frame = ttk.Frame(self.connection_configuration_frame)
        self.cl_cert_file_frame.pack(fill="x")
        self.cl_cert_file_label = ttk.Label(self.cl_cert_file_frame, width=20)
        self.cl_cert_file_label["anchor"] = "e"
        self.cl_cert_file_label["text"] = "Client certificate file"
        self.cl_cert_file_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.cl_cert_file_input = ttk.Entry(self.cl_cert_file_frame, width=40)
        self.cl_cert_file_input.pack(side=tk.LEFT, padx=2)
        self.cl_cert_browser_button = ttk.Button(self.cl_cert_file_frame, width=3)
        self.cl_cert_browser_button["text"] = "..."
        self.cl_cert_browser_button["command"] = partial(self.browse_file, target_entry=self.cl_cert_file_input)
        self.cl_cert_browser_button.pack(side=tk.LEFT, padx=2, pady=2)

        # client_key
        self.cl_key_file_frame = ttk.Frame(self.connection_configuration_frame)
        self.cl_key_file_frame.pack(fill="x")
        self.cl_key_file_label = ttk.Label(self.cl_key_file_frame, width=20)
        self.cl_key_file_label["anchor"] = "e"
        self.cl_key_file_label["text"] = "Client key file"
        self.cl_key_file_label.pack(side=tk.LEFT, anchor="w", padx=2, pady=4)
        self.cl_key_file_input = ttk.Entry(self.cl_key_file_frame, width=40)
        self.cl_key_file_input.pack(side=tk.LEFT, padx=2)
        self.cl_key_browser_button = ttk.Button(self.cl_key_file_frame, width=3)
        self.cl_key_browser_button["text"] = "..."
        self.cl_key_browser_button["command"] = partial(self.browse_file, target_entry=self.cl_key_file_input)
        self.cl_key_browser_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.ssl_state_input.bind("<<ComboboxSelected>>", self.ssl_state_change)
        self.ssl_state_input.current(0)
        self.ssl_state_change(None)

        self.button_frame = ttk.Frame(self.connection_configuration_frame)
        self.button_frame.pack(side='bottom', fill='x', anchor='s', expand=1)
        self.ok_button = ttk.Button(self.button_frame, text="OK")
        self.ok_button.pack(side=tk.RIGHT, pady=5, padx=5)
        self.ok_button["command"] = self.ok
        self.apply_button = ttk.Button(self.button_frame, text="Apply")
        self.apply_button.pack(side=tk.RIGHT, pady=5, padx=5)
        self.apply_button["command"] = self.apply
        self.cancel_button = ttk.Button(self.button_frame, text="Cancel")
        self.cancel_button.pack(side=tk.RIGHT, pady=5, padx=5)
        self.cancel_button["command"] = self.cancel

        self.all_config_state_change("disabled")

        self.profiles_widgets = {}

        connection_profiles = self.config_handler.get_connection_profiles()
        for connection_profile in sorted(connection_profiles):
            self.add_profile_widget(connection_profile)

    def on_generate_client_id(self):
        self.client_id_input.delete(0, tk.END)
        self.client_id_input.insert(0, str(uuid.uuid4()).replace("-", ""))

    def apply(self):
        self.save_current_config()

    def ok(self):
        self.save_current_config()
        self.on_destroy()

    def cancel(self):
        self.on_destroy()

    def on_remove(self):
        if self.currently_selected_connection is not None:
            self.config_handler.remove_connection_config(self.currently_selected_connection)
            self.profiles_widgets[self.currently_selected_connection].pack_forget()
            self.profiles_widgets.pop(self.currently_selected_connection)
            if len(self.profiles_widgets) != 0:
                self.connection_selected(list(self.profiles_widgets.keys())[0])

    def save_current_config(self):
        if self.currently_selected_connection is None:
            return
        config_dict = {
            "broker_addr": self.broker_address_input.get(),
            "broker_port": self.broker_port_name_input.get(),
            "client_id": self.client_id_input.get(),
            "user": self.username_input.get(),
            "pass": self.password_input.get(),
            "timeout": self.timeout_input.get(),
            "keepalive": self.keepalive_input.get(),
            "mqtt_version": self.version_input.get(),
            "ssl": self.ssl_state_input.get(),
            "ca_file": self.ca_file_input.get(),
            "cl_cert": self.cl_cert_file_input.get(),
            "cl_key": self.cl_key_file_input.get()
        }

        self.currently_selected_connection_dict = config_dict
        self.config_handler.save_connection_config(self.profile_name_input.get(), config_dict)

        # If there was a name change, delete the old from the config file via the config handler and update the widget
        if self.profile_name_input.get() != self.currently_selected_connection:
            self.config_handler.remove_connection_config(self.currently_selected_connection)
            self.profiles_widgets[self.currently_selected_connection].connection_name = self.profile_name_input.get()
            self.profiles_widgets[self.currently_selected_connection].connection["text"] = self.profile_name_input.get()
            self.profiles_widgets[self.profile_name_input.get()] = self.profiles_widgets[self.currently_selected_connection]
            self.config_handler.remove_connection_config(self.currently_selected_connection)
            self.connection_selected(self.currently_selected_connection)

    def browse_file(self, target_entry):
        target_text = filedialog.askopenfilename(initialdir=str(Path.home()),
                                                 title="Select CA file")
        print(target_text)
        target_entry.delete(0, tk.END)
        target_entry.insert(0, target_text)

    def add_profile_widget(self, connection_profile):
        self.profiles_widgets[connection_profile] = ConnectionFrame(self.connections_listbox.viewPort,
                                                                    connection_profile,
                                                                    self.connection_selected)
        self.profiles_widgets[connection_profile].pack(fill=tk.X, expand=1, padx=2, pady=2)

    def new_connection(self):
        name = validate_name("New connection", self.profiles_widgets)
        self.add_profile_widget(name)
        self.profiles_widgets[name].on_click(None)
        self.connection_selected(name)
        self.currently_selected_connection_dict = {}

    def connection_selected(self, connection_name):
        if self.currently_selected_connection != connection_name:
            try:
                self.profiles_widgets[self.currently_selected_connection].on_unselect()
            except Exception as e:
                print("Exception deselecting profile widget", e, self.currently_selected_connection, connection_name)
            try:
                self.all_config_state_change("normal")
                self.currently_selected_connection_dict = self.config_handler.get_connection_config_dict(connection_name).get("connection_parameters", {})
                self.profile_name_input.delete(0, tk.END)
                self.profile_name_input.insert(0, connection_name)
                self.broker_address_input.delete(0, tk.END)
                self.broker_address_input.insert(0, self.currently_selected_connection_dict.get("broker_addr", "mqtt.example.com"))
                self.broker_port_name_input.delete(0, tk.END)
                self.broker_port_name_input.insert(0, self.currently_selected_connection_dict.get("broker_port", "1883"))
                self.client_id_input.delete(0, tk.END)
                self.client_id_input.insert(0, self.currently_selected_connection_dict.get("client_id", "MQTTk_Client"))
                self.username_input.delete(0, tk.END)
                self.username_input.insert(0, self.currently_selected_connection_dict.get("user", ""))
                self.password_input.delete(0, tk.END)
                self.password_input.insert(0, self.currently_selected_connection_dict.get("pass", ""))
                self.timeout_input.delete(0, tk.END)
                self.timeout_input.insert(0, self.currently_selected_connection_dict.get("timeout", "10"))
                self.keepalive_input.delete(0, tk.END)
                self.keepalive_input.insert(0, self.currently_selected_connection_dict.get("keepalive", "60"))

                mqtt_version = self.currently_selected_connection_dict.get("mqtt_version", "")
                if mqtt_version in MQTT_VERSION_LIST:
                    self.version_input.current(MQTT_VERSION_LIST.index(mqtt_version))
                else:
                    self.version_input.current(1)

                ssl = self.currently_selected_connection_dict.get("ssl", "")
                if ssl in SSL_LIST:
                    self.ssl_state_input.current(SSL_LIST.index(ssl))
                else:
                    self.ssl_state_input.current(0)
                self.ssl_state_change(None)

                self.ca_file_input.delete(0, tk.END)
                self.ca_file_input.insert(0, self.currently_selected_connection_dict.get("ca_file", ""))
                self.cl_cert_file_input.delete(0, tk.END)
                self.cl_cert_file_input.insert(0, self.currently_selected_connection_dict.get("cl_cert", ""))
                self.cl_key_file_input.delete(0, tk.END)
                self.cl_key_file_input.insert(0, self.currently_selected_connection_dict.get("cl_key", ""))
            except Exception as e:
                self.all_config_state_change("disabled")
                print("Failed to load connection!", e)
            else:
                self.currently_selected_connection = connection_name
                self.all_config_state_change("normal")

    def all_config_state_change(self, state):
        self.profile_name_input.configure(state=state)
        self.broker_address_input.configure(state=state)
        self.broker_port_name_input.configure(state=state)
        self.client_id_input.configure(state=state)
        self.client_id_generate_button.configure(state=state)
        self.username_input.configure(state=state)
        self.password_input.configure(state=state)
        self.timeout_input.configure(state=state)
        self.keepalive_input.configure(state=state)

    def cert_state_change(self, ca, clc, clk):
        self.ca_file_input.configure(state=ca)
        self.ca_browser_button.configure(state=ca)
        self.cl_cert_file_input.configure(state=clc)
        self.cl_cert_browser_button.configure(state=clc)
        self.cl_key_file_input.configure(state=clk)
        self.cl_key_browser_button.configure(state=clk)

    def ssl_state_change(self, event):
        if self.ssl_state_input.get() == "Disabled" or self.ssl_state_input.get() == "CA signed server certificate":
            self.cert_state_change("disabled", "disabled", "disabled")
        elif self.ssl_state_input.get() == "CA certificate file":
            self.cert_state_change("normal", "disabled", "disabled")
        else:
            self.cert_state_change("normal", "normal", "normal")

    def on_destroy(self, *args, **kwargs):
        self.grab_release()
        if self.config_update_callback is not None:
            self.config_update_callback()
        self.destroy()
