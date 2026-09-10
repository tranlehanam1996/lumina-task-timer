import tkinter as tk
from tkinter import messagebox
import platform

# Conditional import for sound to maintain cross-platform compatibility
if platform.system() == "Windows":
    import winsound
else:
    winsound = None

class LuminaTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Lumina Task Timer")
        self.root.geometry("350x550")
        self.root.configure(bg="#2c3e50")

        self.work_time = 25 * 60
        self.break_time = 5 * 60
        self.current_time = self.work_time
        self.is_running = False
        self.is_work_session = True
        self.sessions_completed = 0

        self.setup_ui()

    def setup_ui(self):
        self.label_status = tk.Label(
            self.root, text="Work Session", font=("Helvetica", 18, "bold"),
            bg="#2c3e50", fg="#ecf0f1"
        )
        self.label_status.pack(pady=20)

        self.label_timer = tk.Label(
            self.root, text="25:00", font=("Helvetica", 48),
            bg="#2c3e50", fg="#e74c3c"
        )
        self.label_timer.pack(pady=20)

        self.label_sessions = tk.Label(
            self.root, text="Sessions Completed: 0", font=("Helvetica", 12),
            bg="#2c3e50", fg="#bdc3c7"
        )
        self.label_sessions.pack(pady=10)

        # Settings Frame
        settings_frame = tk.Frame(self.root, bg="#2c3e50")
        settings_frame.pack(pady=20)

        tk.Label(settings_frame, text="Work (min):", bg="#2c3e50", fg="#ecf0f1").grid(row=0, column=0, padx=5)
        self.work_entry = tk.Entry(settings_frame, width=5)
        self.work_entry.insert(0, "25")
        self.work_entry.grid(row=0, column=1, padx=5)

        tk.Label(settings_frame, text="Break (min):", bg="#2c3e50", fg="#ecf0f1").grid(row=1, column=0, padx=5)
        self.break_entry = tk.Entry(settings_frame, width=5)
        self.break_entry.insert(0, "5")
        self.break_entry.grid(row=1, column=1, padx=5)

        self.btn_apply = tk.Button(
            self.root, text="Apply Settings", command=self.apply_settings,
            font=("Helvetica", 10), bg="#95a5a6", fg="white",
            relief="flat"
        )
        self.btn_apply.pack(pady=5)

        self.btn_start = tk.Button(
            self.root, text="Start", command=self.toggle_timer,
            font=("Helvetica", 12), bg="#27ae60", fg="white",
            width=10, relief="flat"
        )
        self.btn_start.pack(pady=10)

        self.btn_reset = tk.Button(
            self.root, text="Reset", command=self.reset_timer,
            font=("Helvetica", 12), bg="#c0392b", fg="white",
            width=10, relief="flat"
        )
        self.btn_reset.pack(pady=10)

    def apply_settings(self):
        try:
            self.work_time = int(self.work_entry.get()) * 60
            self.break_time = int(self.break_entry.get()) * 60
            if not self.is_running:
                self.reset_timer()
            messagebox.showinfo("Settings", "Timer durations updated!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for minutes.")

    def toggle_timer(self):
        if self.is_running:
            self.is_running = False
            self.btn_start.config(text="Start", bg="#27ae60")
        else:
            self.is_running = True
            self.btn_start.config(text="Pause", bg="#f39c12")
            self.tick()

    def reset_timer(self):
        self.is_running = False
        self.is_work_session = True
        self.current_time = self.work_time
        self.btn_start.config(text="Start", bg="#27ae60")
        self.label_status.config(text="Work Session")
        mins, secs = divmod(self.current_time, 60)
        self.label_timer.config(text=f"{mins:02d}:{secs:02d}")

    def tick(self):
        if self.is_running:
            if self.current_time > 0:
                self.current_time -= 1
                mins, secs = divmod(self.current_time, 60)
                self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
                self.root.after(1000, self.tick)
            else:
                self.handle_session_complete()

    def play_notification_sound(self):
        if winsound:
            try:
                winsound.Beep(1000, 500)
            except Exception:
                pass

    def handle_session_complete(self):
        self.is_running = False
        self.is_work_session = not self.is_work_session
        
        if self.is_work_session:
            self.current_time = self.work_time
            self.label_status.config(text="Work Session")
            self.label_timer.config(fg="#e74c3c")
            msg = "Break over! Time to focus."
        else:
            self.sessions_completed += 1
            self.label_sessions.config(text=f"Sessions Completed: {self.sessions_completed}")
            self.current_time = self.break_time
            self.label_status.config(text="Break Time")
            self.label_timer.config(fg="#3498db")
            msg = "Work session complete! Take a break."

        mins, secs = divmod(self.current_time, 60)
        self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
        self.btn_start.config(text="Start", bg="#27ae60")
        
        self.play_notification_sound()
        messagebox.showinfo("Timer", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = LuminaTimer(root)
    root.mainloop()