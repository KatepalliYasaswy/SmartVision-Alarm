# SmartVision Alarm

A polished desktop alarm application based on the original **Alarm by Image** idea, with a midnight-blue navigation rail, clean dashboard cards, quick countdown presets and recent activity table.

Before setting an alarm, select a reference image. When the timer expires, the alarm rings. Dismiss it by either:
- selecting a similar image from your computer, or
- capturing a fresh image using your webcam.

The verification module compares the candidate image with the reference using:
1. Average/perceptual hash distance (ImageHash)
2. SSIM (structural similarity)
3. ORB feature matching (OpenCV)

The default decision rule accepts an image when **at least two of the three checks pass**. These thresholds are configurable in `smartvision/image_verification.py` and should be calibrated using your own test images.

## Requirements

- Windows 10/11
- Python 3.10 recommended
- A working webcam for camera capture
- Speakers/headphones for alarm sound

## Setup (Windows / VS Code)

Open PowerShell in the `SmartVision_Alarm` folder.

```powershell
py -3.10 -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

If `py -3.10` is unavailable, use `python -m venv .venv` with your installed Python version.

## How to use

1. Click **Choose Reference Image** and select a clear image of an object or scene.
2. Enter the alarm duration in seconds.
3. Click **Set Alarm**.
4. When the countdown finishes, the alarm sound starts.
5. Click **Verify with Image Upload** to choose a similar image, or **Verify with Webcam** to capture one.
6. The application evaluates the image. If at least two checks pass, the alarm stops and the result is saved. If verification fails, the alarm keeps ringing.

## Project structure

```text
SmartVision_Alarm/
├── main.py
├── requirements.txt
├── README.md
├── assets/
│   └── alarm.wav
└── smartvision/
    ├── __init__.py
    ├── alarm_manager.py
    ├── database.py
    ├── image_verification.py
    ├── sound_manager.py
    └── webcam.py
```

## Important notes

- This is a desktop prototype, not a medical or guaranteed wake-up device.
- Image similarity cannot prove that the user physically got out of bed.
- Camera capture can be affected by lighting, angle, distance and camera quality.
- Keep the reference image and candidate image reasonably similar in framing.
- The webcam preview is local; images are not uploaded to a server.
- The app supports one active alarm at a time. Alarm history is stored in `smartvision_alarms.db`.
- `assets/alarm.wav` is generated as a simple tone and can be replaced with your own sound file (keep the same filename).
