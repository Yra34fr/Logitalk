import base64
import io
import os.path
import threading
from socket import *
from customtkinter import *
from PIL import Image

class MW(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.title("LogiTalk")
        self.username = "R0man"
        self.label = None
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_sh_m = False
        self.sp_anm_m = -20
        self.btn = CTkButton(self, text=">",
                             command=self.tgl_sh_m,
                             width=30)
        self.btn.place(x=0, y=0)

        self.ch_fd = CTkScrollableFrame(self)
        self.ch_fd.place(x=0, y=0)

        self.mess_enr = CTkEntry(self,
                                 placeholder_text="Введіть повідомлення: ",
                                 height=40)
        self.mess_enr.place(x=0, y=0)

        self.send_btn = CTkButton(self, text="Send",
                                  width=50, height=50,
                                  command=self.send_mess)
        self.send_btn.place(x=0, y=0)

        self.open_img = CTkButton(self, text="IMG",
                                  width=50, height=50,
                                  command=self.open_image)
        self.open_img.place(x=0, y=0)
        self.adaptive()

        try:
            if os.path.exists("1.jpg"):
                self.add_mess("Демонстрація відображення зображення: ",
                              CTkImage(Image.open("1.jpg"), size=(300, 300)))
        except:
            pass

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("6.tcp.eu.ngrok.io", 16077))
            hello = f"TEXT@{self.username}@...\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_mess, daemon=True).start()
        except Exception as e:
            self.after(1000, lambda: self.add_mess(f"Не вдалося підключитися: {e}"))

    def tgl_sh_m(self):
        if self.is_sh_m:
            self.is_sh_m = False
            self.btn.configure(text=">")
            self.sh_m()
        else:
            self.is_sh_m = True
            self.btn.configure(text="<")
            self.sh_m()
            self.label = CTkLabel(self.menu_frame, text="Ім'я")
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...")
            self.entry.pack()
            self.save_btn = CTkButton(self.menu_frame, text="Зберегти",
                                      command=self.save_name)
            self.save_btn.pack(pady=10)

    def sh_m(self):
        current_width = self.menu_frame.winfo_width()
        if self.is_sh_m and current_width < 200:
            self.menu_frame.configure(width=current_width + 20)
            self.after(10, self.sh_m)
        elif not self.is_sh_m and current_width > 30:
            self.menu_frame.configure(width=current_width - 20)
            self.after(10, self.sh_m)
            if current_width <= 50:
                for widget in self.menu_frame.winfo_children():
                    widget.destroy()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_mess(f"Ваш новий нік: {self.username}")

    def adaptive(self):
        try:
            m_width = self.menu_frame.winfo_width()
            w_width = self.winfo_width()
            w_height = self.winfo_height()
            self.menu_frame.configure(height=w_height)
            self.ch_fd.place(x=m_width, y=0)
            self.ch_fd.configure(width=w_width - m_width - 20, height=w_height - 60)
            self.send_btn.place(x=w_width - 60, y=w_height - 55)
            self.open_img.place(x=w_width - 115, y=w_height - 55)
            self.mess_enr.place(x=m_width + 10, y=w_height - 55)
            self.mess_enr.configure(width=w_width - m_width - 135)
        except:
            pass
        self.after(50, self.adaptive)

    def add_mess(self, message, img=None):
        wr_size = max(100, self.ch_fd.winfo_width() - 40)
        mess_frame = CTkFrame(self.ch_fd, fg_color="#3d3d3d")
        mess_frame.pack(pady=5, anchor="w", padx=10)
        if img:
            CTkLabel(mess_frame, text=message, image=img, compound="top",
                     wraplength=wr_size, justify="left").pack(pady=5, padx=10)
        else:
            CTkLabel(mess_frame, text=message, wraplength=wr_size,
                     justify="left").pack(pady=5, padx=10)

    def send_mess(self):
        message = self.mess_enr.get()
        if message:
            self.add_mess(f"Ви: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode('utf-8'))
            except:
                pass
        self.mess_enr.delete(0, END)

    def recv_mess(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk: break
                buffer += chunk.decode('utf-8', errors="ignore")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break

    def handle_line(self, line):
        if not line: return
        parts = line.split("@")
        if parts[0] == "TEXT" and len(parts) >= 3:
            self.add_mess(f"{parts[1]} : {parts[2]}")
        elif parts[0] == "IMAGE" and len(parts) >= 4:
            try:
                img_data = base64.b64decode(parts[3])
                pil_img = Image.open(io.BytesIO(img_data))
                ctk_img = CTkImage(pil_img, size=(250, 250))
                self.add_mess(f"{parts[1]} надіслав фото", img=ctk_img)
            except:
                pass

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if not file_path: return
        try:
            with open(file_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode()
            data = f"IMAGE@{self.username}@{os.path.basename(file_path)}@{b64_data}\n"
            self.sock.sendall(data.encode('utf-8'))
            self.add_mess("Ви надіслали фото",
                          img=CTkImage(Image.open(file_path), size=(250, 250)))
        except:
            pass

if __name__ == "__main__":
    app = MW()
    app.mainloop()
