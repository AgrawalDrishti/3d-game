# Space Heist Game

**Space Heist** is an immersive 3D space adventure game where you pilot a transporter spacecraft to reach a destination space station while evading pirates. Navigate your vessel through an expansive galaxy, and switch between two distinct views—third-person and first-person—to complete your mission.

---

## Getting Started
1. **Launch the Game:**  
   Run the `main.py` file to start the game.

2. **Game States:**
   - **Start Screen:** Choose to start or exit the game.
   - **Gameplay:** Navigate your transporter towards the destination.
   - **Game Won:** Displays when you successfully reach the destination space station.
   - **Game Over:** Displays if a pirate collides with your transporter.

---

## Controls and Navigation

### General Controls
- **W:** Pitch Down  
- **S:** Pitch Up  
- **A:** Yaw Left  
- **D:** Yaw Right  
- **Q:** Roll Left  
- **E:** Roll Right  
- **Space Bar:** Accelerate forward

### View Modes
- **Toggle View:**  
  - **Right Mouse Button:** Switch between Third-Person and First-Person views.
  
### Third-Person View
- **Description:**  
  In this mode, you directly maneuver the transporter using the keyboard controls. The ship rotates according to your inputs, and the camera follows from behind. The transporter automatically moves towards the destination space station.
  
### First-Person View
- **Description:**  
  In first-person view, the transporter’s orientation remains fixed. Instead, you control the camera’s look direction with the mouse.  
- **Aim and Shoot:**  
  - A crosshair appears at the center of the screen.
  - Move the mouse to adjust your aim.
  - Use the left mouse button to fire lasers at approaching pirates.
- **Movement:**  
  Although you cannot steer the spacecraft in first-person mode, you can still accelerate forward using the Space Bar.

---

## Additional Features

### Minimap
- **Location:**  
  Displayed at the bottom left corner of the screen.
- **Functionality:**  
  The minimap provides guidance by indicating the relative elevation difference between your transporter and the destination:
  - **Red:** Destination is higher.
  - **Blue:** Destination is lower.
  - **Yellow:** Nearly equal elevation.

### Laser Blaster
- **First-Person Mode:**  
  In first-person view, use the left mouse button to shoot lasers. Aim with the mouse and destroy incoming pirates before they collide with your transporter.

---

## Game Outcome

- **Game Won:**  
  When your transporter successfully reaches the destination space station, the game transitions to the "Game Won" screen.
- **Game Over:**  
  If a pirate collides with your transporter, the game transitions to the "Game Over" screen.
