# Dorm Layout Studio
**Author:** Joseph Ouyang

---

Dorm Layout Studio is an interactive 2D room designer built for the CMU 15-112 course environment. Users choose between three preset room layouts inspired by real McGill House and Morewood Gardens floor plans, then furnish and arrange their space using a drag-and-drop palette. Measurement tools, placement validation, and full undo/redo support make the design process practical and intuitive.

---

## Table of Contents
- [Features](#features)
- [Room Layouts](#room-layouts)
- [Controls](#controls)
- [Getting Started](#getting-started)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)

---

## Features

### Furniture Placement
Drag any item from the palette on the right side of the screen into the room to place it. A quick click without dragging will not keep the piece. Once furniture is in the room, clicking a piece selects it for dragging or rotation.

### Placement Validation
While a piece is selected, a colored ghost rectangle is drawn over it at all times:

| Ghost Color | Meaning |
|---|---|
| Green | Valid placement: fully inside the room and not overlapping other furniture |
| Red | Invalid placement: outside the room boundary or overlapping another piece |

If a newly spawned piece is released in an invalid position, it is removed. If an existing piece is dragged to an invalid position and released, it snaps back to its original location, size, and orientation.

### Measurement Mode
Click the RULER panel in the bottom-left corner to enter measurement mode, indicated by a green border. In measurement mode:

- The first click inside the room sets the start point
- The second click sets the end point and saves the measurement segment
- A live preview line updates continuously as the mouse moves
- All distances are converted from pixels to real-world feet and inches based on the selected layout's known dimensions

Press `esc` or click the X on the RULER panel to exit measurement mode at any time.

### Undo and Redo
A snapshot-based history system tracks all furniture moves, rotations, deletions, and measurement segments.

| Action | Keyboard | Button |
|---|---|---|
| Undo | `z` | Left arrow under "Back to Layouts" |
| Redo | `y` | Right arrow under "Back to Layouts" |

Undo and redo buttons are grayed out when no action is available in that direction.

### Trash
Drag any furniture piece over the trash can in the bottom-right corner and release to delete it. Deletions are tracked in the undo history.

---

## Room Layouts

Three preset layouts are available at the layout selection screen, each with doors, windows, and labeled dimension lines in feet and inches drawn to scale.

| Layout | Inspiration | Default Furniture |
|---|---|---|
| Single | McGill House single | 1 bed, 1 closet, 1 desk |
| Double | Morewood Gardens double | 2 beds, 2 closets, 2 desks |
| Triple | Morewood Gardens triple | 3 beds, 3 closets, 2 desks |

Each layout loads with a default furniture arrangement that can be freely rearranged or cleared.

---

## Controls

| Input | Action |
|---|---|
| Click and drag from palette | Place new furniture in the room |
| Click a placed piece | Select it |
| Drag a selected piece | Move it |
| `r` | Rotate selected piece 90 degrees clockwise |
| `z` | Undo |
| `y` | Redo |
| `esc` | Exit measurement mode |
| Drag piece to trash | Delete piece |
| Click RULER panel | Toggle measurement mode |

---

## Getting Started

**Requirements:**

- Python 3.10 or later
- `cmu_graphics` module (provided in the 15-112 course environment)
- `cmu_cpcs_utils` module (included in this repository)

**Run the app:**

```bash
python dorm_layout_studio.py
```

The app opens on a Home screen. Click "Let's Design!" to proceed to layout selection, choose a room type, and begin designing. From the design screen, click "Back to Layouts" to return to layout selection.

---

## Tech Stack

| Tool | Use |
|---|---|
| Python 3.10+ | Primary language |
| cmu_graphics | Rendering, event handling, and animation via the 15-112 graphics framework |
| cmu_cpcs_utils | Course utility functions |

---

## Repository Structure

```
dorm-layout-studio/
├── dorm_layout_studio.py    # main application
├── cmu_cpcs_utils.py        # course utility module
├── cmu_graphics/            # graphics framework
├── media_uploads/           # furniture and UI images
└── README.md
```

---

*Built for 15-112 Fundamentals of Programming and Computer Science, Carnegie Mellon University.*
