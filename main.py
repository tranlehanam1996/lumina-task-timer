import tkinter as tk
from tkinter import messagebox, ttk
import platform
import datetime
import os
import json

# Conditional import for sound to maintain cross-platform compatibility
if platform.system() == "Windows":
    import winsound
else:
    winsound = None

class LuminaTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Lumina Task Timer")
        
        # Themes configuration
        self.themes = {
            "dark": {
                "bg": "#2c3e50",
                "fg": "#ecf0f1",
                "accent": "#34495e",
                "text_muted": "#bdc3c7",
                "timer_color": "#e74c3c",
                "break_color": "#3498db",
                "long_break_color": "#9b59b6"
            },
            "light": {
                "bg": "#f5f6fa",
                "fg": "#2f3640",
                "accent": "#dcdde1",
                "text_muted": "#7f8c8d",
                "timer_color": "#c0392b",
                "break_color": "#2980b9",
                "long_break_color": "#8e44ad"
            }
        }
        self.current_theme = "dark"

        # Window dimensions and centering
        window_width = 350
        window_height = 850
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.configure(bg=self.themes[self.current_theme]["bg"])

        self.log_file = "session_logs.txt"
        self.config_file = "settings.json"
        self.placeholder_text = "Focus on a task..."
        
        # Load settings from file or use defaults
        self.load_settings()

        self.current_time = self.work_time
        self.is_running = False
        self.is_work_session = True
        self.sessions_completed = 0
        self.stay_on_top = False

        self.setup_ui()
        
        # Bind Enter key to toggle timer
        self.root.bind('<Return>', lambda event: self.toggle_timer())

    def load_settings(self):
        defaults = {
            "work_time": 25 * 60,
            "break_time": 5 * 60,
            "long_break_time": 15 * 60,
            "session_goal": 4,
            "stay_on_top": False,
            "auto_start": False
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    settings = json.load(f)
                    self.work_time = settings.get("work_time", defaults["work_time"])
                    self.break_time = settings.get("break_time", defaults["break_time"])
                    self.long_break_time = settings.get("long_break_time", defaults["long_break_time"])
                    self.session_goal = settings.get("session_goal", defaults["session_goal"])
                    self.stay_on_top = settings.get("stay_on_top", defaults["stay_on_top"])
                    self.auto_start = settings.get("auto_start", defaults["auto_start"])
            except (json.JSONDecodeError, IOError):
                self.work_time, self.break_time, self.long_break_time, self.session_goal, self.stay_on_top, self.auto_start = defaults.values()
        else:
            self.work_time, self.break_time, self.long_break_time, self.session_goal, self.stay_on_top, self.auto_start = defaults.values()
        
        if self.stay_on_top:
            self.root.attributes('-topmost', True)

    def save_settings(self):
        try:
            settings = {
                "work_time": self.work_time,
                "break_time": self.break_time,
                "long_break_time": self.long_break_time,
                "session_goal": self.session_goal,
                "stay_on_top": self.stay_on_top,
                "auto_start": self.auto_start
            }
            with open(self.config_file, "w") as f:
                json.dump(settings, f)
        except IOError:
            pass

    def setup_ui(self):
        theme = self.themes[self.current_theme]
        
        self.label_status = tk.Label(
            self.root, text="Work Session", font=("Helvetica", 18, "bold"),
            bg=theme["bg"], fg=theme["fg"]
        )
        self.label_status.pack(pady=20)

        # Task Input
        self.task_frame = tk.Frame(self.root, bg=theme["bg"])
        self.task_frame.pack(pady=10)
        
        self.task_label = tk.Label(
            self.task_frame, text="Current Task:", bg=theme["bg"], 
            fg=theme["text_muted"], font=("Helvetica", 10)
        )
        self.task_label.pack()
        
        self.task_entry = tk.Entry(self.task_frame, width=30, justify='center', font=("Helvetica", 12))
        self.task_entry.insert(0, self.placeholder_text)
        self.task_entry.bind("<FocusIn>", self.clear_placeholder)
        self.task_entry.bind("<KeyRelease>", self.update_window_title)
        self.task_entry.pack(pady=5)

        self.btn_clear_task = tk.Button(
            self.task_frame, text="Clear Task", command=self.clear_task,
            font=("Helvetica", 8), bg=theme["accent"], fg=theme["text_muted"],
            relief="flat"
        )
        self.btn_clear_task.pack(pady=2)

        self.label_timer = tk.Label(
            self.root, text="25:00", font=("Helvetica", 48),
            bg=theme["bg"], fg=theme["timer_color"]
        )
        self.label_timer.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=250, mode="determinate")
        self.progress.pack(pady=10)
        self.update_progress()

        self.label_sessions = tk.Label(
            self.root, text=f"Sessions: {self.sessions_completed}/{self.session_goal}", font=("Helvetica", 12),
            bg=theme["bg"], fg=theme["text_muted"]
        )
        self.label_sessions.pack(pady=10)

        # Settings Frame
        self.settings_frame = tk.Frame(self.root, bg=theme["bg"])
        self.settings_frame.pack(pady=20)

        self.set_work_label = tk.Label(self.settings_frame, text="Work (min):", bg=theme["bg"], fg=theme["fg"])
        self.set_work_label.grid(row=0, column=0, padx=5)
        self.work_entry = tk.Entry(self.settings_frame, width=5)
        self.work_entry.insert(0, str(self.work_time // 60))
        self.work_entry.grid(row=0, column=1, padx=5)

        self.set_break_label = tk.Label(self.settings_frame, text="Break (min):", bg=theme["bg"], fg=theme["fg"])
        self.set_break_label.grid(row=1, column=0, padx=5)
        self.break_entry = tk.Entry(self.settings_frame, width=5)
        self.break_entry.insert(0, str(self.break_time // 60))
        self.break_entry.grid(row=1, column=1, padx=5)

        self.set_long_label = tk.Label(self.settings_frame, text="Long Break (min):", bg=theme["bg"], fg=theme["fg"])
        self.set_long_label.grid(row=2, column=0, padx=5)
        self.long_break_entry = tk.Entry(self.settings_frame, width=5)
        self.long_break_entry.insert(0, str(self.long_break_time // 60))
        self.long_break_entry.grid(row=2, column=1, padx=5)

        self.set_goal_label = tk.Label(self.settings_frame, text="Goal (sessions):", bg=theme["bg"], fg=theme["fg"])
        self.set_goal_label.grid(row=3, column=0, padx=5)
        self.goal_entry = tk.Entry(self.settings_frame, width=5)
        self.goal_entry.insert(0, str(self.session_goal))
        self.goal_entry.grid(row=3, column=1, padx=5)

        # Always on top toggle
        self.stay_on_top_var = tk.BooleanVar(value=self.stay_on_top)
        self.chk_topmost = tk.Checkbutton(
            self.settings_frame, text="Always on Top", variable=self.stay_on_top_var,
            bg=theme["bg"], fg=theme["fg"], selectcolor=theme["accent"],
            command=self.toggle_topmost, font=("Helvetica", 9)
        )
        self.chk_topmost.grid(row=4, column=0, columnspan=2, pady=5)

        # Auto-start toggle
        self.auto_start_var = tk.BooleanVar(value=self.auto_start)
        self.chk_autostart = tk.Checkbutton(
            self.settings_frame, text="Auto-start next session", variable=self.auto_start_var,
            bg=theme["bg"], fg=theme["fg"], selectcolor=theme["accent"],
            command=self.toggle_autostart, font=("Helvetica", 9)
        )
        self.chk_autostart.grid(row=5, column=0, columnspan=2, pady=5)

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
            font=("Helvetica", 10), bg=theme["accent"], fg=theme["text_muted"],
            relief="flat"
        )
        self.btn_logs.pack(pady=10)

        # Theme Toggle
        self.btn_theme = tk.Button(
            self.root, text="Switch to Light Mode", command=self.toggle_theme,
            font=("Helvetica", 9), bg=theme["accent"], fg=theme["text_muted"],
            relief="flat"
        )
        self.btn_theme.pack(pady=20)

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        theme = self.themes[self.current_theme]
        
        self.root.configure(bg=theme["bg"])
        self.label_status.config(bg=theme["bg"], fg=theme["fg"])
        self.task_frame.config(bg=theme["bg"])
        self.task_label.config(bg=theme["bg"], fg=theme["text_muted"])
        self.btn_clear_task.config(bg=theme["accent"], fg=theme["text_muted"])
        self.label_timer.config(bg=theme["bg"])
        self.label_sessions.config(bg=theme["bg"], fg=theme["text_muted"])
        self.settings_frame.config(bg=theme["bg"])
        self.set_work_label.config(bg=theme["bg"], fg=theme["fg"])
        self.set_break_label.config(bg=theme["bg"], fg=theme["fg"])
        self.set_long_label.config(bg=theme["bg"], fg=theme["fg"])
        self.set_goal_label.config(bg=theme["bg"], fg=theme["fg"])
        self.chk_topmost.config(bg=theme["bg"], fg=theme["fg"], selectcolor=theme["accent"])
        self.chk_autostart.config(bg=theme["bg"], fg=theme["fg"], selectcolor=theme["accent"])
        self.btn_logs.config(bg=theme["accent"], fg=theme["text_muted"])
        self.btn_theme.config(bg=theme["accent"], fg=theme["text_muted"], 
                            text="Switch to Dark Mode" if self.current_theme == "light" else "Switch to Light Mode")
        
        # Update timer color based on current state
        if self.is_work_session:
            self.label_timer.config(fg=theme["timer_color"])
        else:
            if self.sessions_completed % 4 == 0 and self.sessions_completed > 0:
                self.label_timer.config(fg=theme["long_break_color"])
            else:
                self.label_timer.config(fg=theme["break_color"])

    def clear_placeholder(self, event):
        if self.task_entry.get() == self.placeholder_text:
            self.task_entry.delete(0, tk.END)

    def clear_task(self):
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, self.placeholder_text)
        self.update_window_title()

    def update_window_title(self, event=None):
        task = self.task_entry.get()
        if task == self.placeholder_text or not task.strip():
            task = "Lumina Task Timer"
        else:
            task = f"Lumina - {task}"
        
        if self.is_running:
            mins, secs = divmod(self.current_time, 60)
            self.root.title(f"{task} ({mins:02d}:{secs:02d})")
        else:
            self.root.title(task)

    def toggle_topmost(self):
        self.stay_on_top = self.stay_on_top_var.get()
        self.root.attributes('-topmost', self.stay_on_top)

    def toggle_autostart(self):
        self.auto_start = self.auto_start_var.get()

    def update_progress(self):
        total = self.work_time if self.is_work_session else (self.long_break_time if self.sessions_completed % 4 == 0 and self.sessions_completed > 0 else self.break_time)
        # Progress bar represents time elapsed
        elapsed = total - self.current_time
        percentage = (elapsed / total) * 100 if total > 0 else 0
        self.progress['value'] = percentage

    def apply_settings(self):
        try:
            new_work = int(self.work_entry.get()) * 60
            new_break = int(self.break_entry.get()) * 60
            new_long_break = int(self.long_break_entry.get()) * 60
            new_goal = int(self.goal_entry.get())
            
            if new_work <= 0 or new_break <= 0 or new_long_break <= 0 or new_goal < 0:
                raise ValueError("Time and goals must be positive")

            self.work_time = new_work
            self.break_time = new_break
            self.long_break_time = new_long_break
            self.session_goal = new_goal
            self.stay_on_top = self.stay_on_top_var.get()
            self.auto_start = self.auto_start_var.get()
            self.save_settings()
            
            if not self.is_running:
                # Update current timer display immediately if not running
                if self.is_work_session:
                    self.current_time = self.work_time
                else:
                    self.current_time = self.long_break_time if self.sessions_completed % 4 == 0 and self.sessions_completed > 0 else self.break_time
                
                mins, secs = divmod(self.current_time, 60)
                self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
                self.update_progress()
            
            self.label_sessions.config(text=f"Sessions: {self.sessions_completed}/{self.session_goal}")
            messagebox.showinfo("Settings", "Timer durations and goal updated!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive numbers.")

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
        self.update_window_title()

    def tick(self):
        if self.is_running:
            if self.current_time > 0:
                # Countdown sounds for the last 3 seconds
                if 0 < self.current_time <= 3:
                    self.play_notification_sound(frequency=800, duration=100)
                
                self.current_time -= 1
                mins, secs = divmod(self.current_time, 60)
                time_str = f"{mins:02d}:{secs:02d}"
                self.label_timer.config(text=time_str)
                self.update_window_title()
                self.update_progress()
                self.root.after(1000, self.tick)
            else:
                self.handle_session_complete()

    def play_notification_sound(self, frequency=1000, duration=500):
        if winsound:
            try:
                winsound.Beep(frequency, duration)
            except Exception:
                pass

    def log_session(self):
        task = self.task_entry.get()
        if task == self.placeholder_text or not task.strip():
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
        logs_window.geometry("400x350")
        
        theme = self.themes[self.current_theme]
        logs_window.configure(bg=theme["bg"])

        text_area = tk.Text(logs_window, wrap="word", bg=theme["accent"], fg=theme["fg"], font=("Helvetica", 10))
        text_area.pack(padx=10, pady=10, expand=True, fill="both")

        with open(self.log_file, "r") as f:
            text_area.insert(tk.END, f.read())
        
        text_area.config(state=tk.DISABLED)

        # Clear Logs Button
        btn_clear_logs = tk.Button(
            logs_window, text="Clear All Logs", 
            command=lambda: self.clear_logs(logs_window, text_area),
            font=("Helvetica", 9), bg="#c0392b", fg="white", relief="flat"
        )
        btn_clear_logs.pack(pady=10)

    def clear_logs(self, window, text_area):
        if messagebox.askyesno("Clear Logs", "Are you sure you want to delete all session logs?"):
            try:
                with open(self.log_file, "w") as f:
                    f.write("")
                text_area.config(state=tk.NORMAL)
                text_area.delete(1.0, tk.END)
                text_area.config(state=tk.DISABLED)
                messagebox.showinfo("Logs", "All logs have been cleared.")
            except IOError:
                messagebox.showerror("Error", "Could not clear logs file.")

    def handle_session_complete(self):
        self.is_running = False
        self.is_work_session = not self.is_work_session
        
        theme = self.themes[self.current_theme]
        
        # Visual feedback flash
        original_bg = theme["bg"]
        flash_color = "#f1c40f" if self.current_theme == "dark" else "#f39c12"
        self.root.configure(bg=flash_color)
        self.root.after(200, lambda: self.root.configure(bg=original_bg))

        if self.is_work_session:
            self.current_time = self.work_time
            self.label_status.config(text="Work Session")
            self.label_timer.config(fg=theme["timer_color"])
            msg = "Break over! Time to focus."
        else:
            self.sessions_completed += 1
            self.log_session()
            self.label_sessions.config(text=f"Sessions: {self.sessions_completed}/{self.session_goal}")
            
            if self.sessions_completed % 4 == 0:
                self.current_time = self.long_break_time
                self.label_status.config(text="Long Break Time")
                self.label_timer.config(fg=theme["long_break_color"])
                msg = "Great progress! Take a long break."
            else:
                self.current_time = self.break_time
                self.label_status.config(text="Break Time")
                self.label_timer.config(fg=theme["break_color"])
                msg = "Work session complete! Take a break."

        mins, secs = divmod(self.current_time, 60)
        self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
        self.update_progress()
        self.btn_start.config(text="Start", bg="#27ae60")
        self.update_window_title()
        
        self.play_notification_sound()
        messagebox.showinfo("Timer", msg)
        
        if self.auto_start:
            self.toggle_timer()

if __name__ == "__main__":
    root = tk.Tk()
    app = LuminaTimer(root)
    root.mainloop()