# 📷 SmartVision Alarm
### Computer Vision-Based Intelligent Alarm System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/Tkinter-GUI-0E7490?style=for-the-badge" />
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
</p>

<p align="center">
  <b>An intelligent desktop alarm application that uses image similarity verification to dismiss alarms.</b>
</p>

---

## 📌 Overview

**SmartVision Alarm** is a Python-based desktop application that introduces a computer vision approach to traditional alarm systems.

Unlike conventional alarms that can be dismissed with a single button click, SmartVision Alarm requires users to submit an image similar to a previously selected reference image.

The application verifies the submitted image using three image comparison techniques:

- Perceptual Hashing (pHash)
- Structural Similarity Index (SSIM)
- ORB Feature Matching

Users can complete verification through either an image uploaded from their computer or a live webcam capture.

The application also integrates alarm scheduling, audio playback, a graphical user interface and SQLite-based activity tracking.

## 🎯 Project Objectives

- Develop an interactive desktop alarm application using Python.
- Integrate computer vision techniques for image similarity analysis.
- Support both image upload and live webcam verification.
- Implement automated countdown and alarm management.
- Maintain alarm history using an SQLite database.
- Explore practical applications of image processing in everyday software.

## ✨ Key Features

| Feature | Description |
|---|---|
| 🖼️ Reference Image Selection | Select an image that will be used as the verification reference. |
| ⏱️ Custom Alarm Timer | Set an alarm using a countdown duration in seconds. |
| 📷 Image Upload Verification | Upload an image from your computer for comparison. |
| 🎥 Live Webcam Verification | Capture an image directly using your webcam. |
| 🔍 Perceptual Hashing | Compare images using perceptual hash distance. |
| 🧩 SSIM Analysis | Measure structural similarity between two images. |
| 🎯 ORB Feature Matching | Compare local image features using ORB descriptors. |
| 🔊 Alarm Sound | Play an alarm sound repeatedly until successful verification or cancellation. |
| 🗄️ SQLite Integration | Store alarm details and verification results. |
| 📊 Activity History | View recent alarm records and their statuses. |
| 🎨 Desktop Interface | Dark-themed interface with dashboard cards and navigation controls. |

## 🧠 How Image Verification Works

SmartVision Alarm uses three complementary image comparison techniques to evaluate the similarity between the selected reference image and the submitted candidate image.

### 1. Perceptual Hashing (pHash)

Perceptual hashing generates a compact representation of an image based on its visual characteristics.

- Generates perceptual hashes for both images.
- Calculates the Hamming distance between the hashes.
- A smaller distance indicates greater similarity.

**Current threshold:**

`HASH_MAX_DISTANCE = 12`

### 2. Structural Similarity Index (SSIM)

SSIM evaluates the structural similarity between two images.

It considers similarities in:
- Luminance
- Contrast
- Structural information

The images are converted to grayscale and resized to 320 × 320 pixels before comparison.

**Current threshold:**

`SSIM_MIN_SCORE = 0.62`

A higher SSIM score indicates greater structural similarity.

### 3. ORB Feature Matching

ORB (Oriented FAST and Rotated BRIEF) identifies distinctive keypoints and descriptors in images.

The implementation:
- Detects keypoints using OpenCV ORB.
- Extracts feature descriptors.
- Matches descriptors using a Brute Force Matcher.
- Applies Lowe's ratio test to identify good matches.

**Current configuration:**

- Maximum features: 1200
- Ratio test: 0.75
- Minimum good matches: 10

### 4. Final Verification Decision

The application combines the results of all three techniques.

| Algorithm | Passing condition |
|---|---|
| pHash | Distance ≤ 12 |
| SSIM | Score ≥ 0.62 |
| ORB | Good matches ≥ 10 |

**Decision rule:**

An image is accepted when at least two out of the three verification checks pass.

Otherwise, the submitted image is rejected and the alarm continues ringing.

