import cv2
import numpy as np
import os
import copy
import socket
import pickle
from collections import Counter


# ================= COLOR CLASSIFICATION (FIXED) =================

def classify_hue(h, s, v):
    # White: low saturation, high brightness
    if s < 40 and v > 180:
        return "W"

    # Yellow
    if 20 <= h <= 35:
        return "Y"

    # Blue
    if 90 <= h <= 130:
        return "B"

    # Red (wraps HSV range)
    if h <= 10 or h >= 170:
        return "R"

    # Green
    if 40 <= h <= 85:
        return "G"

    # Orange
    if 10 < h < 20:
        return "O"

    return "?"   # NEVER default to a color


# ================= UI / OVERLAY HELPERS =================

def get_position_for_move(move, frame_size, image_size):
    if move in ["R", "R'"]:
        return (520, 195)
    elif move in ["L", "L'"]:
        return (200, 195)
    elif move in ["U", "U'"]:
        return (260, 145)
    elif move in ["D", "D'"]:
        return (260, 465)
    else:
        return (250, 240)

def overlay_image(bg, overlay, position):
    h, w = overlay.shape[:2]
    x, y = position
    if overlay.shape[2] == 4:
        alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            bg[y:y+h, x:x+w, c] = (
                (1 - alpha) * bg[y:y+h, x:x+w, c] +
                alpha * overlay[:, :, c]
            )
    else:
        bg[y:y+h, x:x+w] = overlay
    return bg

def draw_arrow_for_move(frame, move):
    image_path = f"Resources/{move}.png"
    if os.path.exists(image_path):
        overlay = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if overlay is not None:
            frame[:] = overlay_image(frame, overlay, get_position_for_move(move, frame.shape[:2], (150, 150)))
    cv2.putText(frame, f"Move: {move}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)


# ================= SOLVER HELPERS =================

def expand_moves(solution_str):
    expanded = []
    for move in solution_str.split():
        if move.endswith("2"):
            expanded.extend([move[0], move[0]])
        else:
            expanded.append(move)
    return expanded

def get_required_presses(move):
    return 2 if move.endswith("2") else 1


# ================= CAMERA + SCANNING =================

cap = cv2.VideoCapture("http://192.168.0.106:8080/video")

GRID_SIZE = 3
SPACING = 160
DOT_RADIUS = 5
face_order = ['U', 'R', 'F', 'D', 'L', 'B']
cube_faces = {}

print("▶️ Press keys: U R F D L B to scan that face")
print("▶️ Press ESC when done")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (750, 640))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    height, width = 640, 750
    center_x, center_y = width // 2, height // 2

    current_face = []

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = center_x + (j - 1) * SPACING
            y = center_y + (i - 1) * SPACING + 50

            h, s, v = hsv[y, x]
            color = classify_hue(h, s, v)
            current_face.append(color)

            cv2.circle(frame, (x, y), DOT_RADIUS, (0, 255, 0), -1)
            cv2.putText(frame, color, (x - 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Cube Scanner", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break
    elif chr(key).upper() in face_order:
        face = chr(key).upper()
        cube_faces[face] = current_face.copy()
        print(f"✅ Scanned {face}:")
        for i in range(0, 9, 3):
            print(current_face[i:i+3])

cap.release()
cv2.destroyAllWindows()


# ================= BUILD & VALIDATE CUBE STRING =================

if len(cube_faces) != 6:
    print("⚠️ Scan all 6 faces!")
    exit()

print("\n🧠 Building cube string...")

# Center-based mapping (CORRECT)
color_to_face = {cube_faces[face][4]: face for face in face_order}

cube_string = ''.join(
    color_to_face.get(color, '?')
    for face in face_order
    for color in cube_faces[face]
)

print("\n🧩 Final cube string:")
print(cube_string)

print("\n🔎 Validation:")
print("Length:", len(cube_string))
print("Counts:", Counter(cube_string))

if len(cube_string) != 54 or '?' in cube_string or any(v != 9 for v in Counter(cube_string).values()):
    print("❌ Invalid cube state. Fix color detection / scanning.")
    exit()


# ================= SOLVE =================

import kociemba

solution = kociemba.solve(cube_string)
print("\n🧩 Solution:")
print(solution)

# Send scanned cube state to the State viewer (if running)
try:
    try:
        sock = socket.create_connection(("localhost", 9999), timeout=2)
        sock.sendall(pickle.dumps(cube_faces))
        sock.close()
        print("✅ Sent cube state to viewer (localhost:9999)")
    except Exception as e:
        print("⚠️ Could not send cube state to viewer:", e)
except Exception:
    pass
