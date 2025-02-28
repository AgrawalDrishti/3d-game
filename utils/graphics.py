 #graphics.py
import ctypes
import numpy as np
import copy
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

class VBO:
    def __init__(self, data):
        self.ID = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.ID)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
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
        float_size = ctypes.sizeof(ctypes.c_float)
        if stride == 10:
            # Interleaved data: position (3 floats), color (4 floats), normal (3 floats)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 10 * float_size, ctypes.c_void_p(0))
            
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 10 * float_size, ctypes.c_void_p(3 * float_size))
            
            glEnableVertexAttribArray(2)
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 10 * float_size, ctypes.c_void_p(7 * float_size))
        elif stride == 7:
            # Legacy interleaving: position (3 floats) + color (4 floats)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 7 * float_size, ctypes.c_void_p(0))
            
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 7 * float_size, ctypes.c_void_p(3 * float_size))
        else:
            # Fallback: positions only
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * float_size, ctypes.c_void_p(0))
    def Use(self):
        glBindVertexArray(self.vao)
    def Delete(self):
        glDeleteVertexArrays(1, (self.vao,))

class Shader:
    def __init__(self, vertex_shader, fragment_shader):
        self.ID = compileProgram(
            compileShader(vertex_shader, GL_VERTEX_SHADER),
            compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        )
        self.Use()
    def Use(self):
        glUseProgram(self.ID)
    def Delete(self):
        glDeleteProgram(self.ID)

class Camera:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.position = np.array([50, 0, 0], dtype=np.float32)
        self.lookAt = np.array([0, 0, 0], dtype=np.float32)
        self.up = np.array([0, 0, 0], dtype=np.float32)
        self.near = 1.0
        self.far = 10000
        self.fov = 90
        self.f = 1.0

    def Update(self, shader):
        shader.Use()
        
        # --- Compute the View Matrix using a standard lookAt approach ---
        # Ensure that self.position, self.lookAt, and self.up are set properly.
        n = - self.lookAt / np.linalg.norm(self.lookAt)
        u = np.cross(self.up, n)
        u = u / np.linalg.norm(u)
        v = np.cross(n, u)
        
        viewRotation = np.array([
            [ u[0],   u[1],   u[2],   0],
            [ v[0],  v[1],  v[2],  0],
            [ n[0], n[1], n[2], 0],
            [ 0,0,0,1]
        ], dtype=np.float32)
        
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
        
        viewMatrixLocation = glGetUniformLocation(shader.ID, "viewMatrix".encode('utf-8'))
        glUniformMatrix4fv(viewMatrixLocation, 1, GL_TRUE, viewMatrix)
        
        projectionMatrixLocation = glGetUniformLocation(shader.ID, "projectionMatrix".encode('utf-8'))
        glUniformMatrix4fv(projectionMatrixLocation, 1, GL_TRUE, projectionMatrix)

