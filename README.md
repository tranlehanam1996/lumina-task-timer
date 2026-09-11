# Lumina Task Timer

Lumina Task Timer is a simple, distraction-free Pomodoro timer application designed to help you stay focused and maintain a healthy work-break balance.

## Features
- **Work Intervals**: Default 25-minute focus sessions.
- **Break Intervals**: Default 5-minute recovery breaks.
- **Long Breaks**: Automatically scheduled every 4 work sessions (default 15 min).
- **Task Tracking**: Set a specific task to focus on and log completed sessions.
- **Visual Feedback**: Color-coded timer based on the current session state and a real-time progress bar.
- **Theme Support**: Toggle between light and dark modes for comfortable viewing.
- **Simple Controls**: Start, Pause, and Reset functionality, including an Enter key shortcut to toggle the timer.

## Installation

Lumina is built using Python and requires the `tkinter` library (which comes pre-installed with most Python distributions).

1. Clone this repository:
   ```bash
   git clone https://github.com/tranlehanam1996/lumina-task-timer.git
   ```
2. Navigate to the directory:
   ```bash
   cd lumina-task-timer
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## How to Use
1. Launch the app.
2. (Optional) Enter your current task in the input field.
3. Click **Start** (or press **Enter**) to begin your work session.
4. When the timer hits zero, you will be notified to take a break.
5. The timer will automatically switch between Work and Break modes.
6. Use the **View Logs** button to see your productivity history.