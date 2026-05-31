from collections import defaultdict, deque
import csv
import math
import cv2
import numpy as np
from ultralytics import YOLO

LOG_CSV = "speed_log.csv"
MODEL_PATH = "yolov8n.pt"
VIDEO_IN = "input.mp4"
VIDEO_OUT = "output.mp4"

VEHICLE_CLASSES = {2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}

LANE_WIDTH_M = 3.75 # metres per lane
NUM_LANES_LEFT = 5  # lanes on the left (traffic toward camera)
NUM_LANES_RIGHT = 3  # lanes on the right (traffic going into tunnel)
ROAD_WIDTH_L_M = LANE_WIDTH_M * NUM_LANES_LEFT # = 18.75 m
ROAD_WIDTH_R_M = LANE_WIDTH_M * NUM_LANES_RIGHT # = 11.25 m

DEV_SCALE = 18 # px / m

VISIBLE_LENGTH_M = 70 # metres

SRC_ROAD_L = np.float32([
    [155, 415], # far-left (distant, left kerb)
    [600, 395], # far-right (distant, centre divider)
    [845, 1079], # near-right (close, centre divider)
    [0, 1079] # near-left (close, left kerb)
])

SRC_ROAD_R = np.float32([
    [600, 395], # far-left (distant, centre divider)
    [1140, 395], # far-right (distant, right kerb)
    [1220, 1079], # near-right (close, right kerb)
    [900, 1079] # near-left (close, centre divider)
])

MIN_TRACK_FRAMES = 8 # frames a vehicle must be tracked before showing speed
HISTORY_LEN = 25 # how many recent per-frame speeds to average
MAX_PLAUSIBLE_KPH = 200 # discard obviously wrong estimates (occlusions, etc.)
MIN_PLAUSIBLE_KPH = 2 # ignore near-zero (parked / just detected)

SPEED_GREEN = 60
SPEED_YELLOW =  100

def build_bev_transform(src_pts, road_width_m, visible_length_m, dev_scale):
    """Return (M, Minv, bev_h) for a perspective -> bird's eye wrap."""
    bev_w = int(road_width_m * dev_scale)
    bev_h = int(visible_length_m * dev_scale)       
    dst = np.float32([
        [0, 0], # far-left (distant, left kerb)
        [bev_w, 0], # far-right (distant, right kerb)
        [bev_w, bev_h], # near-right (close, right kerb)
        [0, bev_h] # near-left (close, left kerb)
    ])
    M = cv2.getPerspectiveTransform(src_pts, dst)
    Minv = cv2.getPerspectiveTransform(dst, src_pts)
    return M, Minv, bev_h

def to_bev(M, pt):
    """Transform a single (x, y) image point  to bird's eye coordinates."""
    p = np.float32([[pt[0], pt[1]]]) 
    t = cv2.perspectiveTransform(p, M)
    return float(t[0][0][0]), float(t[0][0][1])



def bev_dist_to_meters(dx_px, dy_px, dev_scale):
    """Convert a distance in bird's eye pixels to metres."""
    return math.hypot(dx_px, dy_px) / dev_scale

def speed_color(kph):
    """Return a color for the given speed."""
    if kph < SPEED_GREEN:
        return (0, 220, 0) # green
    elif kph < SPEED_YELLOW:
        return (0, 200, 255) # yellow
    else:
        return (0, 50, 255) # red
    
def draw_label(frame, text, pos, color, font_scale=0.6, thickness=1):
    """Draw text with a colored background."""
    x, y = int(pos[0]), int(pos[1])
    (tw, th), baseline = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    pad = 4
    cv2.rectangle(frame,
                (x - pad, y - th - pad),
                (x + tw + pad, y + baseline + pad),
                (20, 20, 20), -1)
    cv2.putText(frame, text, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness,
                cv2.LINE_AA)
    
def draw_dashed_line(frame, pt1, pt2, color, thickness=1, dash_length=10):
    """Draw a horizontal dashed line across the frame."""
    x1, y1 = pt1
    x2, y2 = pt2
    dash_len = dash_length
    for x in range(x1, x2, dash_len * 2):
        x_end = min(x + dash_len, x2)
        cv2.line(frame, (x, y1), (x_end, y1), color, thickness)

def main():
    cap = cv2.VideoCapture(VIDEO_IN)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video '{VIDEO_IN}'. "
                                "Make sure it is in the same folder as this script.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video: {VIDEO_IN} ({width}x{height} @ {fps:.1f} fps | {total} frames | "
          f"{total/fps:.1f} seconds)")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(VIDEO_OUT, fourcc, fps, (width, height))

    ML, MLinv, bev_hL = build_bev_transform(
        SRC_ROAD_L, ROAD_WIDTH_L_M, VISIBLE_LENGTH_M, DEV_SCALE)
    MR, MRinv, bev_hR = build_bev_transform(
        SRC_ROAD_R, ROAD_WIDTH_R_M, VISIBLE_LENGTH_M, DEV_SCALE)

model = YOLO(MODEL_PATH)
print(f"Loaded model '{MODEL_PATH}'")

