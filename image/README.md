# Traffic Camera Speed Detection with YOLOv8

A Python script for real-time vehicle detection, tracking, and speed estimation from traffic camera footage using YOLOv8 object detection and Bird's Eye View (BEV) perspective transformation.

## Features

- **Vehicle Detection**: Detects cars, motorcycles, buses, and trucks using YOLOv8
- **Multi-Object Tracking**: Tracks vehicles across frames using ByteTrack
- **Speed Estimation**: Calculates real-time vehicle speeds in km/h with smoothing
- **Dual-Lane Support**: Handles bidirectional traffic with separate calibration for each direction
- **Bird's Eye View**: Perspective transformation for accurate distance measurements
- **Visual Output**: Color-coded speed indicators and bounding boxes
- **Data Logging**: Exports vehicle tracking data to CSV format

## Requirements

```bash
pip install opencv-python numpy ultralytics
```

Or use the provided requirements file:

```bash
pip install -r requirements.txt
```

## Quick Start

1. Place your input video as `input.mp4` in the same directory
2. Run the script:
   ```bash
   python CameraComputervisionYOLOv8python-ai.py
   ```
3. Find results:
   - Annotated video: `output.mp4`
   - Speed log: `speed_log.csv`

## Configuration

### Video Files
Edit these variables at the top of the script:
```python
VIDEO_IN = "input.mp4"   # Input video file
VIDEO_OUT = "output.mp4" # Output video file
```

### Model Settings
```python
MODEL_PATH = "yolov8n.pt"  # YOLO model (auto-downloaded if missing)
conf = 0.35                # Detection confidence threshold
iou = 0.45                 # IoU threshold for NMS
```

### Road Calibration (Customize for your camera)

**Left-side road** (traffic toward camera):
```python
NUM_LANES_LEFT = 5         # Number of lanes
SRC_ROAD_L = np.float32([
    [155, 415],  # far-left (distant)
    [600, 395],  # far-right (distant)
    [845, 1079], # near-right (close)
    [0, 1079]    # near-left (close)
])
```

**Right-side road** (traffic away from camera):
```python
NUM_LANES_RIGHT = 3
SRC_ROAD_R = np.float32([
    [600, 395],   # far-left
    [1140, 395],  # far-right
    [1220, 1079], # near-right
    [900, 1079]   # near-left
])
```

### Speed Parameters
```python
LANE_WIDTH_M = 3.75         # Standard lane width in metres
VISIBLE_LENGTH_M = 70       # Visible road length in metres
DEV_SCALE = 18              # Pixels per metre scaling factor
MIN_TRACK_FRAMES = 8        # Frames before showing speed (stability)
MAX_PLAUSIBLE_KPH = 200     # Maximum reasonable speed
MIN_PLAUSIBLE_KPH = 2       # Minimum speed threshold
```

### Speed Colors
```python
SPEED_GREEN = 60    # Green threshold (km/h)
SPEED_YELLOW = 100  # Yellow threshold (km/h)
# Above 100 km/h = Red
```

## Calibration Guide

To calibrate for your camera angle:

1. **Identify lane boundaries** in your video frame
2. **Measure real-world dimensions**:
   - Lane width (typically 3.75m for highways)
   - Visible road length
3. **Define source points** (`SRC_ROAD_L`/`SRC_ROAD_R`) as trapezoid corners:
   - Order: far-left, far-right, near-right, near-left
4. **Adjust `DEV_SCALE`** until distance measurements match reality

## Output

### Video Output
- **Green box**: < 60 km/h
- **Yellow box**: 60-100 km/h
- **Red box**: > 100 km/h
- Speed bar shows relative speed
- Label shows vehicle type and speed

### CSV Log (`speed_log.csv`)
| Column | Description |
|--------|-------------|
| TrackID | Unique tracking ID |
| Class | Vehicle type (Car/Motorcycle/Bus/Truck) |
| Frames | Number of frames tracked |
| AvgSpeed(kph) | Average speed |
| MaxSpeed(kph) | Maximum speed recorded |

## Vehicle Classes Detected

| COCO ID | Class |
|---------|-------|
| 2 | Car |
| 3 | Motorcycle |
| 5 | Bus |
| 7 | Truck |

## Technical Details

### Speed Calculation
1. Transform 2D bounding box centers to Bird's Eye View coordinates
2. Calculate displacement between first and current frame
3. Convert pixel distance to metres using scale factor
4. Speed = distance / time × 3.6 (m/s to km/h)
5. Apply moving average smoothing (25-frame window)

### Tracking
- Uses ByteTrack for robust multi-object tracking
- Minimum 8 frames before displaying speed (reduces false positives)
- Tracks persist across frames with unique IDs

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing video | Ensure `input.mp4` exists in script directory |
| Inaccurate speeds | Recalibrate `SRC_ROAD_*` points and `DEV_SCALE` |
- Too many detections | Increase `conf` threshold |
| Vehicles not tracked | Check `bytetrack.yaml` exists in Ultralytics installation |
| Poor detection at night | Try YOLOv8n-seg or use a model trained on night footage |

## License

This project uses:
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - AGPL-3.0
- [OpenCV](https://opencv.org/) - Apache-2.0
- [ByteTrack](https://github.com/ifzhang/ByteTrack) - MIT

## Author

Created for traffic analysis and speed monitoring applications.
