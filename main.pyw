import logging
import os
from datetime import datetime
from ftplib import FTP
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter.messagebox import showerror

import pandas as pd

from mysecrets import *

dirname = os.path.abspath(os.path.dirname(__file__))
output_dir = os.path.join(dirname, "roman-toolbox")
logs_dir = os.path.join(output_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)


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
        self.button = ttk.Button(container, text="Choisir un fichier", command=self.upload)
        self.button.grid(column=0, row=1)
        self.status_label = ttk.Label(container, text="")
        self.status_label.grid(column=0, row=2)

    def upload(self):
        self.button["state"] = "disabled"
        try:
            with FTP(FTP_SRV) as ftp:
                ftp.login(user=FTP_USR, passwd=FTP_PWD)
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
