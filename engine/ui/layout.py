WINDOW_W, WINDOW_H = 1100, 720
MARGIN = 20
BOARD_COLS = 4

SLOT_W, SLOT_H = 180, 120
SLOT_GAP = 20

HAND_H = 180

def board_rects():
    total_w = BOARD_COLS * SLOT_W + (BOARD_COLS - 1) * SLOT_GAP
    start_x = (WINDOW_W - total_w) // 2
    enemy_y = 120
    player_y = enemy_y + SLOT_H + 120
    rects = { "enemy": [], "player": [] }
    for i in range(BOARD_COLS):
        x = start_x + i * (SLOT_W + SLOT_GAP)
        rects["enemy"].append((x, enemy_y, SLOT_W, SLOT_H))
        rects["player"].append((x, player_y, SLOT_W, SLOT_H))
    return rects

def hand_area():
    return (MARGIN, WINDOW_H - HAND_H - MARGIN, WINDOW_W - 2*MARGIN, HAND_H)