*Note: These are initial configurable thresholds, not experimentally validated accuracy guarantees. They should be calibrated using different positive and negative image samples.*

## 🔄 Application Workflow

```text
        START APPLICATION
               |
               v
       Select Reference Image
               |
               v
        Set Alarm Duration
               |
               v
          Set Alarm
               |
               v
        Countdown Timer
               |
               v
         Alarm Triggers
               |
               v
       Start Alarm Sound
               |
               v
       Select Verification
          /         \
         /           \
        v             v
   Image Upload    Live Webcam
        |             |
        v             v
   Load Image      Capture Image
         \           /
          \         /
           v       v
       Image Verification
               |
               v
      pHash + SSIM + ORB
               |
               v
       At Least 2 Checks?
          /         \
        YES          NO
         |            |
         v            v
    Stop Alarm    Continue Alarm
         |
         v
    Save Result
         |
         v
    Update History
```

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Tkinter | Graphical user interface |
| OpenCV | Image processing and webcam integration |
| ImageHash | Perceptual hashing |
| Scikit-image | SSIM computation |
| NumPy | Image array processing |
| Pillow | Image loading and display |
| Pygame | Alarm audio playback |
| SQLite | Local database management |

## 📁 Project Structure

```text
SmartVision_Alarm/
│
├── main.py
│
├── requirements.txt
│
├── README.md
│
├── assets/
│   └── alarm.wav
│
├── smartvision/
│   ├── __init__.py
│   ├── alarm_manager.py
│   ├── database.py
│   ├── image_verification.py
│   ├── sound_manager.py
│   └── webcam.py
│
├── .gitignore
│
└── smartvision_alarms.db
    (Generated automatically)
```

### Module Description

**main.py**
- Initializes the desktop application.
- Builds the dashboard and interface.
- Handles reference image selection.
- Manages alarm scheduling and countdown.
- Coordinates image verification.
- Updates alarm history.

**smartvision/alarm_manager.py**
- Manages alarm countdown timing.
- Tracks active alarm information.
- Calculates remaining time.
- Handles alarm state clearing.

**smartvision/image_verification.py**
- Implements pHash comparison.
- Computes SSIM scores.
- Performs ORB feature matching.
- Combines the three verification results.
- Returns a structured verification result.

**smartvision/webcam.py**
- Initializes webcam access.
- Displays live camera preview.
- Captures and saves images.
- Releases camera resources.

**smartvision/sound_manager.py**
- Initializes Pygame audio.
- Loads the alarm sound.
- Plays the sound in a continuous loop.
- Stops audio playback.

**smartvision/database.py**
- Initializes the SQLite database.
- Creates alarm records.
- Updates alarm statuses.
- Stores image verification metrics.
- Retrieves recent alarm history.

## ⚙️ Installation and Setup

### Prerequisites

- Windows 10 or Windows 11
- Python 3.10 (recommended)
- Visual Studio Code or another Python IDE
- Working webcam for live verification
- Speakers or headphones for alarm playback

### Step 1: Clone the Repository

```bash
git clone https://github.com/KatepalliYasaswy/SmartVision-Alarm.git
```

### Step 2: Navigate to the Project Folder

```bash
cd SmartVision-Alarm
```

### Step 3: Create a Virtual Environment

```bash
py -3.10 -m venv .venv
```

### Step 4: Activate the Environment

