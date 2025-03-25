import glfw
from OpenGL.GL import *
import glm
import numpy as np
import random
import os

# Window and camera settings
window_width = 800
window_height = 600
camera_pos = glm.vec3(0.0, 5.0, 10.0)
camera_front = glm.vec3(0.0, -0.5, -1.0)
camera_up = glm.vec3(0.0, 1.0, 0.0)
polluted_mode = True
p_key_pressed = False

# OpenGL objects
vao, vbo = 0, 0
particle_vao, particle_vbo = 0, 0
particles = []
shader = None
window = None

class BSPNode:
    def __init__(self):
        self.normal = glm.vec3()
        self.distance = 0.0
        self.polygons = []
        self.front = None
        self.back = None

class Particle:
    def __init__(self):
        self.position = glm.vec3()
        self.velocity = glm.vec3()
        self.life = 0.0

class Shader:
    def __init__(self, vertex_path, fragment_path):
        try:
            with open(vertex_path, 'r') as f:
                vertex_src = f.read()
            with open(fragment_path, 'r') as f:
                fragment_src = f.read()
        except Exception as e:
            raise RuntimeError(f"Shader loading failed: {str(e)}")

        self.program = glCreateProgram()
        vertex_shader = self.compile_shader(GL_VERTEX_SHADER, vertex_src)
        fragment_shader = self.compile_shader(GL_FRAGMENT_SHADER, fragment_src)
        
        glAttachShader(self.program, vertex_shader)
        glAttachShader(self.program, fragment_shader)
        glLinkProgram(self.program)
        
        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            info = glGetProgramInfoLog(self.program).decode()
            raise RuntimeError(f"Shader linking error: {info}")
        
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

    def compile_shader(self, shader_type, source):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            info = glGetShaderInfoLog(shader).decode()
            raise RuntimeError(f"Shader compilation error: {info}")
        return shader

    def use(self):
        glUseProgram(self.program)

    def set_mat4(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(value))

    def set_vec3(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        glUniform3fv(loc, 1, glm.value_ptr(value))

def init_particles():
    global particle_vao, particle_vbo, particles
    particles = [Particle() for _ in range(100)]
    
    for p in particles:
        p.position = glm.vec3(random.uniform(-2.5, 2.5), 0.0, random.uniform(-2.5, 2.5))
        p.velocity = glm.vec3(0.0, 0.02, 0.0)
        p.life = random.uniform(0, 2)

    particle_vao = glGenVertexArrays(1)
    particle_vbo = glGenBuffers(1)
    
    glBindVertexArray(particle_vao)
    glBindBuffer(GL_ARRAY_BUFFER, particle_vbo)
    glBufferData(GL_ARRAY_BUFFER, len(particles) * 28, None, GL_DYNAMIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(0))
    glBindVertexArray(0)

def update_particles():
    if not polluted_mode:
        return
    
    for p in particles:
        p.position += p.velocity
        p.life -= 0.01
        if p.life <= 0:
            p.position = glm.vec3(random.uniform(-2.5, 2.5), 0.0, random.uniform(-2.5, 2.5))
            p.life = random.uniform(0, 2)

def render_particles():
    if not polluted_mode:
        return
    
    glBindVertexArray(particle_vao)
    data = np.array([(p.position.x, p.position.y, p.position.z, 
                     p.velocity.x, p.velocity.y, p.velocity.z, p.life)
                    for p in particles], dtype=np.float32)
    glBufferSubData(GL_ARRAY_BUFFER, 0, data.nbytes, data)
    glDrawArrays(GL_POINTS, 0, len(particles))
    glBindVertexArray(0)

def create_bsp_tree(polygons):
    if not polygons:
        return None
    
    node = BSPNode()
    node.polygons.append(polygons[0])
    node.normal = glm.normalize(glm.cross(
        polygons[0][1] - polygons[0][0],
        polygons[0][2] - polygons[0][0]
    ))
    node.distance = glm.dot(node.normal, polygons[0][0])

    front_polys = []
    back_polys = []
    
    for poly in polygons[1:]:
        d = glm.dot(node.normal, poly[0]) - node.distance
        if d > 0.01:
            front_polys.append(poly)
        elif d < -0.01:
            back_polys.append(poly)

    node.front = create_bsp_tree(front_polys)
    node.back = create_bsp_tree(back_polys)
    return node

def render_bsp(node):
    if not node:
        return
    
    camera_in_front = glm.dot(node.normal, camera_pos) > node.distance
    
    if not camera_in_front:
        render_bsp(node.back)

    glBindVertexArray(vao)
    for polygon in node.polygons:
        vertices = np.array([[v.x, v.y, v.z] for v in polygon], dtype=np.float32).flatten()
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
        glDrawArrays(GL_TRIANGLES, 0, len(polygon))
    glBindVertexArray(0)

    if camera_in_front:
        render_bsp(node.front)

def save_screenshot(filename):
    pixels = glReadPixels(0, 0, window_width, window_height, GL_RGB, GL_UNSIGNED_BYTE)
    with open(filename, 'wb') as f:
        f.write(f'P6\n{window_width} {window_height}\n255\n'.encode())
        f.write(pixels)

def render_scene(root):
    view = glm.lookAt(camera_pos, camera_pos + camera_front, camera_up)
    projection = glm.perspective(glm.radians(45.0), 
                               window_width / window_height, 0.1, 100.0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    shader.use()
    shader.set_mat4("view", view)
    shader.set_mat4("projection", projection)

    fog_color = glm.vec3(0.5, 0.4, 0.3) if polluted_mode else glm.vec3(0.7, 0.9, 1.0)
    shader.set_vec3("fogColor", fog_color)

    render_bsp(root)
    update_particles()
    render_particles()

def process_input(window):
    global polluted_mode, p_key_pressed
    if glfw.get_key(window, glfw.KEY_P) == glfw.PRESS and not p_key_pressed:
        polluted_mode = not polluted_mode
        save_screenshot("polluted_scene.ppm" if polluted_mode else "clean_scene.ppm")
        p_key_pressed = True
    if glfw.get_key(window, glfw.KEY_P) == glfw.RELEASE:
        p_key_pressed = False

def main():
    global vao, vbo, shader, window

    if not glfw.init():
        print("GLFW initialization failed")
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(window_width, window_height, 
                              "Pollution Awareness Renderer", None, None)
    if not window:
        print("Window creation failed")
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        shader = Shader(os.path.join(script_dir, "vertex.glsl"),
                       os.path.join(script_dir, "fragment.glsl"))
    except Exception as e:
        print(f"Shader error: {e}")
        glfw.terminate()
        return

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glBindVertexArray(0)

    polygons = [[glm.vec3(-3.0, 0.0, -3.0),
                glm.vec3(1.0, 5.0, -3.0),
                glm.vec3(2.0, 3.0, -2.0)]]
    bsp_tree = create_bsp_tree(polygons)
    init_particles()

    while not glfw.window_should_close(window):
        process_input(window)
        render_scene(bsp_tree)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()