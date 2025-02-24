######################################################
# Write other shaders for minimap and crosshair (Since they need orthographic projection)

object_shader = {
    # "vertex_shader" : '''
        
    #     #version 330 core
    #     layout(location = 0) in vec3 vertexPosition;
    #     layout(location = 1) in vec4 vertexColor; // New: per-vertex color attribute

    #     uniform mat4 modelMatrix;
    #     uniform mat4 viewMatrix;
    #     uniform mat4 projectionMatrix;
    #     uniform float focalLength;

    #     out vec4 fragColor; // Pass color to fragment shader

    #     void main() {
    #         vec4 camCoordPos = viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
    #         gl_Position = projectionMatrix * vec4(focalLength * (camCoordPos[0] / abs(camCoordPos[2])), focalLength * (camCoordPos[1] / abs(camCoordPos[2])), camCoordPos[2], 1.0);
    #         fragColor = vertexColor;
    #     }
    #     ''',

    "vertex_shader" : '''
        #version 330 core
        layout(location = 0) in vec3 vertexPosition;
        layout(location = 1) in vec4 vertexColor;

        uniform mat4 modelMatrix;
        uniform mat4 viewMatrix;
        uniform mat4 projectionMatrix;

        out vec4 fragColor;

        void main() {
            gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
            fragColor = vertexColor;
        }
        ''',

    "fragment_shader" : '''
        
        #version 330 core

        in vec4 fragColor; // Receive interpolated vertex color
        out vec4 outputColor;

        void main() {
            outputColor = fragColor;
        }
        '''
}
######################################################
