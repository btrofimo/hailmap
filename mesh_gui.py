import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from geopy.geocoders import Nominatim
import boto3

from process_mesh import load_mesh
from mesh_utils import make_figure, save_figure

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
BUCKET = 'noaa-mrms-pds'
PREFIX = 'MESHMax/'

class S3Browser(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title('S3 Browser')
        self.geometry('400x300')
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind('<Double-1>', self.download_file)
        tk.Button(self, text='Refresh', command=self.refresh).pack()
        self.s3 = boto3.client('s3')
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        try:
            resp = self.s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX, Delimiter='/', MaxKeys=1000)
            for obj in resp.get('Contents', []):
                key = obj['Key']
                if key.endswith('.gz'):
                    self.listbox.insert(tk.END, key)
        except Exception as exc:
            messagebox.showerror('Error', f'Failed to list bucket: {exc}')

    def download_file(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        key = self.listbox.get(selection[0])
        local_path = os.path.join(DATA_DIR, os.path.basename(key))
        try:
            self.s3.download_file(BUCKET, key, local_path)
            messagebox.showinfo('Downloaded', f'Saved to {local_path}')
        except Exception as exc:
            messagebox.showerror('Error', f'Failed to download: {exc}')

class MeshApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('MESH-MAP')
        self.geometry('800x600')

        self.fig = None
        self.canvas = None
        self.pin = None

        open_btn = tk.Button(self, text='Open File', command=self.open_file)
        open_btn.pack(side=tk.TOP, fill=tk.X)

        s3_btn = tk.Button(self, text='S3 Browser', command=self.open_s3)
        s3_btn.pack(side=tk.TOP, fill=tk.X)

        addr_btn = tk.Button(self, text='Pin Address', command=self.pin_address)
        addr_btn.pack(side=tk.TOP, fill=tk.X)

        export_btn = tk.Button(self, text='Export PNG', command=self.export_png)
        export_btn.pack(side=tk.TOP, fill=tk.X)

    def open_file(self):
        path = filedialog.askopenfilename(initialdir=DATA_DIR,
                                           filetypes=[('MESH files', '*.gz *.grib2 *.nc'),
                                                      ('All files', '*.*')])
        if not path:
            return
        try:
            lats, lons, data = load_mesh(path)
            self.fig = make_figure(lats, lons, data, pin=self.pin)
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as exc:
            messagebox.showerror('Error', str(exc))

    def open_s3(self):
        S3Browser(self)

    def pin_address(self):
        address = simpledialog.askstring('Address', 'Enter address:')
        if not address:
            return
        geolocator = Nominatim(user_agent='mesh_map')
        try:
            location = geolocator.geocode(address)
        except Exception as exc:
            messagebox.showerror('Error', f'Geocode failed: {exc}')
            return
        if location:
            self.pin = (location.latitude, location.longitude)
            if self.fig:
                self.open_file()  # redraw with pin
        else:
            messagebox.showinfo('Not found', 'Address not found')

    def export_png(self):
        if not self.fig:
            messagebox.showinfo('No figure', 'Load data first')
            return
        path = filedialog.asksaveasfilename(defaultextension='.png', initialdir=OUTPUT_DIR)
        if not path:
            return
        save_figure(self.fig, path)
        messagebox.showinfo('Saved', f'Figure saved to {path}')


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app = MeshApp()
    app.mainloop()

if __name__ == '__main__':
    main()
