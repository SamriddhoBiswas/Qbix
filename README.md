# 🧊 Rubik’s Cube Solver using Computer Vision & Python

A real-time **Rubik’s Cube Solver** that uses your webcam to:

1. Scan each face of a real cube  
2. Classify sticker colors with HSV thresholds  
3. Solve the cube using the [Kociemba two-phase algorithm](https://github.com/hkociemba/RubiksCube-TwophaseSolver)  
4. Guide you through each move with 2D overlays and a separate viewer  

---

## 🎥 Features

- **Webcam scanning** of all 6 faces  
- **HSV-based color classification**  
- **Kociemba solver** via the `kociemba` Python package  
- **Arrow overlays** for visual move guidance  
- **Real-time state tracking** after every move  
- **Separate viewer window** rendering the cube state via sockets  

---

## 🧰 Tech Stack & Libraries

- **Python 3.10.8**  
- **[OpenCV](https://opencv.org/)** – Camera capture, image display, overlays  
- **[NumPy](https://numpy.org/)** – Numerical operations  
- **[kociemba](https://pypi.org/project/kociemba/)** – Cube solving algorithm  

---

## 📁 Project Structure

```
rubiks-cube-solver/
│
├── main.py       # Main script: scanning, solving & overlay guidance  
├── state.py      # Viewer script: renders current cube state  
├── resources/    # Static assets
│   ├── colors/   # PNG tiles for each sticker color (W, Y, R, O, G, B)
│   ├── U.png      # Arrow overlay images for each move (e.g., U, R, F, etc.)
│   └── …          # Other move arrow PNGs  
└── README.md     # This file  
```
---
