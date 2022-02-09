from mqttk import __version__ as version
import tkinter as tk
import tkinter.ttk as ttk

about_text = "MQTTk is a lightweight free and open source gaphical MQTT client. It is licensed under the " \
             "GNU LGPLv3 license. To learn more about the license, see\nhttps://www.gnu.org/licenses/\n\nMQTTk " \
             "is written in pure python and uses the tk/ttk libraries. For license, see\nhttps://docs.python.org/3/" \
             "license.html\n\nMQTTk uses the Eclipse paho-mqtt client, see relevant license(s) following\nhttps:" \
             "//github.com/eclipse/paho.mqtt.python\n\nCopyright (C) 2022  Máté Szabó"


class AboutDialog(tk.Toplevel):
    def __init__(self, master, icon, style):
        super().__init__(master=master)
        self.master = master
        self.title("About")
        width = 700
        height = 350
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.resizable(False, False)
        self.geometry(alignstr)
        self.iconphoto(False, icon)

        self.about_frame = ttk.Frame(self)

        self.about_label = ttk.Label(self.about_frame, text="About MQTTk\n\nVersion {}".format(version), anchor='n', justify=tk.CENTER, font="Arial 14 bold")
        self.about_label.pack(side=tk.TOP, fill='x', expand=1)

        self.about_content_frame = ttk.Frame(self.about_frame)
        # self.icon_canvas = tk.Canvas(self.about_content_frame, width=200, height=200)
        # self.icon_canvas.create_image(10, 10, anchor='w', image=icon)
        # self.icon_canvas.pack(side=tk.LEFT, expand=1, fill='both')
        self.icon = ttk.Label(self.about_content_frame, image=icon)
        self.icon.pack(side=tk.LEFT, padx=8)
        self.about_text = tk.Text(self.about_content_frame, wrap='word', height=15, exportselection=False, font='Arial 14')
        self.about_text.pack(side=tk.RIGHT, fill='x', expand=1, padx=6, pady=6)
        self.about_text.insert(1.0, about_text)
        self.about_text.configure(bg=style.lookup("TLabel", "background"),
                                  relief='flat',
                                  state='disabled',
                                  borderwidth=0,
                                  border=0,
                                  highlightcolor=style.lookup("TLabel", "background"))
        self.protocol("WM_DELETE_WINDOW", self.on_destroy)
        self.about_content_frame.pack(expand=1, fill='x')

        self.ok_button = ttk.Button(self.about_frame, text="OK")
        self.ok_button.pack(side=tk.BOTTOM, pady=4)
        self.ok_button["command"] = self.on_destroy
        self.about_frame.pack(fill='both', expand=1)

    def on_destroy(self, *args, **kwargs):
        self.grab_release()
        self.destroy()


class PublishNameDialog(tk.Toplevel):
    def __init__(self, master, current_value, name_callback):
        super().__init__(master=master)
        self.master = master
        self.title("Please enter publish template name")
        self.name_callback = name_callback
        width = 250
        height = 140
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.resizable(False, False)
        self.geometry(alignstr)
        self.protocol("WM_DELETE_WINDOW", self.on_destroy)

        self.dialog_frame = ttk.Frame(self)
        self.dialog_frame.pack(fill='both', expand=1)

        self.instruction_text = ttk.Label(self.dialog_frame, text="Please enter publish template name".format(version), anchor='n', justify=tk.CENTER)
        self.instruction_text.pack(side=tk.TOP, fill='x', padx=10, pady=10)

        self.name_input = ttk.Entry(self.dialog_frame)
        self.name_input.insert(0, current_value)
        self.name_input.pack(expand=1, fill='x', side=tk.TOP, padx=10, pady=10)

        self.buttons_frame = ttk.Frame(self.dialog_frame)
        self.buttons_frame.pack(side=tk.TOP, fill='x', expand=1)
        self.ok_button = ttk.Button(self.dialog_frame, text="OK")
        self.ok_button.pack(side=tk.RIGHT, pady=10, padx=20)
        self.ok_button["command"] = self.on_save
        self.cancel_button = ttk.Button(self.dialog_frame, text="Cancel")
        self.cancel_button.pack(side=tk.LEFT, pady=10, padx=20)
        self.cancel_button["command"] = self.on_destroy

    def on_save(self, ):
        if self.name_input.get() != "":
            self.name_callback(self.name_input.get())
        self.on_destroy()

    def on_destroy(self, *args, **kwargs):
        self.grab_release()
        self.destroy()


class SplashScreen(tk.Toplevel):
    def __init__(self, master, splash_icon):
        super().__init__(master=master)
        screenwidth = master.winfo_screenwidth()
        screenheight = master.winfo_screenheight()
        self.overrideredirect(True)
        width = 350
        height = 350
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(alignstr)
        self.title("Splash")
        splash_label = ttk.Label(self, image=splash_icon)
        splash_label.pack()
        self.update()
