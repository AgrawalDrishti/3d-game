import imgui
import numpy as np
from utils.graphics import Object, Camera, Shader
from assets.shaders.shaders import object_shader , lighting_shader
from assets.objects.objects import  get_planet , get_space_station , get_transporter , rotation_matrix
import random
from OpenGL.GL import *

class Game:
    def __init__(self, height, width, gui):
        self.gui = gui
        self.height = height
        self.width = width
        self.screen = 0
        self.shaders = [Shader(lighting_shader["vertex_shader"], lighting_shader["fragment_shader"])]
        self.objects = {}
    

    def InitScene(self):
        if self.screen == 1:

            def setCamera():
                self.camera = Camera(self.height, self.width)
                self.camera.position = np.array([0, 0, 1], dtype=np.float32)
                self.camera.lookAt = np.array([0, 0, -1], dtype=np.float32)
                self.camera.up = np.array([0, 1, 0], dtype=np.float32)
                self.camera.fov = 45
                self.camera.near = 1.0
                self.camera.far = 10000.0
                
            setCamera()
            ############################################################################

            def setWorldLimits():
                self.worldMin = np.array([-5000, -5000, -5000], dtype=np.float32)
                self.worldMax = np.array([5000, 5000, 5000], dtype=np.float32)
            setWorldLimits()

            ############################################################################

            

            ############################################################################

            # Initialize Planets and space stations (Randomly place n planets and n spacestations within world bounds)
            self.n_planets = 10 # for example

            self.objects["planets"] = []
            for i in range(self.n_planets):
                bottom_color = np.array([random.random(), random.random(), random.random()])
                top_color = np.array([random.random(), random.random(), random.random()])

                planet = get_planet(bottom_color , top_color)  # get default planet properties with gradient colors
                # Set a random position: x in [-300,300], y in [-300,300], z in [-150, -30]
                
                if "normals" not in planet:
                    n_vertices = len(planet["vertices"]) // 3
                    # Create a flat array of n_vertices copies of (0, 0, 1)
                    default_normals = np.tile(np.array([0, 0, 1], dtype=np.float32), n_vertices)
                    planet["normals"] = default_normals

                pos = np.array([
                    np.random.uniform(-50, 50),
                    np.random.uniform(-50, 50),
                    np.random.uniform(-150, -40)
                ], dtype=np.float32)

                planet["position"] = pos
                # Optionally, set a random uniform scale between 0.5 and 2.0
                scale_val = 5.0
                planet["scale"] = np.array([scale_val, scale_val, scale_val], dtype=np.float32)
                # Create the planet object and add it to the list
                self.objects["planets"].append(Object(None, self.shaders[0], planet))
            

            self.objects["stations"] = []
            for planet_obj in self.objects.get("planets", []):
                station = get_space_station()

                if "normals" not in station:
                    n_vertices = len(station["vertices"]) // 3
                    station["normals"] = np.tile(np.array([0, 0, 1], dtype=np.float32), n_vertices)
                
                orbit_radius = 10.0  # Adjust as needed
                orbit_angle = random.uniform(0, 2 * np.pi)
                # inclination = random.uniform(-np.radians(60), np.radians(60))  # Adjust as needed
    
                # Compute the initial offset based on orbit_radius and orbit_angle.
                offset = np.array([
                    orbit_radius * np.cos(orbit_angle) ,
                    0,
                    orbit_radius * np.sin(orbit_angle)  # For simplicity, keep z offset zero. Adjust if needed.
                ], dtype=np.float32)

                # Tie the station to its planet: the orbit center is the planet's position.
                orbit_center = planet_obj.properties["position"].copy()
                
                station["orbitCenter"] = planet_obj.properties["position"].copy()

                station["position"] = orbit_center + offset
                # Store the orbital properties using our custom keys.
                station["rotation_radius"] = orbit_radius
                station["init_position"] = orbit_center.copy()
                # Also store the current orbit angle in the Z rotation component.
                station["rotation"] =  np.array([0, 0, orbit_angle], dtype=np.float32)
                station["scale"] = np.array([0.7, 0.7, 0.7], dtype=np.float32)
                self.objects["stations"].append(Object(None, self.shaders[0], station))
                
                # Optionally, make the station smaller.
                
                # Create the station object and add it to our stations list.
                # self.objects["stations"].append(Object(None, self.shaders[0], station))

            ############################################################################
            # Initialize transporter (Randomly choose start and end planet, and initialize transporter at start planet)
            
            self.objects["transporter"] = None
            transporter = get_transporter()
            transporter["position"] = np.array([0, -1.5, -5], dtype=np.float32)
            transporter["scale"] = np.array([0.15, 0.15, 0.15], dtype=np.float32)
            # transporter["rotation"] = np.array([0 , np.pi/2, np.pi/2], dtype=np.float32)
            self.objects["transporter"] = Object(None, self.shaders[0], transporter)
            
            # self.objects["transporter"] = None
            # if len(self.objects["planets"]) > 0:
            #     # Pick the first planet (or choose randomly).
            #     source_planet = self.objects["planets"][0]
            #     transporter = get_transporter()
            #     # Position the transporter at a fixed offset from the planet (e.g., slightly above it).
            #     transporter["position"] = source_planet.properties["position"] + np.array([0, 0, 5], dtype=np.float32)
            #     # Set an appropriate scale for the transporter.
            #     transporter["scale"] = np.array([2, 2.5, 2.5], dtype=np.float32)
            #     self.objects["transporter"] = Object(None, self.shaders[0], transporter)


            ############################################################################
            # Initialize Pirates (Spawn at random locations within world bounds)
            self.n_pirates = 20 # for example

            ############################################################################
            # Initialize minimap arrow (Need to write orthographic projection shader for it)

            ############################################################################

    def ProcessFrame(self, inputs, time):
        self.DrawText()
        self.UpdateScene(inputs, time)
        self.DrawScene()

    def DrawText(self):
        if self.screen == 0: # Example start screen
            window_w, window_h = 400, 200  # Set the window size
            x_pos = (self.width - window_w) / 2
            y_pos = (self.height - window_h) / 2

            imgui.new_frame()
            # Centered window
            imgui.set_next_window_position(x_pos, y_pos)
            imgui.set_next_window_size(window_w, window_h)
            imgui.begin("Main Menu", False, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)

            # Center text horizontally
            imgui.set_cursor_pos_x((window_w - imgui.calc_text_size("Press 1: New Game")[0]) / 2)
            imgui.text("Press 1: New Game")

            imgui.end()

            imgui.render()
            self.gui.render(imgui.get_draw_data())

        if self.screen == 2: # YOU WON Screen
            pass

        if self.screen == 3: # GAME OVER Screen
            pass
        
    def UpdateScene(self, inputs, time):
        if self.screen == 1: # Game screen
            ############################################################################

            # Update each space station's orbital motion.
            # angular_speed = 0.5  # radians per second (adjust as needed)
            # delta = time["deltaTime"]
            delta = time["deltaTime"]
            theta = 0.4 * delta  # Increment per frame.

            for station_obj in self.objects.get("stations", []):
                # Update the Z-axis rotation (which we use as the orbital angle).
                station_obj.properties["rotation"][2] += theta
                # Retrieve orbit parameters.
                radius = station_obj.properties["rotation_radius"]
                center = station_obj.properties["init_position"]
                # Compute new position in the X-Y plane.
                station_obj.properties["position"][0] = center[0] + radius * np.cos(station_obj.properties["rotation"][2])
                station_obj.properties["position"][1] = center[1] + radius * np.sin(station_obj.properties["rotation"][2])
                # Keep the Z position the same as the orbit center (or offset it slightly if desired).
                station_obj.properties["position"][2] = center[2]

            if self.objects.get("transporter") is not None:
                transporter = self.objects["transporter"]
                if "orientation" not in transporter.properties:
                    t_rot = transporter.properties["rotation"]
                    transporter.properties["orientation"] = rotation_matrix(t_rot[0], t_rot[1], t_rot[2])
                
                # Get current orientation.
                current_orient = transporter.properties["orientation"]

                # t_rot = self.objects["transporter"].properties["rotation"]
                rotation_speed = 0.5  # radians per second
                dR = np.eye(3, dtype=np.float32)
                if inputs.get("W"):
                    dR = dR @ rotation_matrix(rotation_speed * delta, 0, 0)[:3, :3]  # pitch down
                if inputs.get("S"):
                    dR = dR @ rotation_matrix(-rotation_speed * delta, 0, 0)[:3, :3]  # pitch up
                if inputs.get("A"):
                    dR = dR @ rotation_matrix(0, rotation_speed * delta, 0)[:3, :3]  # yaw left
                if inputs.get("D"):
                    dR = dR @ rotation_matrix(0, -rotation_speed * delta, 0)[:3, :3]  # yaw right
                if inputs.get("Q"):
                    dR = dR @ rotation_matrix(0, 0, rotation_speed * delta)[:3, :3]  # roll left
                if inputs.get("E"):
                    dR = dR @ rotation_matrix(0, 0, -rotation_speed * delta)[:3, :3]  # roll right

                new_orient = current_orient @ dR
                transporter.properties["orientation"] = new_orient

                max_speed = 10.0    # maximum speed
                # Initialize velocity if not already present.
                vel = transporter.properties.get("velocity", np.array([0, 0, 0], dtype=np.float32))
                if inputs.get("SPACE"):
                    forward = new_orient @ np.array([0, 0, -1], dtype=np.float32)
                    # vel += delta * forward
                    # speed = np.linalg.norm(vel)
                    transporter.properties["speed"] += 0.05

                    if transporter.properties["speed"] > max_speed:
                        transporter.properties["speed"] = max_speed

                    transporter.properties["velocity"] = transporter.properties["speed"] * forward

                    
                else:
                    # If SPACE is not pressed, immediately set velocity to zero.
                    transporter.properties["speed"] = 0.0
                    transporter.properties["velocity"] = np.array([0, 0, 0], dtype=np.float32)
                # Update transporter position based on velocity.
                transporter.properties["position"] += transporter.properties["velocity"] * delta
            
            # Manage inputs 
            
            ############################################################################
            # Update transporter (Update velocity, position, and check for collisions)
           

            ############################################################################
            # Update spacestations (Update velocity and position to revolve around respective planet)
            

            ############################################################################
            # Update Minimap Arrow: (Set direction based on transporter velocity direction and target direction)
            

            ############################################################################
            # Update Lasers (Update position of any currently shot lasers, make sure to despawn them if they go too far to save computation)
           
            
            ############################################################################
            # Update Pirates (Write logic to update their velocity based on transporter position, and check for collision with laser or transporter)
            

            ############################################################################
            # Update Camera (Check for view (3rd person or 1st person) and set position and LookAt accordingly)
            

            ############################################################################
            pass
        
        elif self.screen == 0: # Example start screen
            self.screen = 1
            self.InitScene()

        elif self.screen == 2: # YOU WON
            pass
        elif self.screen == 3: # GAME OVER
            pass
    
    def DrawScene(self):
        if self.screen == 1: 
            ######################################################
            # Example draw statements
            
            for shader in (self.shaders):
                self.camera.Update(shader)
                lightPosLocation = glGetUniformLocation(shader.ID, "lightPos".encode('utf-8'))
                glUniform3f(lightPosLocation, 100.0, 100.0, 100.0)
                viewPosLocation = glGetUniformLocation(shader.ID, "viewPos".encode('utf-8'))
                glUniform3f(viewPosLocation, self.camera.position[0], self.camera.position[1], self.camera.position[2])
                glUniform1f(glGetUniformLocation(shader.ID, "ambientStrength".encode('utf-8')), 0.3)
                glUniform1f(glGetUniformLocation(shader.ID, "specularStrength".encode('utf-8')), 0.8)
                glUniform1f(glGetUniformLocation(shader.ID, "shininess".encode('utf-8')), 64.0)

            for planet_obj in self.objects.get("planets", []):
                planet_obj.Draw()
            
            for station_obj in self.objects.get("stations", []):
                station_obj.Draw()
            
            if self.objects.get("transporter") is not None:
                self.objects["transporter"].Draw()

            # self.gameState["transporter"].Draw()
            # self.gameState["stars"].Draw()
            # self.gameState["arrow"].Draw()

            # if self.gameState["transporter"].properties["view"] == 2: # Conditionally draw crosshair
            #     self.gameState["crosshair"].Draw()

            # for laser in self.gameState["lasers"]:
            #     laser.Draw()
            # for planet in self.gameState["planets"]:
            #     planet.Draw()
            # for spaceStation in self.gameState["spaceStations"]:
            #     spaceStation.Draw()
            # for pirate in self.gameState["pirates"]:
            #     pirate.Draw()
            ######################################################
            pass
