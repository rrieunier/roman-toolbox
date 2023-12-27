import logging
import os
from datetime import datetime
from ftplib import FTP
from os.path import expanduser
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter.messagebox import showerror

import pandas as pd
import yaml

home = expanduser("~")
dirname = os.path.join(home, "AppData", "Local")
output_dir = os.path.join(dirname, "roman-toolbox")
config_path = os.path.join(output_dir, "config.yml")
logs_dir = os.path.join(output_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
else:
    config = {"ftp_server": "", "ftp_user": "", "ftp_password": ""}
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f)


def persist_config(key, value):
    config[key] = value
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f)


def get_log_file():
    date = datetime.now().isoformat().replace(":", "-")
    return os.path.join(logs_dir, f"{date}.log")


logging.basicConfig(filename=get_log_file(), level=logging.DEBUG)


def create_backup(ftp):
    with open(os.path.join(output_dir, "backup.pdf"), "wb") as f:
        ftp.retrbinary("RETR tarifs-verres-tapas.pdf", f.write)


class MenuUpdate:

    def __init__(self, container):
        ttk.Label(container, text="Mettre à jour le menu").grid(column=0, row=0, sticky=(N, E, W))
        ttk.Label(container, text="Serveur FTP").grid(column=0, row=1)
        self.ftp_server = StringVar(container, config["ftp_server"])
        ttk.Entry(container, textvariable=self.ftp_server).grid(column=0, row=2)
        ttk.Label(container, text="Utilisateur FTP").grid(column=0, row=3)
        self.ftp_user = StringVar(container, config["ftp_user"])
        ttk.Entry(container, textvariable=self.ftp_user).grid(column=0, row=4)
        ttk.Label(container, text="Mot de passe FTP").grid(column=0, row=5)
        self.ftp_password = StringVar(container, config["ftp_password"])
        ttk.Entry(container, textvariable=self.ftp_password, show="*").grid(column=0, row=6)
        self.button = ttk.Button(container, text="Choisir un fichier", command=self.upload)
        self.button.grid(column=0, row=7)
        self.status_label = ttk.Label(container, text="")
        self.status_label.grid(column=0, row=8)

    def upload(self):
        self.button["state"] = "disabled"

        persist_config("ftp_server", self.ftp_server)
        persist_config("ftp_user", self.ftp_user)
        persist_config("ftp_password", self.ftp_password)

        try:
            with FTP(self.ftp_server.get()) as ftp:
                ftp.login(user=self.ftp_user.get(), passwd=self.ftp_password.get())
                ftp.cwd("/www/wp-content/uploads/menu-carte/")
                ftp.dir()
                f = filedialog.askopenfile("rb", filetypes=[("pdf", "*.pdf")])
                if f is not None:
                    logging.info("Creating backup")
                    create_backup(ftp)
                    logging.info(f)
                    ftp.storbinary("STOR tarifs-verres-tapas.pdf", f)
                    f.close()
                    ftp.dir()
                    logging.info("Uploaded")
            self.status_label["foreground"] = "#0f0"
            self.status_label["text"] = "Succès"
        except:
            self.status_label["foreground"] = "#f00"
            self.status_label["text"] = "Échec"
            raise
        finally:
            self.button["state"] = "normal"


class CSVConverter:
    def __init__(self, container):
        self.output_dir = ""
        ttk.Label(container, text="Convertir CSV en Excel").grid(column=1, row=0, sticky=(N, E, W))
        self.button = ttk.Button(container, text="Sélectionner & convertir", command=self.convert)
        self.button.grid(column=1, row=1)
        self.status_label = ttk.Label(container, text="")
        self.status_label.grid(column=1, row=2)

    def convert(self):
        self.button["state"] = "disabled"
        try:
            for f in filedialog.askopenfilenames(filetypes=[("csv", "*.csv")]):
                output_name = ".".join(f.split(".")[:-1])
                self.output_dir = os.path.dirname(output_name)
                pd.read_csv(f, sep="\t").to_excel(output_name + ".xlsx", index=False)
            os.startfile(self.output_dir)
            self.status_label["foreground"] = "#0f0"
            self.status_label["text"] = "Succès"
        except:
            self.status_label["foreground"] = "#f00"
            self.status_label["text"] = "Échec"
            raise
        finally:
            self.button["state"] = "normal"


class TkWrapper(Tk):

    def report_callback_exception(self, exc, val, tb):
        showerror("Erreur", message=str(val))


if __name__ == "__main__":
    mainframe = TkWrapper()

    mainframe.title("Roman Pépère Toolbox")

    # mainframe = ttk.Frame(root, padding="3 3 12 12", width=300, height=200)
    # mainframe.grid(column=0, row=0, sticky=NSEW)

    MenuUpdate(mainframe)
    CSVConverter(mainframe)

    mainframe.grid_columnconfigure(0, weight=1)
    mainframe.grid_columnconfigure(1, weight=1)
    mainframe.grid_rowconfigure(0, weight=1)

    mainframe.mainloop()
