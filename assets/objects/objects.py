import numpy as np
import os

###############################################################
# Write logic to load OBJ Files:
    # Will depend on type of object. For example if normals needed along with vertex positions 
    # then will need to load slightly differently.

# Can use the provided OBJ files from assignment_2_template/assets/objects/models/
# Can also download other assets or model yourself in modelling softwares like blender

###############################################################
# Create Transporter, Pirates, Stars(optional), Minimap arrow, crosshair, planet, spacestation, laser


###############################################################

def load_obj(file_path):
    vertices = []
    indices = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.strip().split()
                # Read vertex positions
                vertices.extend([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith('f '):
                parts = line.strip().split()
                face = []
                for part in parts[1:]:
                    # OBJ indices are 1-based, so convert to 0-based index
                    idx = int(part.split('/')[0]) - 1
                    face.append(idx)
                # Handle triangular faces, or split quads into two triangles
                if len(face) == 3:
                    indices.extend(face)
                elif len(face) == 4:
                    indices.extend([face[0], face[1], face[2], face[0], face[2], face[3]])
    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def get_planet(bottom_color , top_color):
    # Construct the path to your planet.obj file.
    file_path = os.path.join(os.path.dirname(__file__), "models", "planet.obj")
    vertices, indices = load_obj(file_path)

    # Reshape vertices into (N, 3) for easier processing.
    vertices_reshaped = vertices.reshape(-1, 3)
    
    # Compute min and max y to determine gradient limits.
    min_y = np.min(vertices_reshaped[:, 1])
    max_y = np.max(vertices_reshaped[:, 1])
    
    # Define your gradient colors.
    # Bottom color: dark blue; Top color: light blue.
    # bottom_color = np.array([0.0, 0.0, 0.5])
    # top_color = np.array([0.5, 0.7, 1.0])
    
    colors = []
    for vertex in vertices_reshaped:
        y = vertex[1]
        # Compute an interpolation factor based on y-coordinate.
        t = (y - min_y) / (max_y - min_y) if max_y != min_y else 0.0
        # Interpolate between bottom_color and top_color.
        color = bottom_color * (1 - t) + top_color * t
        # Append RGBA (alpha set to 1.0).
        colors.extend(list(color) + [1.0])
    colors = np.array(colors, dtype=np.float32)

    planet_properties = {
        'vertices': vertices,
        'indices': indices,
        'colors': colors,
        'position': np.array([0, 0, -10], dtype=np.float32),  # Adjust as needed
        'velocity': np.array([0, 0, 0], dtype=np.float32),
        'rotation': np.array([0, 0, 0], dtype=np.float32),
        'scale': np.array([1, 1, 1], dtype=np.float32),
        # Set a more natural color for the planet (e.g., a bluish hue)
        'color': np.array([0.2, 0.6, 1.0, 1.0], dtype=np.float32),
        'sens': 250,
    }
    return planet_properties


def create_sphere(radius, segments):
    vertices = []
    indices = []

    for y in range(segments + 1):
        for x in range(segments + 1):
            x_segment = x / segments
            y_segment = y / segments
            x_pos = radius * np.cos(x_segment * 2.0 * np.pi) * np.sin(y_segment * np.pi)
            y_pos = radius * np.cos(y_segment * np.pi)
            z_pos = radius * np.sin(x_segment * 2.0 * np.pi) * np.sin(y_segment * np.pi)

            vertices.extend([x_pos, y_pos, z_pos])

    for y in range(segments):
        for x in range(segments):
            i0 = y * (segments + 1) + x
            i1 = i0 + 1
            i2 = i0 + (segments + 1)
            i3 = i2 + 1

            indices.extend([i0, i2, i1])
            indices.extend([i1, i2, i3])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def get_space_station():
    # Construct the path to your spacestation.obj file.
    file_path = os.path.join(os.path.dirname(__file__), "models", "spacestation.obj")
    vertices, indices = load_obj(file_path)
    
    # For simplicity, we'll assign a uniform color to all vertices (e.g. light gray).
    vertices_reshaped = vertices.reshape(-1, 3)
    num_vertices = vertices_reshaped.shape[0]
    # Create a colors array: for each vertex, assign a RGBA value.
    colors = np.tile(np.array([0.812, 0.0, 1.0, 1.0], dtype=np.float32), num_vertices)
    
    station_properties = {
        'vertices': vertices,
        'indices': indices,
        'colors': colors,
        'position': np.array([0, 0, 0], dtype=np.float32),  # default; will be updated in game.py
        'velocity': np.array([0, 0, 0], dtype=np.float32),
        'rotation': np.array([0, 0, 0], dtype=np.float32),
        'scale': np.array([0.5, 0.5, 0.5], dtype=np.float32),
        'color': np.array([0.812, 0.0, 1.0, 1.0], dtype=np.float32),
        'sens': 250,
        'rotation_radius': 1.5,
        'init_position': np.array([0, 0, 0], dtype=np.float32),
    }
    return station_properties
