import cv2
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk


class WebcamCapture:
    """Live webcam preview with a one-click capture action."""

    BG = "#111C2E"
    PANEL = "#1C2B40"
    ACCENT = "#536DFE"
    MUTED = "#B7C3D4"

    def __init__(self, parent, on_capture):
        self.parent = parent
        self.on_capture = on_capture
        self.window = tk.Toplevel(parent)
        self.window.title("SmartVision | Live camera")
        self.window.geometry("760x610")
        self.window.configure(bg=self.BG)
        self.window.resizable(False, False)

        tk.Label(
            self.window, text="LIVE CAMERA VERIFICATION",
            bg=self.BG, fg="white", font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", padx=22, pady=(18, 3))
        tk.Label(
            self.window, text="Position the reference object in the camera frame, then capture.",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", padx=22, pady=(0, 14))

        preview_frame = tk.Frame(self.window, bg=self.PANEL, highlightbackground="#34465F", highlightthickness=1)
        preview_frame.pack(fill="both", expand=True, padx=22, pady=(0, 14))
        self.preview = tk.Label(
            preview_frame, text="Starting camera...",
            bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 10)
        )
        self.preview.pack(fill="both", expand=True, padx=8, pady=8)

        controls = tk.Frame(self.window, bg=self.BG)
        controls.pack(pady=(0, 18))
        self.capture_button = tk.Button(
            controls, text="◎   Capture image", command=self.capture,
            bg=self.ACCENT, fg="white", activebackground="#4058E8",
            activeforeground="white", relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 10, "bold"), padx=22, pady=11
        )
        self.capture_button.pack(side="left", padx=7)
        tk.Button(
            controls, text="Close", command=self.close,
            bg=self.PANEL, fg="white", activebackground="#2B3D55",
            activeforeground="white", relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 10, "bold"), padx=22, pady=11
        ).pack(side="left", padx=7)

        self.cap = cv2.VideoCapture(0)
        self.current_frame = None
        self.closed = False

        if not self.cap.isOpened():
            messagebox.showerror("Camera error", "Could not access the webcam. Check camera permissions.")
            self.close()
            return

        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.update_frame()

    def update_frame(self):
        if self.closed:
            return
        ok, frame = self.cap.read()
        if ok:
            self.current_frame = frame.copy()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb)
            image.thumbnail((700, 450))
            self.photo = ImageTk.PhotoImage(image)
            self.preview.configure(image=self.photo, text="")
        self.window.after(30, self.update_frame)

    def capture(self):
        if self.current_frame is None:
            messagebox.showwarning("Camera", "No camera frame is available yet.")
            return
        path = Path(__file__).resolve().parent.parent / "captured_image.jpg"
        if not cv2.imwrite(str(path), self.current_frame):
            messagebox.showerror("Camera", "Could not save the captured image.")
            return
        self.close()
        self.on_capture(str(path))

    def close(self):
        if self.closed:
            return
        self.closed = True
        if self.cap is not None:
            self.cap.release()
        try:
            self.window.destroy()
        except tk.TclError:
            pass
