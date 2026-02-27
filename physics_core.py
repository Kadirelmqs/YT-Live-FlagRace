import pymunk
import math
from settings import *
# from flag_handler import flag_manager


# --- PHYSICS FUNCTIONS ---

def rebuild_circle_segments(space, body, radius, gap_angle_deg):
    for shape in list(space.shapes):
        if shape.body == body and isinstance(shape, pymunk.Segment):
            space.remove(shape)
    
    res = 120
    gap_start = -gap_angle_deg / 2
    gap_end = gap_angle_deg / 2
    
    for i in range(res):
        angle_start = (i / res) * 360
        angle_end = ((i + 1) / res) * 360
        if gap_start <= (angle_start - 50) <= gap_end:
            continue
        as_rad = math.radians(angle_start)
        ae_rad = math.radians(angle_end)
        p1 = (radius * math.cos(as_rad), radius * math.sin(as_rad))
        p2 = (radius * math.cos(ae_rad), radius * math.sin(ae_rad))
        
        segment = pymunk.Segment(body, p1, p2, INTERNAL_SETTINGS["wall_thickness"])
        segment.elasticity = INTERNAL_SETTINGS["elasticity"]
        segment.friction = 0.5 
        segment.color = (0, 255, 0, 255) 
        space.add(segment)

def create_circle_body(space, pos, rotation_speed):
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position = pos
    body.angular_velocity = rotation_speed
    space.add(body)
    return body

def limit_velocity(body, gravity, damping, dt):
    pymunk.Body.update_velocity(body, gravity, damping, dt)
    l = body.velocity.length
    if l > MAX_VELOCITY:
        scale = MAX_VELOCITY / l
        body.velocity = body.velocity * scale

def spawn_flag(space, pos, radius, specific_data=None):
    mass = 10 
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = pos
    body.velocity_func = limit_velocity
    
    shape = pymunk.Circle(body, radius)
    shape.elasticity = INTERNAL_SETTINGS["elasticity"]
    shape.friction = 0.5 
    
    w = radius * 2.2
    h = radius * 1.5
    
    if specific_data:
        shape.custom_data = specific_data
    else:
        shape.custom_data = flag_manager.get_random_flag(w, h)
        
    space.add(body, shape)
    return shape
