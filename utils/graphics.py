import ctypes
import numpy as np
import copy
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

class VBO:
    def __init__(self, vertices):
        self.ID = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.ID)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    def Use(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.ID)
    def Delete(self):
        glDeleteBuffers(1, (self.ID,))

class IBO:
    def __init__(self, indices):
        self.ID = glGenBuffers(1)
        self.count = len(indices)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ID)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    def Use(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ID)
    def Delete(self):
        glDeleteBuffers(1, (self.ID,))

class VAO:
    def __init__(self, vbo: VBO, stride):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        vbo.Use()
        # If stride is 7, then we assume 3 floats for position and 4 floats for color.
        if stride == 7:
            # Position attribute: location 0, 3 floats, stride of 7 floats, offset 0
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 7 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(0))
            # Color attribute: location 1, 4 floats, stride of 7 floats, offset 3 floats
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 7 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        else:
            # Fallback (positions only)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(0))
    def Use(self):
        glBindVertexArray(self.vao)
    def Delete(self):
        glDeleteVertexArrays(1, (self.vao,))

class Shader:
    def __init__(self, vertex_shader, fragment_shader):
        self.ID = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER), compileShader(fragment_shader, GL_FRAGMENT_SHADER))
        self.Use()
    def Use(self):
        glUseProgram(self.ID)
    def Delete(self):
        glDeleteProgram((self.ID,))

class Camera:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.position = np.array([50,0,0], dtype=np.float32)
        self.lookAt = np.array([0,0,0], dtype=np.float32)
        self.up = np.array([0,0,0], dtype=np.float32)
        self.near = 1.0
        self.far = 10000
        self.fov = 90

        self.f = 1.0

    # def Update(self, shader):
    #     shader.Use()

    #     # View matrix

    #     viewTranslate = np.array([  [1, 0, 0, -self.position[0]],
    #                                 [0, 1, 0, -self.position[1]],
    #                                 [0, 0, 1, -self.position[2]],
    #                                 [0, 0, 0, 1]], dtype = np.float32)
        
    #     n = - self.lookAt / np.linalg.norm(self.lookAt)
        
    #     u = np.cross(self.up, n)
    #     u = u / np.linalg.norm(u)

    #     v = np.cross(n, u)
    #     v = v / np.linalg.norm(v)

    #     viewRotate = np.array([[u[0], u[1], u[2],0],
    #                         [v[0], v[1], v[2],0],
    #                         [n[0], n[1], n[2],0],
    #                         [  0,    0,    0, 1]], dtype = np.float32)

    #     viewMatrix = viewRotate @ viewTranslate
        
    #     # Projection matrix

    #     orthoTranslate = np.array([  [1,0,0,0],
    #                                 [0,1,0,0],
    #                                 [0,0,1, (self.near + self.far)/2.0],
    #                                 [0,0,0,1]], dtype = np.float32)
        
    #     fovRadians = np.radians(self.fov/2)
    #     cameraHeight = 2 * self.f * np.tan(fovRadians)
    #     cameraWidth = (self.width/self.height) * cameraHeight
    #     orthoScale = np.array([ [2.0/cameraWidth, 0, 0, 0],
    #                             [0, 2.0/cameraHeight, 0, 0],
    #                             [0, 0, -2.0/(self.far - self.near), 0],
    #                             [0, 0, 0, 1]], dtype = np.float32)


    #     projectionMatrix = orthoScale @ orthoTranslate

    #     viewMatrixLocation = glGetUniformLocation(shader.ID, "viewMatrix".encode('utf-8'))
    #     glUniformMatrix4fv(viewMatrixLocation, 1, GL_TRUE, viewMatrix)

    #     projectionMatrixLocation = glGetUniformLocation(shader.ID, "projectionMatrix".encode('utf-8'))
    #     glUniformMatrix4fv(projectionMatrixLocation, 1, GL_TRUE, projectionMatrix)

    #     focalLengthLocation = glGetUniformLocation(shader.ID, "focalLength".encode('utf-8'))
    #     glUniform1f(focalLengthLocation, self.f)
    def Update(self, shader):
        shader.Use()
        
        # --- Compute the View Matrix using a standard lookAt approach ---
        # Ensure that self.position, self.lookAt, and self.up are set properly.
        forward = self.lookAt - self.position
        forward = forward / np.linalg.norm(forward)
        right = np.cross(forward, self.up)
        right = right / np.linalg.norm(right)
        trueUp = np.cross(right, forward)
        
        # Build the rotation part of the view matrix.
        viewRotation = np.array([
            [ right[0],   right[1],   right[2],   0],
            [ trueUp[0],  trueUp[1],  trueUp[2],  0],
            [ -forward[0], -forward[1], -forward[2], 0],
            [ 0,          0,          0,          1]
        ], dtype=np.float32)
        
        # Build the translation part of the view matrix.
        viewTranslation = np.array([
            [1, 0, 0, -self.position[0]],
            [0, 1, 0, -self.position[1]],
            [0, 0, 1, -self.position[2]],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        viewMatrix = viewRotation @ viewTranslation
        
        # --- Compute a Standard Perspective Projection Matrix ---
        aspect = self.width / self.height
        fov_rad = np.radians(self.fov)
        f = 1.0 / np.tan(fov_rad / 2.0)
        near = self.near
        far = self.far
        projectionMatrix = np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0]
        ], dtype=np.float32)
        
        # --- Upload the matrices to the shader ---
        viewMatrixLocation = glGetUniformLocation(shader.ID, "viewMatrix".encode('utf-8'))
        glUniformMatrix4fv(viewMatrixLocation, 1, GL_TRUE, viewMatrix)
        
        projectionMatrixLocation = glGetUniformLocation(shader.ID, "projectionMatrix".encode('utf-8'))
        glUniformMatrix4fv(projectionMatrixLocation, 1, GL_TRUE, projectionMatrix)