```powershell
.venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Run the Application

```bash
python main.py
```

## 📦 Dependencies

The project uses the following Python libraries:

```text
Pillow>=10.0.0
opencv-python>=4.8.0
ImageHash>=4.3.1
scikit-image>=0.22.0
pygame>=2.5.0
numpy>=1.24.0
```

All dependencies are listed in `requirements.txt`.

## 🖥️ How to Use

**Step 1 – Launch the Application**

Run `main.py` to open the SmartVision Alarm dashboard.

**Step 2 – Select a Reference Image**

Click **Choose Reference Image** and select an image from your computer.

**Step 3 – Configure the Alarm**

Enter the desired alarm duration in seconds.

**Step 4 – Set the Alarm**

Click **Set Alarm** to start the countdown.

**Step 5 – Wait for the Alarm**

When the countdown reaches zero, the alarm sound starts playing.

**Step 6 – Verify Your Image**

Choose either:

- **Verify with Image Upload:** Select a similar image from your computer.
- **Verify with Webcam:** Open the live camera window and capture an image.

**Step 7 – View the Verification Result**

The application evaluates the submitted image using pHash, SSIM and ORB.

If at least two checks pass, the alarm stops and the result is recorded.

If verification fails, the alarm continues ringing.

## 🗄️ Database Design

SmartVision Alarm uses SQLite for local alarm record management.

The database is automatically initialized when the application starts.

**Database:** `smartvision_alarms.db`

**Table:** `alarms`

| Column | Description |
|---|---|
| id | Unique alarm identifier |
| reference_image | Selected reference image path |
| duration_seconds | Configured alarm duration |
| created_at | Alarm creation timestamp |
| triggered_at | Alarm trigger timestamp |
| stopped_at | Alarm stop or cancellation timestamp |
| status | Scheduled, Ringing, Stopped or Cancelled |
| verification_method | Image Upload or Webcam |
| hash_distance | Perceptual hash distance |
| ssim_score | Structural similarity score |
| orb_matches | Number of good ORB matches |
| verification_message | Verification result message |

The database stores alarm activity locally on the user's computer.

## 🔐 Privacy and Security

- Image comparison is performed locally.
- No cloud image upload or remote image processing is implemented.
- Alarm records are stored in a local SQLite database.
- Webcam access is requested through the local computer's camera interface.
- Captured images are saved locally as `captured_image.jpg`.

**Privacy note:** Reference images and captured images remain on the local machine unless the user separately shares them.

## ⚠️ Limitations

- The application currently supports one active alarm at a time.
- Image similarity does not establish the identity of a person.
- A similar uploaded photograph can potentially pass verification.
- Verification results may vary depending on lighting, image quality, camera angle, distance and object positioning.
- The current thresholds are configurable and require further experimentation.
- The alarm is a desktop prototype and is not a guaranteed wake-up or safety device.
- Alarm scheduling is managed during the running application; persistent recovery of scheduled alarms after restarting the application is not implemented.

## 🚀 Future Enhancements

The following features are potential future improvements:

- [ ] Advanced image verification and geometric feature validation.
- [ ] Experimental evaluation of verification accuracy.
- [ ] Adjustable verification sensitivity.
- [ ] Persistent alarm scheduling across application restarts.
- [ ] Multiple alarm profiles.
- [ ] Detailed verification analytics dashboard.
- [ ] Enhanced alarm history and statistics.
- [ ] Custom alarm sound selection.
- [ ] Improved UI animations and personalization.
- [ ] Additional computer vision techniques.

## 🎓 Learning Outcomes

Developing SmartVision Alarm provides practical experience in:

- Python modular programming.
- Computer vision and image processing.
- Image similarity measurement.
- Feature detection and matching.
- Real-time webcam integration.
- Desktop GUI development.
- SQLite database operations.
- Event-driven programming and countdown management.
- Integration of multiple Python libraries into one application.

## 👩‍💻 Developer

**Yasaswy Katepalli**

Computer Science Undergraduate | Data Science

Interested in Data Analytics, Artificial Intelligence, Machine Learning and Computer Vision.

<p align="center">
  <a href="https://github.com/KatepalliYasaswy">GitHub</a> •
  <a href="https://www.linkedin.com/in/katepalli-yasaswy/">LinkedIn</a> •
  <a href="mailto:katepalli555@gmail.com">Email</a>
</p>

---

<p align="center">
  <b>SmartVision Alarm</b>
  <br/>
  Turning Computer Vision into Practical Everyday Applications.
  <br/><br/>
  ⭐ If you find this project interesting, consider giving the repository a star!
</p>
