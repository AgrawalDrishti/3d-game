#game..py
import imgui
import numpy as np
from utils.graphics import Object, Camera, Shader
from assets.shaders.shaders import object_shader , lighting_shader
from assets.objects.objects import  get_planet , get_space_station , get_transporter , rotation_matrix , get_pirate
import random
from OpenGL.GL import *
import copy

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
                self.camera.position = np.array([0, 0, 0], dtype=np.float32)
                self.camera.lookAt = np.array([0, 0, -1], dtype=np.float32)
                self.camera.up = np.array([0, 1, 0], dtype=np.float32)
                self.camera.fov = 45
                self.camera.near = 1.0
                self.camera.far = 10000.0
                
            setCamera()

            def setWorldLimits():
                self.worldMin = np.array([-5000, -5000, -5000], dtype=np.float32)
                self.worldMax = np.array([5000, 5000, 5000], dtype=np.float32)
            setWorldLimits()

            self.n_planets = 20 # for example

            self.objects["planets"] = []
            for i in range(self.n_planets):
                bottom_color = np.array([random.random(), random.random(), random.random()])
                top_color = np.array([random.random(), random.random(), random.random()])

                planet = get_planet(bottom_color , top_color)  
                
                if "normals" not in planet:
                    n_vertices = len(planet["vertices"]) // 3
                    default_normals = np.tile(np.array([0, 0, 1], dtype=np.float32), n_vertices)
                    planet["normals"] = default_normals

                pos = np.array([
                    np.random.uniform(-200, 200),
                    np.random.uniform(-200, 200),
                    np.random.uniform(-200, 200)
                ], dtype=np.float32)

                planet["position"] = pos
                scale_val = 5.0
                planet["scale"] = np.array([scale_val, scale_val, scale_val], dtype=np.float32)
                self.objects["planets"].append(Object(None, self.shaders[0], planet))
            
            # Select a destination planet (randomly for now)
            if len(self.objects["planets"]) > 0:
                self.destination_planet = random.choice(self.objects["planets"])
                print("Destination planet position:", self.destination_planet.properties["position"])

            self.objects["stations"] = []
            for planet_obj in self.objects.get("planets", []):
                station = get_space_station()

                if "normals" not in station:
                    n_vertices = len(station["vertices"]) // 3
                    station["normals"] = np.tile(np.array([0, 0, 1], dtype=np.float32), n_vertices)
                
                orbit_radius = 10.0  # Adjust as needed
                orbit_angle = random.uniform(0, 2 * np.pi)
    
                offset = np.array([
                    orbit_radius * np.cos(orbit_angle) ,
                    0,
                    orbit_radius * np.sin(orbit_angle) 
                ], dtype=np.float32)

                orbit_center = planet_obj.properties["position"].copy()
                
                station["orbitCenter"] = planet_obj.properties["position"].copy()

                station["position"] = orbit_center + offset
                station["rotation_radius"] = orbit_radius
                station["init_position"] = orbit_center.copy()
                station["rotation"] =  np.array([0, 0, orbit_angle], dtype=np.float32)
                station["scale"] = np.array([0.7, 0.7, 0.7], dtype=np.float32)
                self.objects["stations"].append(Object(None, self.shaders[0], station))

            # Initialize transporter and set its starting position on a randomly chosen source station.
            if len(self.objects["stations"]) >= 2:
                indices = list(range(len(self.objects["stations"])))
                source_index = random.choice(indices)
                indices.remove(source_index)
                destination_index = random.choice(indices)
            else:
                source_index = 0
                destination_index = 0

            print(f"Source index: {source_index}, Destination index: {destination_index}")

            source_station = self.objects["stations"][source_index]
            destination_station = self.objects["stations"][destination_index]

            # Store the destination for later use
            self.destination_station = destination_station

            # self.objects["transporter"] = None
            transporter = get_transporter()
            transporter["position"] = copy.deepcopy(source_station.properties["position"])+ np.array([0, -1.0, 0], dtype=np.float32)
            print("Source station position: ", source_station.properties["position"])
            print("Transporter position: ", transporter["position"])
            print("Destination station position: ", destination_station.properties["position"])
            transporter["scale"] = np.array([0.2, 0.2, 0.2], dtype=np.float32)
            self.objects["transporter"] = Object(None, self.shaders[0], transporter)
            
            self.n_pirates = 20 # for example

            # After you've created stations and the transporter, create a pirate list.
            self.objects["pirates"] = []
            for i in range(self.n_pirates):
                pirate = get_pirate()
                
                pos = np.array([
                    np.random.uniform(-100, 100),
                    np.random.uniform(-100, 100),
                    np.random.uniform(-100, 100)
                ], dtype=np.float32)

                pirate["position"] = pos
                # Optionally scale the pirate smaller or bigger
                pirate["scale"] = np.array([1, 1, 1], dtype=np.float32)

                speed = 15
                direction = np.random.uniform(-1, 1, size=3)
                direction_norm = np.linalg.norm(direction)
                if direction_norm > 0:
                    direction = direction / direction_norm  # normalize
                pirate["velocity"] = direction * speed
                pirate_obj = Object(None, self.shaders[0], pirate)
                self.objects["pirates"].append(pirate_obj)

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

            if imgui.button("Start Game" , 395 , 80):
                self.screen = 1
                self.InitScene()
            if imgui.button("Exit" , 395 , 80):
                exit(0)  # Alternatively, use sys.exit(0) if you import sys

            imgui.end()

            imgui.render()
            self.gui.render(imgui.get_draw_data())

        if self.screen == 2:  # YOU WON Screen
            window_w, window_h = 400, 200  # Set the window size for the Game Won screen
            x_pos = (self.width - window_w) / 2
            y_pos = (self.height - window_h) / 2

            imgui.new_frame()
            imgui.set_next_window_position(x_pos, y_pos)
            imgui.set_next_window_size(window_w, window_h)
            imgui.begin("Game Won", False, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)
            
            # Center the "GAME WON" text horizontally.
            imgui.set_cursor_pos_x((window_w - imgui.calc_text_size("GAME WON")[0]) / 2)
            imgui.text("GAME WON")
            
            # Add a "Back to Menu" button.
            if imgui.button("Back to Menu", 395, 80):
                self.screen = 0   # Go back to the start menu screen
            
            imgui.end()
            imgui.render()
            self.gui.render(imgui.get_draw_data())


        if self.screen == 3:  # GAME OVER Screen
            window_w, window_h = 400, 200  # Set the window size for the Game Over screen
            x_pos = (self.width - window_w) / 2
            y_pos = (self.height - window_h) / 2

            imgui.new_frame()
            imgui.set_next_window_position(x_pos, y_pos)
            imgui.set_next_window_size(window_w, window_h)
            imgui.begin("Game Over", False, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)
            
            # Center the "GAME OVER" text horizontally.
            imgui.set_cursor_pos_x((window_w - imgui.calc_text_size("GAME OVER")[0]) / 2)
            imgui.text("GAME OVER")
            
            # Add a "Back to Menu" button.
            if imgui.button("Back to Menu", 395, 80):
                self.screen = 0   # Go back to the start menu screen
            
            imgui.end()
            imgui.render()
            self.gui.render(imgui.get_draw_data())

            
        
    def UpdateScene(self, inputs, time):
        if self.screen == 1: 
            # angular_speed = 0.5  # radians per second (adjust as needed)
            # delta = time["deltaTime"]
            delta = time["deltaTime"]
            theta = 0.4 * delta  # Increment per frame.

            for station_obj in self.objects.get("stations", []):
                station_obj.properties["rotation"][2] += theta
                radius = station_obj.properties["rotation_radius"]
                center = station_obj.properties["init_position"]
                station_obj.properties["position"][0] = center[0] + radius * np.cos(station_obj.properties["rotation"][2])
                station_obj.properties["position"][1] = center[1] + radius * np.sin(station_obj.properties["rotation"][2])
                station_obj.properties["position"][2] = center[2]
            
            # Update pirates so that they chase the transporter
            if self.objects.get("pirates") is not None and self.objects.get("transporter") is not None:
                transporter_pos = self.objects["transporter"].properties["position"]
                chase_speed = 7.0  # Set a constant speed for chasing; adjust as needed.
                for pirate_obj in self.objects.get("pirates", []):
                    pirate_pos = pirate_obj.properties["position"]
                    # Compute direction from pirate to transporter
                    direction = transporter_pos - pirate_pos
                    norm = np.linalg.norm(direction)
                    if norm > 0:
                        direction = direction / norm  # Normalize
                    else:
                        direction = np.array([0, 0, 0], dtype=np.float32)
                    # Set the pirate's velocity towards the transporter
                    pirate_obj.properties["velocity"] = direction * chase_speed
                    # Update the pirate's position based on the new velocity
                    pirate_obj.properties["position"] += pirate_obj.properties["velocity"] * delta

            if self.objects.get("transporter") is not None and self.objects.get("pirates") is not None:
                transporter_pos = self.objects["transporter"].properties["position"]
                collision_threshold = 2.0  # Adjust threshold as needed for your models
                for pirate_obj in self.objects["pirates"]:
                    pirate_pos = pirate_obj.properties["position"]
                    if np.linalg.norm(transporter_pos - pirate_pos) < collision_threshold:
                        print("Collision detected! Game Over.")
                        self.screen = 3  # Set game over state
                        break

            if self.objects.get("transporter") is not None:
                transporter = self.objects["transporter"]
                if "orientation" not in transporter.properties:
                    t_rot = transporter.properties["rotation"]
                    transporter.properties["orientation"] = rotation_matrix(t_rot[0], t_rot[1], t_rot[2])
                
                current_orient = transporter.properties["orientation"]

                rotation_speed = 0.5  # radians per second
                dR = np.eye(3, dtype=np.float32)
                if inputs.get("W"): dR = dR @ rotation_matrix(rotation_speed * delta, 0, 0)[:3, :3]  # pitch down
                if inputs.get("S"): dR = dR @ rotation_matrix(-rotation_speed * delta, 0, 0)[:3, :3]  # pitch up
                if inputs.get("A"): dR = dR @ rotation_matrix(0, rotation_speed * delta, 0)[:3, :3]  # yaw left
                if inputs.get("D"): dR = dR @ rotation_matrix(0, -rotation_speed * delta, 0)[:3, :3]  # yaw right
                if inputs.get("Q"): dR = dR @ rotation_matrix(0, 0, rotation_speed * delta)[:3, :3]  # roll left
                if inputs.get("E"): dR = dR @ rotation_matrix(0, 0, -rotation_speed * delta)[:3, :3]  # roll right

                new_orient = current_orient @ dR
                transporter.properties["orientation"] = new_orient

                max_speed = 10.0 

                forward_spaceship = new_orient @ np.array([0, 0, -1], dtype=np.float32)
                up_spaceship = new_orient @ np.array([0, 1, 0], dtype=np.float32)

                if inputs.get("SPACE"):
                    transporter.properties["speed"] += 0.05
                    if transporter.properties["speed"] > max_speed:
                        transporter.properties["speed"] = max_speed

                    transporter.properties["velocity"] = transporter.properties["speed"] * forward_spaceship
                else:
                    transporter.properties["speed"] = 0.0
                    transporter.properties["velocity"] = np.array([0, 0, 0], dtype=np.float32)

                transporter.properties["position"] += transporter.properties["velocity"] * delta
            
                self.camera.lookAt = forward_spaceship
                self.camera.up = up_spaceship
                self.camera.position = copy.deepcopy(transporter.properties["position"]) - (5*forward_spaceship) + (up_spaceship)

                dest_pos = self.destination_planet.properties["position"]
                transport_pos = transporter.properties["position"]
                distance_to_destination = np.linalg.norm(dest_pos - transport_pos)
                if distance_to_destination < 5.0:
                    print("Game Won! Distance:", distance_to_destination)
                    self.screen = 2  # Switch to game-won screen
            
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
            if inputs["1"]:
                self.screen = 1
                self.InitScene()

        elif self.screen == 2: # YOU WON
            pass
        elif self.screen == 3: # GAME OVER
            pass
    
    def DrawScene(self):
        if self.screen == 1: 

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
            
            for pirate_obj in self.objects.get("pirates", []):
                pirate_obj.Draw()


            # START ImGui rendering properly (BEFORE any ImGui drawing)
            imgui.new_frame()

            if (self.destination_planet is not None) and (self.objects.get("transporter") is not None):
                # Get positions (world positions)
                transporter_pos = self.objects["transporter"].properties["position"]
                destination_pos = self.destination_planet.properties["position"]
                # Compute horizontal difference (using X and Z) for direction.
                diff_x = destination_pos[0] - transporter_pos[0]
                diff_z = destination_pos[2] - transporter_pos[2]
                angle = np.arctan2(diff_z, diff_x)  # angle in radians
                
                # Compute elevation difference (Y difference)
                elev_diff = destination_pos[1] - transporter_pos[1]
                
                # Get distance to destination for display
                distance = np.sqrt(diff_x**2 + diff_z**2 + elev_diff**2)
                
                # Define arrow's center in a corner (top-right) for better visibility
                arrow_center = (self.width - 100, 100)
                
                # Make arrow much bigger for better visibility
                arrow_size = 40
                local_points = [
                    (0, -arrow_size*2), 
                    (-arrow_size, arrow_size), 
                    (arrow_size, arrow_size)
                ]
                
                # Set arrow color based on elevation difference
                if elev_diff > 1.0:
                    col_u32 = imgui.get_color_u32_rgba(1.0, 0.0, 0.0, 1.0)  # red: destination is higher
                elif elev_diff < -1.0:
                    col_u32 = imgui.get_color_u32_rgba(0.0, 0.0, 1.0, 1.0)  # blue: destination is lower
                else:
                    col_u32 = imgui.get_color_u32_rgba(1.0, 1.0, 0.0, 1.0)  # yellow: nearly equal
                
                # Fixed rotation calculation
                cos_a = np.cos(angle)
                sin_a = np.sin(angle)
                
                # Rotate and translate each point correctly
                p1x = local_points[0][0] * cos_a - local_points[0][1] * sin_a + arrow_center[0]
                p1y = local_points[0][0] * sin_a + local_points[0][1] * cos_a + arrow_center[1]
                p2x = local_points[1][0] * cos_a - local_points[1][1] * sin_a + arrow_center[0]
                p2y = local_points[1][0] * sin_a + local_points[1][1] * cos_a + arrow_center[1]
                p3x = local_points[2][0] * cos_a - local_points[2][1] * sin_a + arrow_center[0]
                p3y = local_points[2][0] * sin_a + local_points[2][1] * cos_a + arrow_center[1]
                
                # Draw the filled triangle
                draw_list = imgui.get_foreground_draw_list()
                draw_list.add_triangle_filled(p1x, p1y, p2x, p2y, p3x, p3y, col_u32)
                
                # Add distance indicator text
                draw_list.add_text(arrow_center[0] - 50, arrow_center[1] + 40, 
                                imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0), 
                                f"Distance: {distance:.1f} units")
                
            imgui.render()
            self.gui.render(imgui.get_draw_data())

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