class Object:
    def __init__(self, objType, shader, properties):
        self.properties = copy.deepcopy(properties)
        self.shader = shader
        
        # Check if the properties include normals. If so, interleave positions, colors, and normals.
        if ('normals' in self.properties) and ('positions' in self.properties) and ('colors' in self.properties):
            positions = self.properties['positions']
            normals = self.properties['normals']
            colors = self.properties['colors']
            num_vertices = len(positions) // 3
            interleaved = []
            for i in range(num_vertices):
                # Add position (3 floats)
                interleaved.extend(positions[i*3 : (i+1)*3])
                # Add color (4 floats)
                interleaved.extend(colors[i*4 : (i+1)*4])
                # Add normal (3 floats)
                interleaved.extend(normals[i*3 : (i+1)*3])
            interleaved = np.array(interleaved, dtype=np.float32)
            self.vbo = VBO(interleaved)
            self.vao = VAO(self.vbo, 10)  # 10 floats per vertex
            self.num_vertices = num_vertices  # Save vertex count for drawing.
            # Remove these keys so we don't duplicate data.
            self.properties.pop('positions')
            self.properties.pop('normals')
            self.properties.pop('colors')
        elif 'colors' in self.properties:
            # Legacy: only positions and colors, no normals.
            vertices = self.properties['vertices']
            colors = self.properties['colors']
            num_vertices = len(vertices) // 3
            interleaved = []
            for i in range(num_vertices):
                interleaved.extend(vertices[i*3:(i+1)*3])
                interleaved.extend(colors[i*4:(i+1)*4])
            interleaved = np.array(interleaved, dtype=np.float32)
            self.vbo = VBO(interleaved)
            self.vao = VAO(self.vbo, 7)
            self.num_vertices = num_vertices
            self.properties.pop('vertices')
            self.properties.pop('colors')
        else:
            # Fallback: positions only.
            self.vbo = VBO(self.properties['vertices'])
            self.vao = VAO(self.vbo, 3)
            self.num_vertices = len(self.properties['vertices']) // 3
            self.properties.pop('vertices')
            
        # Assume indices are provided if using glDrawElements.
        if 'indices' in self.properties:
            self.ibo = IBO(self.properties['indices'])
            self.properties.pop('indices')
        else:
            self.ibo = None
        # Store shader reference in self.shader

    # def Draw(self):
    #     position = self.properties['position']
    #     scale = self.properties['scale']
    #     # Use local orientation if available.
    #     if "orientation" in self.properties:
    #         R_mat = self.properties["orientation"]
    #         rotationMatrix_full = np.eye(4, dtype=np.float32)
    #         rotationMatrix_full[:3, :3] = R_mat
    #     else:
    #         rotation = self.properties['rotation']
    #         rx, ry, rz = rotation
    #         rotation_z_matrix = np.array([
    #             [np.cos(rz), -np.sin(rz), 0, 0],
    #             [np.sin(rz),  np.cos(rz), 0, 0],
    #             [0, 0, 1, 0],
    #             [0, 0, 0, 1]
    #         ], dtype=np.float32)
    #         rotation_x_matrix = np.array([
    #             [1, 0, 0, 0],
    #             [0, np.cos(rx), -np.sin(rx), 0],
    #             [0, np.sin(rx),  np.cos(rx), 0],
    #             [0, 0, 0, 1]
    #         ], dtype=np.float32)
    #         rotation_y_matrix = np.array([
    #             [np.cos(ry), 0, np.sin(ry), 0],
    #             [0, 1, 0, 0],
    #             [-np.sin(ry), 0, np.cos(ry), 0],
    #             [0, 0, 0, 1]
    #         ], dtype=np.float32)
    #         rotationMatrix_full = rotation_z_matrix @ rotation_y_matrix @ rotation_x_matrix

    #     translation_matrix = np.array([
    #         [1, 0, 0, position[0]],
    #         [0, 1, 0, position[1]],
    #         [0, 0, 1, position[2]],
    #         [0, 0, 0, 1]
    #     ], dtype=np.float32)
    #     scale_matrix = np.array([
    #         [scale[0], 0, 0, 0],
    #         [0, scale[1], 0, 0],
    #         [0, 0, scale[2], 0],
    #         [0, 0, 0, 1]
    #     ], dtype=np.float32)
        
    #     self.modelMatrix = translation_matrix @ rotationMatrix_full @ scale_matrix

    #     self.shader.Use()
    #     modelMatrixLocation = glGetUniformLocation(self.shader.ID, "modelMatrix".encode('utf-8'))
    #     glUniformMatrix4fv(modelMatrixLocation, 1, GL_TRUE, self.modelMatrix)
        
    #     colorLocation = glGetUniformLocation(self.shader.ID, "objectColor".encode('utf-8'))
    #     c = self.properties.get("color", [1,1,1,1])
    #     glUniform4f(colorLocation, c[0], c[1], c[2], c[3])
    #     self.vao.Use()
    #     self.ibo.Use()
    #     glDrawElements(GL_TRIANGLES, self.ibo.count, GL_UNSIGNED_INT, None)

    def Draw(self):
        position = self.properties['position']
        scale = self.properties['scale']
        # Use local orientation if available.
        if "orientation" in self.properties:
            R_mat = self.properties["orientation"]
            rotationMatrix_full = np.eye(4, dtype=np.float32)
            rotationMatrix_full[:3, :3] = R_mat
        else:
            rotation = self.properties['rotation']
            rx, ry, rz = rotation
            rotation_z_matrix = np.array([
                [np.cos(rz), -np.sin(rz), 0, 0],
                [np.sin(rz),  np.cos(rz), 0, 0],
                [0,          0,          1, 0],
                [0,          0,          0, 1]
            ], dtype=np.float32)
            rotation_x_matrix = np.array([
                [1, 0,           0,          0],
                [0, np.cos(rx), -np.sin(rx),  0],
                [0, np.sin(rx),  np.cos(rx),  0],
                [0, 0,           0,          1]
            ], dtype=np.float32)
            rotation_y_matrix = np.array([
                [np.cos(ry),  0, np.sin(ry), 0],
                [0,           1, 0,          0],
                [-np.sin(ry), 0, np.cos(ry), 0],
                [0,           0, 0,          1]
            ], dtype=np.float32)
            rotationMatrix_full = rotation_z_matrix @ rotation_y_matrix @ rotation_x_matrix

        translation_matrix = np.array([
            [1, 0, 0, position[0]],
            [0, 1, 0, position[1]],
            [0, 0, 1, position[2]],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        scale_matrix = np.array([
            [scale[0], 0, 0, 0],
            [0, scale[1], 0, 0],
            [0, 0, scale[2], 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        self.modelMatrix = translation_matrix @ rotationMatrix_full @ scale_matrix

        self.shader.Use()
        modelMatrixLocation = glGetUniformLocation(self.shader.ID, "modelMatrix".encode('utf-8'))
        glUniformMatrix4fv(modelMatrixLocation, 1, GL_TRUE, self.modelMatrix)

        # Set fallback color uniform if needed.
        colorLocation = glGetUniformLocation(self.shader.ID, "objectColor".encode('utf-8'))
        c = self.properties.get("color", [1, 1, 1, 1])
        glUniform4f(colorLocation, c[0], c[1], c[2], c[3])
        
        self.vao.Use()
        
        if self.ibo is not None:
            self.ibo.Use()
            glDrawElements(GL_TRIANGLES, self.ibo.count, GL_UNSIGNED_INT, None)
        else:
            # If no indices, use glDrawArrays with the stored vertex count.
            glDrawArrays(GL_TRIANGLES, 0, self.num_vertices)

