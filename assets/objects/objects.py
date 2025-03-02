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
def rotation_matrix(rx, ry, rz):
        cx, cy, cz = np.cos([rx, ry, rz])
        sx, sy, sz = np.sin([rx, ry, rz])
        
        Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        
        return Rz @ Ry @ Rx

def load_obj_with_normals(file_path , rotation = np.array([0 , 0 , 0] , dtype=np.float32)):
    """Loads vertex positions and vertex normals from an OBJ file.
       Assumes faces are in the format v//vn (no texture coords).
       Expands all faces into triangles (no indexing)."""
    positions = []
    normals = []
    faces = []
    R = rotation_matrix(*rotation)
    R_invT = np.linalg.inv(R).T

    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                # Vertex positions
                parts = line.strip().split()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                x , y , z = R @ np.array([x , y , z])
                positions.append((x, y, z))
            elif line.startswith('vn '):
                # Vertex normals
                parts = line.strip().split()
                nx, ny, nz = float(parts[1]), float(parts[2]), float(parts[3])
                nx , ny , nz = R_invT @ np.array([nx , ny , nz])
                normals.append((nx, ny, nz))
            elif line.startswith('f '):
                # Face references: e.g. "f v1//vn1 v2//vn2 v3//vn3"
                parts = line.strip().split()[1:]  # skip 'f'
                face_indices = []
                for part in parts:
                    # Typically "v//vn"
                    sub_parts = part.split('//')
                    v_idx = int(sub_parts[0]) - 1  # convert to 0-based
                    vn_idx = int(sub_parts[1]) - 1
                    face_indices.append((v_idx, vn_idx))
                faces.append(face_indices)

    # Expand positions and normals into a flat array for all triangles
    out_positions = []
    out_normals = []
    for face in faces:
        # If it's a triangle: face = [(v_idx1, vn_idx1), (v_idx2, vn_idx2), (v_idx3, vn_idx3)]
        if len(face) == 3:
            for (vi, ni) in face:
                out_positions.extend(positions[vi])
                out_normals.extend(normals[ni])
        elif len(face) == 4:
            # Convert quad to two triangles
            # face: [(v0,vn0), (v1,vn1), (v2,vn2), (v3,vn3)]
            # Tri1: v0,v1,v2
            # Tri2: v0,v2,v3
            # for example:
            (v0, n0), (v1, n1), (v2, n2), (v3, n3) = face
            triA = [(v0,n0), (v1,n1), (v2,n2)]
            triB = [(v0,n0), (v2,n2), (v3,n3)]
            for (vi, ni) in triA:
                out_positions.extend(positions[vi])
                out_normals.extend(normals[ni])
            for (vi, ni) in triB:
                out_positions.extend(positions[vi])
                out_normals.extend(normals[ni])

    out_positions = np.array(out_positions, dtype=np.float32)
    out_normals = np.array(out_normals, dtype=np.float32)

    return out_positions, out_normals

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
    file_path = os.path.join(os.path.dirname(__file__), "models", "planet.obj")
    positions, normals = load_obj_with_normals(file_path)
    positions_reshaped = positions.reshape(-1, 3)
    
    min_y = np.min(positions_reshaped[:, 1])
    max_y = np.max(positions_reshaped[:, 1])

    colors = []
    for vertex in positions_reshaped:
        y = vertex[1]
        t = (y - min_y) / (max_y - min_y) if max_y != min_y else 0.0
        color = bottom_color * (1 - t) + top_color * t
        colors.extend(list(color) + [1.0])
    colors = np.array(colors, dtype=np.float32)

    planet_properties = {
        'positions': positions,  
        'normals': normals, 
        'colors': colors,
        'position': np.array([0, 0, -10], dtype=np.float32), 
        'velocity': np.array([0, 0, 0], dtype=np.float32),
        'rotation': np.array([0, 0, 0], dtype=np.float32),
        'scale': np.array([1, 1, 1], dtype=np.float32),
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

def get_space_station(is_destination_space_station=False):
    # Construct the path to your spacestation.obj file.
    file_path = os.path.join(os.path.dirname(__file__), "models", "spacestation.obj")
    positions, normals = load_obj_with_normals(file_path)
    num_vertices = len(positions) // 3

    # Define the default color (purple) and create the colors array.
    default_color = np.array([0.812, 0.0, 1.0, 1.0], dtype=np.float32)
    colors = np.tile(default_color, num_vertices)
    
    # Create the space station properties dictionary.
    station_properties = {
        'positions': positions,
        'normals': normals,
        'colors': colors,
        'position': np.array([0, 0, 0], dtype=np.float32),  # default; will be updated in game.py
        'velocity': np.array([0, 0, 0], dtype=np.float32),
        'rotation': np.array([0, 0, 0], dtype=np.float32),
        'scale': np.array([0.5, 0.5, 0.5], dtype=np.float32),
        'color': default_color,
        'sens': 250,
        'rotation_radius': 1.5,
        'init_position': np.array([0, 0, 0], dtype=np.float32),
        'is_destination_space_station': is_destination_space_station
    }

    # If this space station is marked as the destination, update its color to green.
    if is_destination_space_station:
        green_color = np.array([0.0, 1.0, 0.0, 1.0], dtype=np.float32)
        station_properties['color'] = green_color
        station_properties['colors'] = np.tile(green_color, num_vertices)

    return station_properties

def get_transporter():
    # Construct the path to your transporter.obj file.
    file_path = os.path.join(os.path.dirname(__file__), "models", "transporter.obj")
    positions , normals = load_obj_with_normals(file_path , np.array([np.pi/2 , np.pi/2 , 0] , dtype=np.float32))
    
    # For this example, we'll assign a uniform color (e.g. bright red) to the transporter.
    # vertices_reshaped = vertices.reshape(-1, 3)
    num_vertices = len(positions)//3
    colors = []

    positions_reshaped = positions.reshape(-1, 3)
    # Compute min and max Y-values.
    min_y = np.min(positions_reshaped[:, 1])
    max_y = np.max(positions_reshaped[:, 1])
    
    # Define dark grey and light grey for the gradient.
    dark_grey = np.array([0.2, 0.2, 0.2], dtype=np.float32)
    light_grey = np.array([0.7, 0.7, 0.7], dtype=np.float32)
    
    colors = []
    for vertex in positions_reshaped:
        y = vertex[1]
        # Interpolation factor based on Y (if max_y==min_y, t defaults to 0).
        t = (y - min_y) / (max_y - min_y) if max_y != min_y else 0.0
        # Interpolate between dark_grey and light_grey.
        col = dark_grey * (1 - t) + light_grey * t
        colors.extend([col[0], col[1], col[2], 1.0])
    colors = np.array(colors, dtype=np.float32)

    
    transporter_properties = {
        'positions': positions,
        'normals': normals,
        'colors': colors,
        # Default position; will be updated in game.py (e.g. placed at a source station)
        'position': np.array([0, 0, -5], dtype=np.float32),
        'velocity': np.array([0, 0, 0], dtype=np.float32),
        # Set an initial rotation if desired.
        'rotation': np.array([0, 0, 0], dtype=np.float32),
        # Scale can be adjusted for appropriate size.
        'scale': np.array([1, 1, 1], dtype=np.float32),
        # Fallback uniform color.
        'color': np.array([1.0, 0.0, 0.0, 1.0], dtype=np.float32),
        'sens': 250,
        'speed': 0.05
    }
    return transporter_properties

def get_pirate():
    # Construct the path to your "pirate.obj" file
    file_path = os.path.join(os.path.dirname(__file__), "models", "pirate.obj")
    
    # Load positions and normals (if the pirate model has them). 
    # If your pirate doesn't need rotation, just pass a default array. 
    positions, normals = load_obj_with_normals(file_path)

    # We'll create a simple uniform color (e.g. grey) or random color, or you can do a gradient.
    num_vertices = len(positions) // 3
    # For demonstration, let's make it a uniform grey: (0.5,0.5,0.5,1)
    colors = np.tile(np.array([1, 0.0 , 0.0, 1.0], dtype=np.float32), num_vertices)
    
    pirate_properties = {
        'positions': positions,
        'normals': normals,
        'colors': colors,
        # We'll set position in game.py
        'position': np.array([0,0,0], dtype=np.float32),
        'velocity': np.array([0,0,0], dtype=np.float32),
        'rotation': np.array([0,0,0], dtype=np.float32),
        'scale': np.array([1,1,1], dtype=np.float32),
        # fallback color if needed
        'color': np.array([0.5,0.5,0.5,1.0], dtype=np.float32),
        'sens': 250,
    }
    return pirate_properties

def get_laser():
    # Construct the path to your laser.obj file.
    file_path = os.path.join(os.path.dirname(__file__), "models", "laser.obj")
    positions, normals = load_obj_with_normals(file_path)
    num_vertices = len(positions) // 3

    # Assign a uniform color to the laser.
    # You can choose any color; here, we use a bright yellow.
    laser_color = np.array([1.0, 1.0, 0.0, 1.0], dtype=np.float32)
    colors = np.tile(laser_color, num_vertices)

    laser_properties = {
        'positions': positions,
        'normals': normals,
        'colors': colors,
        # Initial position can be set dynamically when the laser is fired.
        'position': np.array([0, 0, 0], dtype=np.float32),
        # Lasers will have velocity when fired.
        'velocity': np.array([0, 0, 0], dtype=np.float32),
        'rotation': np.array([0, 0, 0], dtype=np.float32),
        # Scale might be adjusted based on your desired laser size.
        'scale': np.array([1, 1, 1], dtype=np.float32),
        'color': laser_color,
        'sens': 250,
    }
    return laser_properties
