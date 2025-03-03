#game..py
import imgui
import numpy as np
from utils.graphics import Object, Camera, Shader
from assets.shaders.shaders import object_shader , lighting_shader
from assets.objects.objects import  get_planet , get_space_station , get_transporter , rotation_matrix , get_pirate , get_laser
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
        self.view_mode = "3rd"
        self.prev_right_click = False
        self.objects["lasers"] = []

    def DrawCrosshair(self):
        # Only draw the crosshair in 1st person view
        if self.view_mode == "1st":
            # Compute the center of the window
            center_x = self.width / 2
            center_y = self.height / 2

            # Crosshair settings: length of each line and thickness
            crosshair_length = 10  # half-length of the crosshair lines
            thickness = 2.0
            color = imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0)  # white color

            # Get the current ImGui foreground draw list
            draw_list = imgui.get_foreground_draw_list()

            # Draw horizontal line
            draw_list.add_line(center_x - crosshair_length, center_y,
                            center_x + crosshair_length, center_y,
                            color, thickness)
            # Draw vertical line
            draw_list.add_line(center_x, center_y - crosshair_length,
                            center_x, center_y + crosshair_length,
                            color, thickness)

    def spawn_laser(self):
        laser = get_laser()
        laser["position"] = copy.deepcopy(self.camera.position)
        laser_speed = 500.0  
        laser["velocity"] = self.camera.lookAt * laser_speed
        laser["scale"] = np.array([0.05, 0.05, 0.05], dtype=np.float32)
        
        self.objects["lasers"].append(Object(None, self.shaders[0], laser))

    def InitScene(self):
        if self.screen == 1:
            self.view_mode = "3rd"
            def setCamera():
                self.camera = Camera(self.height, self.width)
                self.camera.position = np.array([0, 0, 0], dtype=np.float32)
                self.camera.lookAt = np.array([0, 0, -1], dtype=np.float32)
                self.camera.up = np.array([0, 1, 0], dtype=np.float32)
                self.camera.fov = 90
                self.camera.near = 0.1
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
                    np.random.uniform(-5000, 5000),
                    np.random.uniform(-5000, 5000),
                    np.random.uniform(-5000, 5000)
                ], dtype=np.float32)

                planet["position"] = pos
                scale_val = 50.0
                planet["scale"] = np.array([scale_val, scale_val, scale_val], dtype=np.float32)
                self.objects["planets"].append(Object(None, self.shaders[0], planet))
            
            self.objects["stations"] = []
            num_stations = len(self.objects.get("planets", []))

            if num_stations >= 2:
                indices = list(range(num_stations))
                source_index = random.choice(indices)
                indices.remove(source_index)
                destination_index = random.choice(indices)
            else:
                source_index = 0
                destination_index = 0

            for i, planet_obj in enumerate(self.objects.get("planets", [])):
                is_destination = (i == destination_index)
                station = get_space_station(is_destination_space_station=is_destination)

                if "normals" not in station:
                    n_vertices = len(station["vertices"]) // 3
                    station["normals"] = np.tile(np.array([0, 0, 1], dtype=np.float32), n_vertices)
                
                orbit_radius = 60.0  # Adjust as needed
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
                station["scale"] = np.array([5, 5, 5], dtype=np.float32)
                self.objects["stations"].append(Object(None, self.shaders[0], station))

            print(f"Source index: {source_index}, Destination index: {destination_index}")

            source_station = self.objects["stations"][source_index]
            destination_station = self.objects["stations"][destination_index]
            self.destination_station = destination_station

            self.destination_planet = self.objects["planets"][destination_index]
            print("Destination planet position:", self.destination_planet.properties["position"])

            transporter = get_transporter()
            transporter["position"] = copy.deepcopy(source_station.properties["position"])+ np.array([0, -1.0, 0], dtype=np.float32)
            print("Source station position: ", source_station.properties["position"])
            print("Transporter position: ", transporter["position"])
            print("Destination station position: ", destination_station.properties["position"])
            transporter["scale"] = np.array([0.2, 0.2, 0.2], dtype=np.float32)
            self.objects["transporter"] = Object(None, self.shaders[0], transporter)
            
            self.n_pirates = 20 
            self.objects["pirates"] = []
            for i in range(self.n_pirates):
                pirate = get_pirate()
                
                pos = np.array([
                    np.random.uniform(-4000, 4000),
                    np.random.uniform(-4000, 4000),
                    np.random.uniform(-4000, 4000)
                ], dtype=np.float32)

                pirate["position"] = pos
                pirate["scale"] = np.array([1, 1, 1], dtype=np.float32)

                speed = 50
                direction = np.random.uniform(-1, 1, size=3)
                direction_norm = np.linalg.norm(direction)
                if direction_norm > 0:
                    direction = direction / direction_norm  
                pirate["velocity"] = direction * speed
                pirate_obj = Object(None, self.shaders[0], pirate)
                self.objects["pirates"].append(pirate_obj)

    def ProcessFrame(self, inputs, time):
        current_right_click = inputs.get("R_CLICK", False)
        if current_right_click and not self.prev_right_click:
            # Toggle view mode.
            self.view_mode = "1st" if self.view_mode == "3rd" else "3rd"
            print("Switched to", self.view_mode, "person view")
        self.prev_right_click = current_right_click

        self.DrawText()
        self.UpdateScene(inputs, time)
        self.DrawScene()

    def DrawText(self):
        if self.screen == 0: 
            window_w, window_h = 400, 200  
            x_pos = (self.width - window_w) / 2
            y_pos = (self.height - window_h) / 2

            imgui.new_frame()
            imgui.set_next_window_position(x_pos, y_pos)
            imgui.set_next_window_size(window_w, window_h)
            imgui.begin("Main Menu", False, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)

            if imgui.button("Start Game" , 395 , 80):
                self.screen = 1
                self.InitScene()
            if imgui.button("Exit" , 395 , 80):
                exit(0) 

            imgui.end()
            imgui.render()
            self.gui.render(imgui.get_draw_data())

        if self.screen == 2: 
            window_w, window_h = 400, 200  
            x_pos = (self.width - window_w) / 2
            y_pos = (self.height - window_h) / 2

            imgui.new_frame()
            imgui.set_next_window_position(x_pos, y_pos)
            imgui.set_next_window_size(window_w, window_h)
            imgui.begin("Game Won", False, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)
            
            imgui.set_cursor_pos_x((window_w - imgui.calc_text_size("GAME WON")[0]) / 2)
            imgui.text("GAME WON")
            
            if imgui.button("Back to Menu", 395, 80):
                self.screen = 0  
            
            imgui.end()
            imgui.render()
            self.gui.render(imgui.get_draw_data())


        if self.screen == 3: 
            window_w, window_h = 400, 200 
            x_pos = (self.width - window_w) / 2
            y_pos = (self.height - window_h) / 2

            imgui.new_frame()
            imgui.set_next_window_position(x_pos, y_pos)
            imgui.set_next_window_size(window_w, window_h)
            imgui.begin("Game Over", False, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)
            
            imgui.set_cursor_pos_x((window_w - imgui.calc_text_size("GAME OVER")[0]) / 2)
            imgui.text("GAME OVER")
            
            if imgui.button("Back to Menu", 395, 80):
                self.screen = 0   
            
            imgui.end()
            imgui.render()
            self.gui.render(imgui.get_draw_data())
     
    def UpdateScene(self, inputs, time):
        if self.screen == 1: 
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
                chase_speed = 50.0  
                for pirate_obj in self.objects.get("pirates", []):
                    pirate_pos = pirate_obj.properties["position"]
                    direction = transporter_pos - pirate_pos
                    norm = np.linalg.norm(direction)
                    if norm > 0:
                        direction = direction / norm  # Normalize
                    else:
                        direction = np.array([0, 0, 0], dtype=np.float32)
                    pirate_obj.properties["velocity"] = direction * chase_speed
                    pirate_obj.properties["position"] += pirate_obj.properties["velocity"] * delta

            if self.objects.get("transporter") is not None and self.objects.get("pirates") is not None:
                transporter_pos = self.objects["transporter"].properties["position"]
                collision_threshold = 3.0  
                for pirate_obj in self.objects["pirates"]:
                    pirate_pos = pirate_obj.properties["position"]
                    if np.linalg.norm(transporter_pos - pirate_pos) < collision_threshold:
                        print("Collision detected! Game Over.")
                        self.screen = 3 
                        break
            
            if self.view_mode == "3rd":
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

                    max_speed = 60.0 

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

                    dest_pos = self.destination_station.properties["position"]
                    transport_pos = transporter.properties["position"]
                    distance_to_destination = np.linalg.norm(dest_pos - transport_pos)
                    if distance_to_destination < 10.0:
                        print("Game Won! Distance:", distance_to_destination)
                        self.screen = 2  # Switch to game-won screen

            else:               
                if inputs.get("L_CLICK"):
                    self.spawn_laser()
                    print("Laser fired!")
                
                mousedelta = np.linalg.norm(inputs["mouseDelta"])/1000 * time['deltaTime']
                cam_left = np.cross(self.camera.up, self.camera.lookAt)
                if inputs["mouseDelta"][0] < 0:
                    self.camera.lookAt = self.camera.lookAt + mousedelta * cam_left
                if inputs["mouseDelta"][0] > 0:
                    self.camera.lookAt = self.camera.lookAt - mousedelta * cam_left
                if inputs["mouseDelta"][1] < 0:
                    self.camera.lookAt = self.camera.lookAt + mousedelta * self.camera.up
                if inputs["mouseDelta"][1] > 0:
                    self.camera.lookAt = self.camera.lookAt - mousedelta * self.camera.up

                self.camera.lookAt = self.camera.lookAt / np.linalg.norm(self.camera.lookAt)
                self.camera.up = np.cross(self.camera.lookAt, cam_left)


                if self.objects.get("transporter") is not None:
                    transporter = self.objects["transporter"]
                    # Ensure that an orientation exists. It should have been set in 3rd person mode.
                    if "orientation" not in transporter.properties:
                        transporter.properties["orientation"] = rotation_matrix(*transporter.properties["rotation"])
                    
                    # Get the current (static) orientation.
                    current_orient = transporter.properties["orientation"]
                    forward_spaceship = current_orient @ np.array([0, 0, -1], dtype=np.float32)
                    up_spaceship = current_orient @ np.array([0, 1, 0], dtype=np.float32)

                    max_speed = 10.0
                    # Allow only space bar to accelerate the spaceship in the forward direction.
                    if inputs.get("SPACE"):
                        transporter.properties["speed"] += 0.05
                        if transporter.properties["speed"] > max_speed:
                            transporter.properties["speed"] = max_speed

                        transporter.properties["velocity"] = transporter.properties["speed"] * forward_spaceship
                    else:
                        transporter.properties["speed"] = 0.0
                        transporter.properties["velocity"] = np.array([0, 0, 0], dtype=np.float32)
                    
                    transporter.properties["position"] += transporter.properties["velocity"] * delta

                    # In 1st person view, the camera is attached directly to the transporter.
                    camera_offset = (-0.0* forward_spaceship) + (1.0* up_spaceship)
                    self.camera.position = copy.deepcopy(transporter.properties["position"]) + camera_offset

                    # self.camera.lookAt = forward_spaceship
                    # self.camera.up = up_spaceship 

                # --- Update lasers ---
                if "lasers" in self.objects:
                    for laser_obj in self.objects["lasers"][:]:
                        laser_obj.properties["position"] += laser_obj.properties["velocity"] * delta
                        
                        if np.linalg.norm(laser_obj.properties["position"]) > 5000:
                            self.objects["lasers"].remove(laser_obj)       
            
            ############################################################################
            # Update Pirates (Write logic to update their velocity based on transporter position, and check for collision with laser or transporter)
            for pirate in self.objects['pirates']:
                for laser in self.objects['lasers']:
                    if np.linalg.norm(pirate.properties['position'] - laser.properties['position']) < 50:
                        self.objects['pirates'].remove(pirate)
                        self.objects['lasers'].remove(laser)
                        break

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
            
            for laser_obj in self.objects.get("lasers", []):
                laser_obj.Draw()

            # START ImGui rendering properly (BEFORE any ImGui drawing)
            imgui.new_frame()
            self.DrawCrosshair()

            if (self.destination_station is not None) and (self.objects.get("transporter") is not None):
                # Get positions (world positions)
                transporter_pos = self.objects["transporter"].properties["position"]
                destination_pos = self.destination_station.properties["position"]
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
            ######################################################
            pass

