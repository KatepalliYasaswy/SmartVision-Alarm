import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading

from PIL import Image, ImageTk

from smartvision.alarm_manager import AlarmManager
from smartvision.database import (
    initialize_database,
    create_alarm,
    update_alarm_triggered,
    update_alarm_stopped,
    update_alarm_cancelled,
    get_recent_alarms,
)
from smartvision.image_verification import compare_images
from smartvision.sound_manager import SoundManager
from smartvision.webcam import WebcamCapture


BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"
SOUND_PATH = ASSET_DIR / "alarm.wav"


class SmartVisionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartVision Alarm")
        self.root.geometry("820x720")
        self.root.minsize(760, 650)
        self.root.configure(bg="#eef3f8")

        initialize_database()
        self.alarm_manager = AlarmManager()
        self.sound = SoundManager(str(SOUND_PATH))

        self.reference_path = None
        self.reference_photo = None
        self.alarm_is_ringing = False
        self.verification_busy = False
        self.current_alarm_id = None

        self.build_ui()
        self.refresh_history()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.tick()

    def build_ui(self):
        header = tk.Frame(self.root, bg="#17324d", height=82)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="SMARTVISION ALARM",
            font=("Segoe UI", 21, "bold"), fg="white", bg="#17324d"
        ).pack(anchor="w", padx=24, pady=(13, 0))
        tk.Label(
            header, text="Wake up. Find it. Capture it. Start your day.",
            font=("Segoe UI", 10), fg="#d7e5f2", bg="#17324d"
        ).pack(anchor="w", padx=26)

        body = tk.Frame(self.root, bg="#eef3f8")
        body.pack(fill="both", expand=True, padx=22, pady=16)

        left = tk.Frame(body, bg="white", highlightbackground="#d8e1eb", highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = tk.Frame(body, bg="white", highlightbackground="#d8e1eb", highlightthickness=1, width=270)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(left, text="1. Choose your reference image", bg="white",
                 fg="#17324d", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=(18, 8))

        self.image_preview = tk.Label(left, text="No reference image selected",
                                      bg="#f3f6fa", fg="#718096", width=42, height=12)
        self.image_preview.pack(padx=18, pady=4, fill="x")

        tk.Button(left, text="Choose Reference Image", command=self.choose_reference,
                  bg="#2864a5", fg="white", activebackground="#1f5289",
                  relief="flat", font=("Segoe UI", 10, "bold"), padx=12, pady=9).pack(pady=10)

        tk.Label(left, text="2. Set alarm duration", bg="white",
                 fg="#17324d", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=(12, 6))
        duration_row = tk.Frame(left, bg="white")
        duration_row.pack(anchor="w", padx=18)
        self.duration_entry = tk.Entry(duration_row, font=("Segoe UI", 12), width=12, relief="solid", bd=1)
        self.duration_entry.insert(0, "30")
        self.duration_entry.pack(side="left", ipady=5)
        tk.Label(duration_row, text="seconds", bg="white", fg="#526273",
                 font=("Segoe UI", 10)).pack(side="left", padx=8)

        self.set_alarm_button = tk.Button(
            left, text="Set Alarm", command=self.set_alarm,
            bg="#16845b", fg="white", activebackground="#116b49",
            relief="flat", font=("Segoe UI", 11, "bold"), padx=20, pady=10
        )
        self.set_alarm_button.pack(anchor="w", padx=18, pady=14)

        self.countdown_label = tk.Label(left, text="No alarm scheduled",
                                        bg="white", fg="#526273", font=("Segoe UI", 12, "bold"))
        self.countdown_label.pack(anchor="w", padx=18, pady=(2, 8))

        self.status_label = tk.Label(left, text="Choose a reference image to begin.",
                                     bg="white", fg="#526273", font=("Segoe UI", 10),
                                     wraplength=430, justify="left")
        self.status_label.pack(anchor="w", padx=18, pady=(0, 16))

        tk.Label(right, text="ALARM VERIFICATION", bg="white", fg="#17324d",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=16, pady=(18, 10))

        self.ringing_label = tk.Label(right, text="Alarm is not ringing",
                                      bg="#f3f6fa", fg="#526273", font=("Segoe UI", 10, "bold"),
                                      wraplength=220, pady=12)
        self.ringing_label.pack(fill="x", padx=14, pady=4)

        self.upload_button = tk.Button(
            right, text="Verify with Image Upload", command=self.verify_upload,
            state="disabled", bg="#2864a5", fg="white", relief="flat",
            font=("Segoe UI", 9, "bold"), padx=8, pady=10
        )
        self.upload_button.pack(fill="x", padx=14, pady=(12, 7))

        self.camera_button = tk.Button(
            right, text="Verify with Webcam", command=self.open_webcam,
            state="disabled", bg="#2864a5", fg="white", relief="flat",
            font=("Segoe UI", 9, "bold"), padx=8, pady=10
        )
        self.camera_button.pack(fill="x", padx=14, pady=7)

        self.cancel_button = tk.Button(
            right, text="Cancel Scheduled Alarm", command=self.cancel_alarm,
            state="disabled", bg="#a33a3a", fg="white", relief="flat",
            font=("Segoe UI", 9, "bold"), padx=8, pady=9
        )
        self.cancel_button.pack(fill="x", padx=14, pady=(7, 18))

        tk.Label(right, text="Verification rule", bg="white", fg="#17324d",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=(10, 4))
        tk.Label(
            right, text="At least 2 of 3 checks must pass:\n• Perceptual hash\n• SSIM\n• ORB feature matches",
            bg="white", fg="#526273", justify="left", font=("Segoe UI", 9)
        ).pack(anchor="w", padx=16)

        history_frame = tk.Frame(self.root, bg="white", highlightbackground="#d8e1eb", highlightthickness=1)
        history_frame.pack(fill="x", padx=22, pady=(0, 16))
        tk.Label(history_frame, text="Recent alarm history", bg="white", fg="#17324d",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(10, 5))

        columns = ("id", "created", "duration", "status", "method")
        self.history_table = ttk.Treeview(history_frame, columns=columns, show="headings", height=5)
        headings = {"id": "ID", "created": "Created", "duration": "Duration (s)",
                    "status": "Status", "method": "Verification"}
        widths = {"id": 45, "created": 190, "duration": 100, "status": 100, "method": 130}
        for col in columns:
            self.history_table.heading(col, text=headings[col])
            self.history_table.column(col, width=widths[col], anchor="center")
        self.history_table.pack(fill="x", padx=12, pady=(0, 10))

    def choose_reference(self):
        path = filedialog.askopenfilename(
            title="Select reference image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if not path:
            return
        try:
            image = Image.open(path).convert("RGB")
            image.thumbnail((420, 210))
            self.reference_photo = ImageTk.PhotoImage(image)
            self.image_preview.configure(image=self.reference_photo, text="", height=210)
            self.reference_path = path
            self.status_label.configure(text=f"Reference image selected: {Path(path).name}")
        except Exception as exc:
            messagebox.showerror("Image Error", f"Could not open this image.\n{exc}")

    def set_alarm(self):
        if self.alarm_manager.active or self.alarm_is_ringing:
            messagebox.showwarning("Alarm Active", "Only one alarm can be active at a time.")
            return
        if not self.reference_path:
            messagebox.showwarning("Missing Image", "Please choose a reference image first.")
            return
        try:
            duration = int(self.duration_entry.get().strip())
            if duration <= 0:
                raise ValueError
            if duration > 86400:
                messagebox.showwarning("Duration", "Please set a duration of 24 hours or less.")
                return
        except ValueError:
            messagebox.showwarning("Invalid Duration", "Enter a whole number of seconds greater than zero.")
            return

        alarm_id = create_alarm(self.reference_path, duration)
        self.current_alarm_id = alarm_id
        self.alarm_manager.start(alarm_id, duration)
        self.cancel_button.configure(state="normal")
        self.set_alarm_button.configure(state="disabled")
        self.status_label.configure(text=f"Alarm #{alarm_id} scheduled.")
        self.refresh_history()

    def tick(self):
        if self.alarm_manager.active:
            remaining = self.alarm_manager.remaining_seconds()
            self.countdown_label.configure(text=f"Time remaining: {remaining} second(s)")
            if self.alarm_manager.is_finished():
                self.trigger_alarm()
        self.root.after(250, self.tick)

    def trigger_alarm(self):
        alarm_id = self.alarm_manager.alarm_id
        self.alarm_manager.clear()
        self.alarm_is_ringing = True
        update_alarm_triggered(alarm_id)
        self.sound.play_loop()
        self.ringing_label.configure(text="ALARM IS RINGING", fg="#b3261e", bg="#fdecea")
        self.status_label.configure(text="Time is up! Upload a similar image or capture one using your webcam.")
        self.upload_button.configure(state="normal")
        self.camera_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.countdown_label.configure(text="Alarm is ringing!")
        self.refresh_history()

    def verify_upload(self):
        if not self.alarm_is_ringing or self.verification_busy:
            return
        path = filedialog.askopenfilename(
            title="Choose a similar image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if path:
            self.run_verification(path, "Image upload")

    def open_webcam(self):
        if not self.alarm_is_ringing or self.verification_busy:
            return
        WebcamCapture(self.root, lambda path: self.run_verification(path, "Webcam"))

    def run_verification(self, candidate_path, method):
        self.verification_busy = True
        self.upload_button.configure(state="disabled")
        self.camera_button.configure(state="disabled")
        self.status_label.configure(text="Comparing images... please wait.")

        def worker():
            try:
                result = compare_images(self.reference_path, candidate_path)
                self.root.after(0, lambda: self.finish_verification(result, method))
            except Exception as exc:
                self.root.after(0, lambda error=str(exc): self.verification_error(error))

        threading.Thread(target=worker, daemon=True).start()

    def finish_verification(self, result, method):
        self.verification_busy = False
        details = (
            f"{result.message}\n"
            f"Hash distance: {result.hash_distance} (pass: {result.hash_passed})\n"
            f"SSIM: {result.ssim_score:.3f} (pass: {result.ssim_passed})\n"
            f"ORB matches: {result.orb_good_matches} (pass: {result.orb_passed})"
        )
        if result.accepted:
            self.sound.stop()
            update_alarm_stopped(self.current_alarm_id, method, result)
            self.alarm_is_ringing = False
            self.upload_button.configure(state="disabled")
            self.camera_button.configure(state="disabled")
            self.ringing_label.configure(text="Alarm successfully stopped", fg="#137547", bg="#e7f5ed")
            self.status_label.configure(text=details)
            self.countdown_label.configure(text="Alarm stopped.")
            self.set_alarm_button.configure(state="normal")
            messagebox.showinfo("Verification Successful", details)
        else:
            self.upload_button.configure(state="normal")
            self.camera_button.configure(state="normal")
            self.ringing_label.configure(text="Verification failed - still ringing", fg="#b3261e", bg="#fdecea")
            self.status_label.configure(text=details)
            messagebox.showwarning("Try Again", details + "\n\nThe alarm will continue ringing.")
        self.refresh_history()

    def verification_error(self, error):
        self.verification_busy = False
        self.upload_button.configure(state="normal")
        self.camera_button.configure(state="normal")
        self.status_label.configure(text=f"Verification error: {error}")
        messagebox.showerror("Verification Error", error)

    def cancel_alarm(self):
        if self.alarm_manager.active and self.current_alarm_id is not None:
            if messagebox.askyesno("Cancel Alarm", "Cancel the scheduled alarm?"):
                update_alarm_cancelled(self.current_alarm_id)
                self.alarm_manager.clear()
                self.current_alarm_id = None
                self.set_alarm_button.configure(state="normal")
                self.cancel_button.configure(state="disabled")
                self.countdown_label.configure(text="Alarm cancelled.")
                self.status_label.configure(text="Scheduled alarm cancelled.")
                self.refresh_history()

    def refresh_history(self):
        for item in self.history_table.get_children():
            self.history_table.delete(item)
        for row in get_recent_alarms():
            created = row["created_at"].replace("T", " ")
            method = row["verification_method"] or "-"
            self.history_table.insert(
                "", "end",
                values=(row["id"], created, row["duration_seconds"], row["status"], method)
            )

    def on_close(self):
        if self.alarm_manager.active or self.alarm_is_ringing:
            if not messagebox.askyesno("Exit SmartVision", "An alarm is active. Exit anyway?"):
                return
            if self.current_alarm_id and self.alarm_manager.active:
                update_alarm_cancelled(self.current_alarm_id)
        self.sound.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartVisionApp(root)
    root.mainloop()
