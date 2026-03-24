import pymunk
import math
from settings import *
# from flag_handler import flag_manager


# --- PHYSICS FUNCTIONS ---

def rebuild_circle_segments(space, body, radius, gap_angle_deg):
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
    # --- HUNİ (FUNNEL) KOLLARINI EKLEME ---
    funnel_length = 100 # Huninin dışarı uzanan kollarının uzunluğu (Piksel)
    funnel_flare = 50   # Huninin ne kadar dışa açılacağı (Derece)
    
    # 1. Boşluğun başlangıç ve bitiş açılarını hesapla
    edge1_angle_deg = 50 + gap_start
    edge2_angle_deg = 50 + gap_end
    
    # 2. Çember üzerindeki kenar noktalarını bul
    p1_edge = (radius * math.cos(math.radians(edge1_angle_deg)), radius * math.sin(math.radians(edge1_angle_deg)))
    p2_edge = (radius * math.cos(math.radians(edge2_angle_deg)), radius * math.sin(math.radians(edge2_angle_deg)))
    
    # 3. Kolların dışarıya doğru uzanacağı açıları (V şekli) hesapla
    funnel_angle_1 = edge1_angle_deg - funnel_flare
    funnel_angle_2 = edge2_angle_deg + funnel_flare
    
    # 4. Kolların dış uç noktalarını hesapla
    p1_outer = (
        p1_edge[0] + funnel_length * math.cos(math.radians(funnel_angle_1)),
        p1_edge[1] + funnel_length * math.sin(math.radians(funnel_angle_1))
    )
    
    p2_outer = (
        p2_edge[0] + funnel_length * math.cos(math.radians(funnel_angle_2)),
        p2_edge[1] + funnel_length * math.sin(math.radians(funnel_angle_2))
    )
    
    # 5. Fizik motoruna 1. Huni Kolunu ekle
    funnel1 = pymunk.Segment(body, p1_edge, p1_outer, INTERNAL_SETTINGS["wall_thickness"])
    funnel1.elasticity = INTERNAL_SETTINGS["elasticity"]
    funnel1.friction = 0.5
    space.add(funnel1)
    
    # 6. Fizik motoruna 2. Huni Kolunu ekle
    funnel2 = pymunk.Segment(body, p2_edge, p2_outer, INTERNAL_SETTINGS["wall_thickness"])
    funnel2.elasticity = INTERNAL_SETTINGS["elasticity"]
    funnel2.friction = 0.5
    space.add(funnel2)

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

# def spawn_flag(space, pos, radius, specific_data=None):
def spawn_flag(space, pos, radius, specific_data=None, flag_manager=None):
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
    elif flag_manager:
        shape.custom_data = flag_manager.get_random_flag(w, h)
    else:
        shape.custom_data = {
            "image": pygame.Surface((int(w), int(h))),
            "name": "Unknown",
            "original": None
        }
        
    space.add(body, shape)
    return shape