class Object:
    def __init__(self, objType, shader, properties):
        self.properties = copy.deepcopy(properties)
        # Check if colors exist; if so, interleave vertex positions and colors.
        if 'colors' in self.properties:
            vertices = self.properties['vertices']
            colors = self.properties['colors']
            num_vertices = len(vertices) // 3
            interleaved = []
            for i in range(num_vertices):
                # Add position (3 floats)
                interleaved.extend(vertices[i*3:(i+1)*3])
                # Add color (4 floats)
                interleaved.extend(colors[i*4:(i+1)*4])
            interleaved = np.array(interleaved, dtype=np.float32)
            # Use the interleaved data in the VBO.
            self.vbo = VBO(interleaved)
            # The stride is now 7 floats per vertex.
            self.vao = VAO(self.vbo, 7)
            # Remove vertices and colors from properties as they've been consumed.
            self.properties.pop('vertices')
            self.properties.pop('colors')
        else:
            self.vbo = VBO(self.properties['vertices'])
            self.vao = VAO(self.vbo, 3)
            self.properties.pop('vertices')
        self.ibo = IBO(self.properties['indices'])
        self.properties.pop('indices')
        self.shader = shader

    def Draw(self):
        # Build the model matrix from position, rotation, and scale.
        position = self.properties['position']
        rotation = self.properties['rotation']
        scale = self.properties['scale']

        translation_matrix = np.array([
            [1, 0, 0, position[0]],
            [0, 1, 0, position[1]],
            [0, 0, 1, position[2]],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        rotation_z_matrix = np.array([
            [np.cos(rotation[2]), -np.sin(rotation[2]), 0, 0],
            [np.sin(rotation[2]),  np.cos(rotation[2]), 0, 0],
            [0,                  0,                   1, 0],
            [0,                  0,                   0, 1]
        ], dtype=np.float32)
        rotation_x_matrix = np.array([
            [1, 0, 0, 0],
            [0, np.cos(rotation[0]), -np.sin(rotation[0]), 0],
            [0, np.sin(rotation[0]),  np.cos(rotation[0]), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        rotation_y_matrix = np.array([
            [np.cos(rotation[1]), 0, np.sin(rotation[1]), 0],
            [0, 1, 0, 0],
            [-np.sin(rotation[1]), 0, np.cos(rotation[1]), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        scale_matrix = np.array([
            [scale[0], 0, 0, 0],
            [0, scale[1], 0, 0],
            [0, 0, scale[2], 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        rotationMatrix = rotation_z_matrix @ rotation_y_matrix @ rotation_x_matrix
        self.modelMatrix = translation_matrix @ rotationMatrix @ scale_matrix

        # Bind shader and set uniforms.
        self.shader.Use()
        modelMatrixLocation = glGetUniformLocation(self.shader.ID, "modelMatrix".encode('utf-8'))
        glUniformMatrix4fv(modelMatrixLocation, 1, GL_TRUE, self.modelMatrix)
        
        # The uniform "objectColor" is now unused since the shader uses per-vertex colors,
        # but we set it anyway as a fallback.
        colorLocation = glGetUniformLocation(self.shader.ID, "objectColor".encode('utf-8'))
        glUniform4f(colorLocation,
                    self.properties["color"][0],
                    self.properties["color"][1],
                    self.properties["color"][2],
                    self.properties["color"][3])
        self.vao.Use()
        self.ibo.Use()
        glDrawElements(GL_TRIANGLES, self.ibo.count, GL_UNSIGNED_INT, None)        