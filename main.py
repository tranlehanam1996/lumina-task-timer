import tkinter as tk
from tkinter import messagebox, ttk
import platform
import datetime
import os

# Conditional import for sound to maintain cross-platform compatibility
if platform.system() == "Windows":
    import winsound
else:
    winsound = None

class LuminaTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Lumina Task Timer")
        
        # Window dimensions and centering
        window_width = 350
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.configure(bg="#2c3e50")

        self.work_time = 25 * 60
        self.break_time = 5 * 60
        self.current_time = self.work_time
        self.is_running = False
        self.is_work_session = True
        self.sessions_completed = 0
        self.log_file = "session_logs.txt"

        self.setup_ui()

    def setup_ui(self):
        self.label_status = tk.Label(
            self.root, text="Work Session", font=("Helvetica", 18, "bold"),
            bg="#2c3e50", fg="#ecf0f1"
        )
        self.label_status.pack(pady=20)

        # Task Input
        task_frame = tk.Frame(self.root, bg="#2c3e50")
        task_frame.pack(pady=10)
        tk.Label(task_frame, text="Current Task:", bg="#2c3e50", fg="#bdc3c7", font=("Helvetica", 10)).pack()
        self.task_entry = tk.Entry(task_frame, width=30, justify='center', font=("Helvetica", 12))
        self.task_entry.insert(0, "Focus on a task...")
        self.task_entry.pack(pady=5)

        self.label_timer = tk.Label(
            self.root, text="25:00", font=("Helvetica", 48),
            bg="#2c3e50", fg="#e74c3c"
        )
        self.label_timer.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=250, mode="determinate")
        self.progress.pack(pady=10)
        self.update_progress()

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

        self.btn_logs = tk.Button(
            self.root, text="View Logs", command=self.view_logs,
            font=("Helvetica", 10), bg="#34495e", fg="#bdc3c7",
            relief="flat"
        )
        self.btn_logs.pack(pady=10)

    def update_progress(self):
        total = self.work_time if self.is_work_session else self.break_time
        # Progress bar represents time elapsed
        elapsed = total - self.current_time
        percentage = (elapsed / total) * 100 if total > 0 else 0
        self.progress['value'] = percentage

    def apply_settings(self):
        try:
            new_work = int(self.work_entry.get()) * 60
            new_break = int(self.break_entry.get()) * 60
            
            if new_work <= 0 or new_break <= 0:
                raise ValueError("Time must be positive")

            self.work_time = new_work
            self.break_time = new_break
            
            if not self.is_running:
                # Update current timer display immediately if not running
                if self.is_work_session:
                    self.current_time = self.work_time
                else:
                    self.current_time = self.break_time
                
                mins, secs = divmod(self.current_time, 60)
                self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
                self.update_progress()
            
            messagebox.showinfo("Settings", "Timer durations updated!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive numbers for minutes.")

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
        self.update_progress()
        self.root.title("Lumina Task Timer")

    def tick(self):
        if self.is_running:
            if self.current_time > 0:
                self.current_time -= 1
                mins, secs = divmod(self.current_time, 60)
                time_str = f"{mins:02d}:{secs:02d}"
                self.label_timer.config(text=time_str)
                self.root.title(f"Lumina - {time_str}")
                self.update_progress()
                self.root.after(1000, self.tick)
            else:
                self.handle_session_complete()

    def play_notification_sound(self):
        if winsound:
            try:
                winsound.Beep(1000, 500)
            except Exception:
                pass

    def log_session(self):
        task = self.task_entry.get()
        if task == "Focus on a task..." or not task.strip():
            task = "Unnamed Task"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        duration = self.work_time // 60
        
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] Task: {task} | Duration: {duration} min\n")

    def view_logs(self):
        if not os.path.exists(self.log_file):
            messagebox.showinfo("Logs", "No session logs found yet!")
            return

        logs_window = tk.Toplevel(self.root)
        logs_window.title("Session History")
        logs_window.geometry("400x300")
        logs_window.configure(bg="#2c3e50")

        text_area = tk.Text(logs_window, wrap="word", bg="#34495e", fg="#ecf0f1", font=("Helvetica", 10))
        text_area.pack(padx=10, pady=10, expand=True, fill="both")

        with open(self.log_file, "r") as f:
            text_area.insert(tk.END, f.read())
        
        text_area.config(state=tk.DISABLED)

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
            self.log_session()
            self.label_sessions.config(text=f"Sessions Completed: {self.sessions_completed}")
            self.current_time = self.break_time
            self.label_status.config(text="Break Time")
            self.label_timer.config(fg="#3498db")
            msg = "Work session complete! Take a break."

        mins, secs = divmod(self.current_time, 60)
        self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
        self.update_progress()
        self.btn_start.config(text="Start", bg="#27ae60")
        self.root.title("Lumina Task Timer")
        
        self.play_notification_sound()
        messagebox.showinfo("Timer", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = LuminaTimer(root)
    root.mainloop()