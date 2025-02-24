import imgui
import numpy as np
from utils.graphics import Object, Camera, Shader
from assets.shaders.shaders import object_shader
from assets.objects.objects import  get_planet
import random

class Game:
    def __init__(self, height, width, gui):
        self.gui = gui
        self.height = height
        self.width = width
        self.screen = 0
        self.shaders = [Shader(object_shader["vertex_shader"], object_shader["fragment_shader"])]
        self.objects = {}
    

    def InitScene(self):
        if self.screen == 1:

            def setCamera():
                self.camera = Camera(self.height, self.width)
                self.camera.position = np.array([0, 0, 1], dtype=np.float32)
                self.camera.lookAt = np.array([0, 0, -1], dtype=np.float32)
                self.camera.up = np.array([0, 1, 0], dtype=np.float32)
                self.camera.fov = 90
            setCamera()
            ############################################################################

            def setWorldLimits():
                self.worldMin = np.array([-5000, -5000, -5000], dtype=np.float32)
                self.worldMax = np.array([5000, 5000, 5000], dtype=np.float32)
            setWorldLimits()

            # Initialize transporter
            # test_sphere = get_sphere()
            # test_sphere["position"] = [0, 0, -10]
            # self.objects["sphere"] = Object(None, self.shaders[0], test_sphere)

            ############################################################################

            

            ############################################################################

            # Initialize Planets and space stations (Randomly place n planets and n spacestations within world bounds)
            self.n_planets = 20 # for example

            self.objects["planets"] = []
            for i in range(self.n_planets):
                bottom_color = np.array([random.random(), random.random(), random.random()])
                top_color = np.array([random.random(), random.random(), random.random()])

                planet = get_planet(bottom_color , top_color)  # get default planet properties with gradient colors
                # Set a random position: x in [-300,300], y in [-300,300], z in [-150, -30]
                pos = np.array([
                    np.random.uniform(-100, 100),
                    np.random.uniform(-100, 100),
                    np.random.uniform(-150, -30)
                ], dtype=np.float32)
                planet["position"] = pos
                # Optionally, set a random uniform scale between 0.5 and 2.0
                scale_val = np.random.uniform(1.0, 3.0)
                planet["scale"] = np.array([scale_val, scale_val, scale_val], dtype=np.float32)
                # Create the planet object and add it to the list
                self.objects["planets"].append(Object(None, self.shaders[0], planet))
            

            ############################################################################
            # Initialize transporter (Randomly choose start and end planet, and initialize transporter at start planet)

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

            for planet_obj in self.objects.get("planets", []):
                planet_obj.Draw()

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
