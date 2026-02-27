LEADERBOARD = {}
NEXT_ROUND_QUEUE = {}
IS_CHAT_RUNNING = False
is_round_recorded = False

# --- OYUN DURUMLARI ---
STATE_MENU = 0
STATE_COUNTDOWN = 1
STATE_GAME = 2
STATE_WINNER = 3

current_state = STATE_MENU
game_objects = []
space = None
circle_body = None
round_start_time = 0
winner_obj = None