bev_history = defaultdict(lambda: deque(maxlen=HISTORY_LEN + 1))
track_history = defaultdict(lambda: deque(maxlen=HISTORY_LEN))
track_frames = defaultdict(int)
track_classes = {}
track_max_kph = defaultdict(float)
track_kph_sum = defaultdict(float)
track_kph_cnt = defaultdict(int)
speed_smooth = defaultdict(lambda: deque(maxlen=HISTORY_LEN))

frame_idx = 0
dt = 1.0 / fps # time per frame in seconds

print("Processing frames...")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_idx += 1
    if frame_idx % 10 == 0:
        print(f"Frame {frame_idx}/{total} ({frame_idx/fps:.1f}s)")

    results = model(
        frame, 
        persist=True,
        tracker="bytetrack.yaml",
        classes=list(VEHICLE_CLASSES.keys()),
        conf=0.35,
        iou=0.45,
        verbose=False,
    )
    
    if results[0].boxes is None or results[0].boxes.id is None:
        out.write(frame)
        continue
    
    boxes = results[0].boxes.cpu().numpy() # [N, 4]
    ids = results[0].boxes.id.cpu().numpy() # [N]
    clss = results[0].boxes.cls.cpu().numpy() # [N]
    confs = results[0].boxes.conf.cpu().numpy() # [N]

    for box, tid, cls_id, conf in zip(boxes, ids, clss, confs):
        tid = int(tid)
        cls_id = int(cls_id)
        cls_name = VEHICLE_CLASSES.get(cls_id, "Vehicle")
        track_classes[tid] = cls_name
        track_frames[tid] += 1

        x1, y1, x2, y2 = box
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        use_left = cx < (width / 2 + 80)  # left road (width slight overlap)
        M_use = ML if use_left else MR
        scale_x = DEV_SCALE

        kph = None
        if len(bev_history[tid]) > 0:
            bx0, by0, fi0 = bev_history[tid][0]
            bx1, by1, fil = bev_history[tid][-1]
            n_frames = fil - fi0
            if n_frames > 0:
                dist_m = bev_dist_to_meters(bx1 - bx0, by1 - by0, scale_x)
                elapsed_s = n_frames * dt
                raw_kph = (dist_m / elapsed_s) * 3.6

                if MIN_PLAUSIBLE_KPH < raw_kph < MAX_PLAUSIBLE_KPH:
                    speed_smooth[tid].append(raw_kph)
                    kph = np.mean(speed_smooth[tid])
                    track_kph_sum[tid] += kph
                    track_kph_cnt[tid] += 1
                    track_max_kph[tid] = max(track_max_kph[tid], kph)

        show_speed = (kph is not None and
                     track_frames[tid] >= MIN_TRACK_FRAMES)
        color = speed_color(kph) if show_speed else (180, 180, 180)

        cv2.rectangle(frame,
                    (int(x1), int(y1)), (int(x2), int(y2)),
                    color, 2)
        if show_speed:
            label = f"{cls_name} ({kph:.0f} km/h)"
        else:
            label = cls_name

        draw_label(frame, label, (x1, y1 - 6), color)

        if show_speed:
            bar_max = SPEED_YELLOW
            bar_frac = min(kph / bar_max, 1.0)
            bar_len = int((x2 - x1) * bar_frac)
            bar_y = int(y2) + 5
            cv2.rectangle(frame, (int(x1), bar_y),
                         (int(x1) + bar_len, bar_y + 5),
                          color, -1)

        # Store BEV position
        bev_x, bev_y = to_bev(M_use, (cx, cy))
        bev_history[tid].append((bev_x, bev_y, frame_idx))

    cv2.putText(frame,
                f"Frame {frame_idx}/{total} | ({frame_idx/fps:.1f}s)",
                (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                (200, 220, 220), 1, cv2.LINE_AA)
    for i, (label, color) in enumerate([
        ("<60 km/h", (0, 220, 0)),
        ("60-100 km/h", (0, 200, 255)),
        (">100 km/h", (0, 50, 255))
    ]):
        y_leg = height - 80 + i * 26
        cv2.rectangle(frame,
                       (12, y_leg - 14), (32, y_leg + 4),
                         color, -1)
        cv2.putText(frame, label,
                     (38, y_leg) , cv2.FONT_HERSHEY_DUPLEX,
                    0.55, (230, 230, 230), 1, cv2.LINE_AA)
    out.write(frame)

cap.release()
out.release()
print(f"\n Done! Output saved to '{VIDEO_OUT}'")

with open(LOG_CSV, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["TrackID", "Class", "Frames", "AvgSpeed(kph)", "MaxSpeed(kph)"])
    for tid in sorted(track_classes.keys()):
        avg_kph = track_kph_sum[tid] / track_kph_cnt[tid] if track_kph_cnt[tid] > 0 else 0
        writer.writerow([
            tid,
            track_classes.get(tid, "Unknown"),
            track_frames[tid],
            round(avg_kph, 2),
            round(track_max_kph[tid], 1),
        ])
    print(f"Speed log saved to '{LOG_CSV}'")

if __name__ == "__main__":
    main()