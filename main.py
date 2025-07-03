import customtkinter as ctk
import speedtest
import threading
import time
import math
import csv
from datetime import datetime

#
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


APP_WIDTH = 700
APP_HEIGHT = 520
BG_COLORS = ["#0f0f0f", "#1a1a2e", "#2e2e4a", "#3e3e63", "#2e2e4a", "#1a1a2e"]

class SpeedtestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ultimate Speedtest App")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)

     
        self.bg_index = 0

       
        self.st = None
        self.running = False
        self.angle = 0
        self.download_speed = 0.0
        self.upload_speed = 0.0
        self.ping = 0.0

        self.create_widgets()
        self.start_background_animation()

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
            text="Start Speedtest",
            font=("Segoe UI", 20),
            fg_color="#1f6feb",
            hover_color="#388bfd",
            corner_radius=12,
            width=200,
            height=50,
            command=self.toggle_speedtest
        )
        self.start_button.grid(row=0, column=0, padx=10)

        # Export Button
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

    def start_background_animation(self):
        def animate():
            while True:
                color = BG_COLORS[self.bg_index % len(BG_COLORS)]
                self.configure(bg=color)
                self.main_frame.configure(fg_color=color)
                self.bg_index += 1
                time.sleep(1.5)
        threading.Thread(target=animate, daemon=True).start()

    def draw_spinner(self, progress=0):
        self.canvas.delete("all")
        x, y, r = 75, 75, 60
       
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline="#444444", width=10)
        # Progress arc
        extent = progress * 360
        start_angle = self.angle % 360
        self.canvas.create_arc(x - r, y - r, x + r, y + r, start=start_angle, extent=extent, outline="#1f6feb", width=10, style="arc")

    def spinner_animation(self):
        while self.running:
            self.angle = (self.angle + 8) % 360
            self.draw_spinner(progress=1)
            time.sleep(0.02)

    def toggle_speedtest(self):
        if self.running:
            # Stop test
            self.running = False
            self.start_button.configure(text="⚡ Start Speedtest")
            self.status_label.configure(text="🛑 Speedtest stopped.")
        else:
            # Start test
            self.running = True
            self.start_button.configure(text="⏹ Stop Speedtest")
            threading.Thread(target=self.run_speedtest, daemon=True).start()
            threading.Thread(target=self.spinner_animation, daemon=True).start()

    def run_speedtest(self):
        self.status_label.configure(text="🔄 Finding best server...")
        self.download_label.configure(text="⬇ Download: --- Mbps")
        self.upload_label.configure(text="⬆ Upload: --- Mbps")
        self.ping_label.configure(text="📶 Ping: --- ms")
        self.download_bar.set(0)
        self.upload_bar.set(0)

        try:
            self.st = speedtest.Speedtest()
            self.st.get_best_server()
            self.ping = self.st.results.ping
            self.ping_label.configure(text=f"📶 Ping: {self.ping:.0f} ms")
        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {e}")
            self.running = False
            self.start_button.configure(text="⚡ Start Speedtest")
            return

        # Download speed test with progress update
        self.status_label.configure(text="⬇ Testing download speed...")
        try:
            # Download test in a thread (blocking, no progress callback)
            download_thread = threading.Thread(target=self.download_test, daemon=True)
            download_thread.start()

            # While download test runs, fake progress bar animation
            for i in range(101):
                if not self.running:
                    return
                self.download_bar.set(i / 100)
                time.sleep(0.04)
            download_thread.join()
        except Exception as e:
            self.status_label.configure(text=f"❌ Download test error: {e}")
            self.running = False
            self.start_button.configure(text="⚡ Start Speedtest")
            return

        # Upload speed test with progress update
        self.status_label.configure(text="⬆ Testing upload speed...")
        try:
            upload_thread = threading.Thread(target=self.upload_test, daemon=True)
            upload_thread.start()

            for i in range(101):
                if not self.running:
                    return
                self.upload_bar.set(i / 100)
                time.sleep(0.04)
            upload_thread.join()
        except Exception as e:
            self.status_label.configure(text=f"❌ Upload test error: {e}")
            self.running = False
            self.start_button.configure(text="⚡ Start Speedtest")
            return

    
        if self.running:
            self.status_label.configure(text="✅ Speedtest completed!")
            self.download_label.configure(text=f"⬇ Download: {self.download_speed:.2f} Mbps")
            self.upload_label.configure(text=f"⬆ Upload: {self.upload_speed:.2f} Mbps")
            self.ping_label.configure(text=f"📶 Ping: {self.ping:.0f} ms")
            self.running = False
            self.start_button.configure(text="⚡ Start Speedtest")
            self.log_result()
        else:
            self.status_label.configure(text="🛑 Speedtest stopped.")

    def download_test(self):
        self.download_speed = self.st.download() / 1_000_000  

    def upload_test(self):
        self.upload_speed = self.st.upload() / 1_000_000  

    def log_result(self):
        """Append the last test result to a log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp}, {self.download_speed:.2f}, {self.upload_speed:.2f}, {self.ping:.0f}\n"
        with open("speedtest_log.txt", "a") as f:
            f.write(line)

    def export_logs(self):
        """Export the log file as CSV if it exists"""
        try:
            with open("speedtest_log.txt", "r") as f:
                lines = f.readlines()

            if not lines:
                self.status_label.configure(text="ℹ️ No logs to export.")
                return

            # Write CSV file
            with open("speedtest_export.csv", "w", newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["Timestamp", "Download Mbps", "Upload Mbps", "Ping ms"])
                for line in lines:
                    csvwriter.writerow(line.strip().split(", "))

            self.status_label.configure(text="✅ Logs exported to speedtest_export.csv")

        except FileNotFoundError:
            self.status_label.configure(text="ℹ️ No logs found.")
        except Exception as e:
            self.status_label.configure(text=f"❌ Export failed: {e}")

if __name__ == "__main__":
    app = SpeedtestApp()
    app.mainloop()
