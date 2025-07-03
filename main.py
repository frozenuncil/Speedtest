import customtkinter as ctk
import speedtest
import threading
import time
import math
from datetime import datetime
import csv

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

APP_WIDTH = 700
APP_HEIGHT = 520
BG_COLORS = ["#0f0f0f", "#1a1a2e", "#2e2e4a", "#3e3e63", "#2e2e4a", "#1a1a2e"]

class SpeedtestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌐 Ultimate Speedtest App")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)

        self.bg_index = 0
        self.test_active = False
        self.spinner_active = False
        self.ui_locked = False
        self.angle = 0

        self.create_widgets()
        self.animate_background()

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self, width=650, height=480, corner_radius=20, fg_color="#111111")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self.main_frame, text="🌐 Ultimate Internet Speedtest", font=("Segoe UI", 30, "bold"))
        self.title_label.pack(pady=20)

        self.canvas = ctk.CTkCanvas(self.main_frame, width=150, height=150, bg="#111111", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.download_label = ctk.CTkLabel(self.main_frame, text="⬇ Download: --- Mbps", font=("Segoe UI", 20))
        self.download_label.pack(pady=5)

        self.upload_label = ctk.CTkLabel(self.main_frame, text="⬆ Upload: --- Mbps", font=("Segoe UI", 20))
        self.upload_label.pack(pady=5)

        self.ping_label = ctk.CTkLabel(self.main_frame, text="📶 Ping: --- ms", font=("Segoe UI", 18), text_color="#888888")
        self.ping_label.pack(pady=5)

        self.status_label = ctk.CTkLabel(self.main_frame, text="", font=("Segoe UI", 16), text_color="#888888")
        self.status_label.pack(pady=10)

        self.download_bar = ctk.CTkProgressBar(self.main_frame, width=500)
        self.download_bar.set(0)
        self.download_bar.pack(pady=5)

        self.upload_bar = ctk.CTkProgressBar(self.main_frame, width=500)
        self.upload_bar.set(0)
        self.upload_bar.pack(pady=5)

        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(pady=20)

        self.start_button = ctk.CTkButton(
            self.buttons_frame,
            text="⚡ Start Speedtest",
            font=("Segoe UI", 20),
            fg_color="#1f6feb",
            hover_color="#388bfd",
            corner_radius=12,
            width=200,
            height=50,
            command=self.toggle_speedtest
        )
        self.start_button.grid(row=0, column=0, padx=10)

        self.export_button = ctk.CTkButton(
            self.buttons_frame,
            text="📁 Export Logs",
            font=("Segoe UI", 20),
            fg_color="#3a7bd5",
            hover_color="#5596f9",
            corner_radius=12,
            width=200,
            height=50,
            command=self.export_logs
        )
        self.export_button.grid(row=0, column=1, padx=10)

    def animate_background(self):
        color = BG_COLORS[self.bg_index % len(BG_COLORS)]
        self.configure(bg=color)
        self.main_frame.configure(fg_color=color)
        self.bg_index += 1
        self.after(1500, self.animate_background)

    def draw_spinner(self):
        self.canvas.delete("all")
        x, y, r = 75, 75, 60
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline="#444444", width=10)
        self.canvas.create_arc(x - r, y - r, x + r, y + r, start=self.angle, extent=90, outline="#1f6feb", width=10, style="arc")

    def animate_spinner(self):
        if not self.spinner_active:
            return
        self.angle = (self.angle + 8) % 360
        self.draw_spinner()
        self.after(20, self.animate_spinner)

    def toggle_speedtest(self):
        if self.test_active or self.ui_locked:
            return
        self.test_active = True
        self.ui_locked = True
        self.spinner_active = True
        self.status_label.configure(text="🔄 Running speedtest...")
        self.start_button.configure(text="⏳ Testing...")

        threading.Thread(target=self.run_speedtest, daemon=True).start()
        self.animate_spinner()

    def run_speedtest(self):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            ping = st.results.ping

            self.ping_label.configure(text=f"📶 Ping: {ping:.0f} ms")
            self.status_label.configure(text="⬇ Downloading...")
            download = st.download() / 1_000_000
            self.download_bar.set(1)
            self.download_label.configure(text=f"⬇ Download: {download:.2f} Mbps")

            self.status_label.configure(text="⬆ Uploading...")
            upload = st.upload() / 1_000_000
            self.upload_bar.set(1)
            self.upload_label.configure(text=f"⬆ Upload: {upload:.2f} Mbps")

            self.status_label.configure(text="✅ Speedtest complete!")
            self.log_result(download, upload, ping)

        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {e}")

        self.spinner_active = False
        self.test_active = False
        self.ui_locked = False
        self.start_button.configure(text="⚡ Start Speedtest")

    def log_result(self, download, upload, ping):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp}, {download:.2f}, {upload:.2f}, {ping:.0f}\n"
        with open("speedtest_log.txt", "a") as f:
            f.write(line)

    def export_logs(self):
        try:
            with open("speedtest_log.txt", "r") as f:
                lines = f.readlines()

            if not lines:
                self.status_label.configure(text="ℹ️ No logs to export.")
                return

            with open("speedtest_export.csv", "w", newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["Timestamp", "Download Mbps", "Upload Mbps", "Ping ms"])
                for line in lines:
                    csvwriter.writerow(line.strip().split(", "))

            self.status_label.configure(text="✅ Exported to speedtest_export.csv")

        except Exception as e:
            self.status_label.configure(text=f"❌ Export failed: {e}")

if __name__ == "__main__":
    app = SpeedtestApp()
    app.mainloop()
