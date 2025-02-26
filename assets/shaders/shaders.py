######################################################
# Write other shaders for minimap and crosshair (Since they need orthographic projection)

######################################################
# Lighting shader with vertex normals for metallic shading

lighting_shader = {
    "vertex_shader" : '''
        #version 330 core
        // Input attributes
        layout(location = 0) in vec3 inPosition;
        layout(location = 1) in vec4 inColor;
        layout(location = 2) in vec3 inNormal;
        
        // Uniform matrices
        uniform mat4 modelMatrix;
        uniform mat4 viewMatrix;
        uniform mat4 projectionMatrix;
        
        // Outputs to fragment shader
        out vec4 vertColor;
        out vec3 vertNormal;
        out vec3 fragPos;
        
        void main(){
            // Transform vertex position into world space
            vec4 worldPos = modelMatrix * vec4(inPosition, 1.0);
            // Compute final position in clip space
            gl_Position = projectionMatrix * viewMatrix * worldPos;
            
            // Pass along the per-vertex color
            vertColor = inColor;
            // Transform the normal to world space (assuming uniform scaling)
            vertNormal = normalize(mat3(modelMatrix) * inNormal);
            // Pass the world-space position for lighting calculations
            fragPos = worldPos.xyz;
        }
    ''',
    
    "fragment_shader" : '''
        #version 330 core
        in vec4 vertColor;
        in vec3 vertNormal;
        in vec3 fragPos;
        
        out vec4 outputColor;
        
        // Uniforms for lighting calculations.
        // You can adjust these or update them from your game code.
        uniform vec3 lightPos;         // Position of the light in world space.
        uniform vec3 viewPos;          // Position of the camera/viewer.
        uniform float ambientStrength; // e.g. 0.3
        uniform float specularStrength;// e.g. 0.8
        uniform float shininess;       // e.g. 64.0
        
        void main(){
            // Normalize the incoming normal
            vec3 norm = normalize(vertNormal);
            // Compute light direction
            vec3 lightDir = normalize(lightPos - fragPos);
            // Ambient component
            vec3 ambient = ambientStrength * vertColor.rgb;
            // Diffuse component
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * vertColor.rgb;
            // Specular component using Blinn-Phong model.
            vec3 viewDir = normalize(viewPos - fragPos);
            vec3 halfwayDir = normalize(lightDir + viewDir);
            float spec = pow(max(dot(norm, halfwayDir), 0.0), shininess);
            vec3 specular = specularStrength * spec * vec3(1.0, 1.0, 1.0);
            
            vec3 result = ambient + diffuse + specular;
            outputColor = vec4(result, 1.0);
        }
    '''
}

######################################################



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
