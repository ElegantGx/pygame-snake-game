import pygame
import random
import sys

pygame.init()

# ==================== 常量 =======================
W, H = 800, 600
CELL = 20
GRID_W, GRID_H = W // CELL, H // CELL

COLORS = {
    'BLACK': (0, 0, 0), 'WHITE': (255, 255, 255), 'GREEN': (0, 255, 0),
    'RED': (255, 0, 0), 'DARK_GREEN': (0, 200, 0), 'YELLOW': (255, 255, 0),
    'GRAY': (128, 128, 128), 'BLUE': (0, 0, 255), 'LIGHT_BLUE': (100, 100, 255)
}

# 方向
UP, RIGHT, DOWN, LEFT = range(4)
DIR_VECT = {UP: (0, -1), RIGHT: (1, 0), DOWN: (0, 1), LEFT: (-1, 0)}

MODE_TRAD, MODE_LR = 0, 1
SNAKE_SPEED = 10
FPS_OPTS = [10, 30, 60]

LANG_CN, LANG_EN = 0, 1

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
pygame.key.set_repeat(0)

# ==================== 字体 ====================
def load_font(size):
    for name in ['simhei', 'microsoft yahei', 'simsun', 'noto sans cjk sc', 'droidsansfallback']:
        path = pygame.font.match_font(name)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)

font = load_font(30)
big_font = load_font(60)
CHINESE_OK = font.render('测', True, COLORS['WHITE']).get_width() > 0

# ==================== 多语言文本 ====================
TEXTS = {
    LANG_CN: {
        'title': '贪吃蛇', 'press_enter': '按 Enter 开始游戏',
        'settings': '设置', 'how_to_play': '操作说明',
        'fps': '帧率', 'mode': '操作模式',
        'mode_traditional': '传统模式（方向键）', 'mode_leftright': '左右转向模式',
        'language': '语言', 'chinese': '简体中文', 'english': 'English',
        'back': '返回', 'game_over': '游戏结束', 'you_win': '胜利！', 'score': '得分',
        'restart': '重新开始', 'menu': '主菜单',
        'how_to_play_title': '操作说明',
        'how_to_traditional': '使用 ↑ ↓ ← → 控制蛇的移动\n不能直接反向',
        'how_to_leftright': '使用 ← → 控制蛇的转向\n左转逆时针，右转顺时针',
        'common_controls': '游戏结束按 R 重开，按 M 返回菜单',
        'any_key': '按任意键返回'
    },
    LANG_EN: {
        'title': 'Snake Game', 'press_enter': 'Press ENTER to start',
        'settings': 'Settings', 'how_to_play': 'How to Play',
        'fps': 'FPS', 'mode': 'Control Mode',
        'mode_traditional': 'Traditional (Arrow Keys)', 'mode_leftright': 'Left/Right Turn',
        'language': 'Language', 'chinese': '简体中文', 'english': 'English',
        'back': 'Back', 'game_over': 'Game Over', 'you_win': 'You Win!', 'score': 'Score',
        'restart': 'Restart', 'menu': 'Menu',
        'how_to_play_title': 'How to Play',
        'how_to_traditional': 'Use ↑ ↓ ← → to move the snake\nCannot reverse direction directly',
        'how_to_leftright': 'Use ← → to turn the snake\nLeft turns counter-clockwise, right turns clockwise',
        'common_controls': 'Press R to restart, M to menu after game over',
        'any_key': 'Press any key to return'
    }
}

def text(key, lang):
    return TEXTS[lang][key]

# ==================== 辅助函数 ====================
def wait_mouse_release():
    """等待鼠标左键松开，防止按下状态传递到下一界面"""
    while pygame.mouse.get_pressed()[0]:
        pygame.event.pump()
        clock.tick(30)

# ==================== 通用绘制 ====================
def draw_rect(x, y, color):
    pygame.draw.rect(screen, color, (x*CELL, y*CELL, CELL, CELL))

def draw_button(text, x, y, w, h, color, hover):
    rect = pygame.Rect(x, y, w, h)
    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)
    if hovered:
        pygame.draw.rect(screen, hover, rect)
    else:
        pygame.draw.rect(screen, color, rect)
    surf = font.render(text, True, COLORS['WHITE'])
    screen.blit(surf, surf.get_rect(center=rect.center))
    return hovered

def draw_snake(snake):
    for s in snake:
        draw_rect(s[0], s[1], COLORS['GREEN'])
        pygame.draw.rect(screen, COLORS['DARK_GREEN'], (s[0]*CELL, s[1]*CELL, CELL, CELL), 1)

def draw_food(food):
    draw_rect(food[0], food[1], COLORS['RED'])

def draw_score(score, lang):
    surf = font.render(f"{text('score', lang)}: {score}", True, COLORS['WHITE'])
    screen.blit(surf, (10, 10))

# ==================== 游戏逻辑 ====================
def generate_food(snake):
    total = GRID_W * GRID_H
    if len(snake) >= total:
        return None
    while True:
        f = [random.randint(0, GRID_W-1), random.randint(0, GRID_H-1)]
        if f not in snake:
            return f

def game_loop(fps, mode, lang):
    pygame.event.clear()
    interval = max(1, fps // SNAKE_SPEED)
    snake = [[GRID_W//2, GRID_H//2]]
    dir = RIGHT
    next_dir = RIGHT
    food = generate_food(snake)
    if food is None:
        return end_screen(0, True, lang)
    score = 0
    move_cnt = 0
    turn_flag = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if mode == MODE_TRAD:
                    if event.key == pygame.K_UP and dir != DOWN: next_dir = UP
                    elif event.key == pygame.K_DOWN and dir != UP: next_dir = DOWN
                    elif event.key == pygame.K_LEFT and dir != RIGHT: next_dir = LEFT
                    elif event.key == pygame.K_RIGHT and dir != LEFT: next_dir = RIGHT
                else:  # MODE_LR
                    if not turn_flag:
                        if event.key == pygame.K_LEFT:
                            dir = (dir - 1) % 4; turn_flag = True
                        elif event.key == pygame.K_RIGHT:
                            dir = (dir + 1) % 4; turn_flag = True

        move_cnt += 1
        if move_cnt >= interval:
            move_cnt = 0
            if mode == MODE_TRAD:
                dir = next_dir
            else:
                turn_flag = False

            dx, dy = DIR_VECT[dir]
            head = [snake[0][0] + dx, snake[0][1] + dy]

            if head == food:
                snake.insert(0, head)
                score += 1
                food = generate_food(snake)
                if food is None:
                    return end_screen(score, True, lang)
            else:
                snake.insert(0, head)
                snake.pop()

            if (head[0] < 0 or head[0] >= GRID_W or
                head[1] < 0 or head[1] >= GRID_H or
                head in snake[1:]):
                return end_screen(score, False, lang)

        screen.fill(COLORS['BLACK'])
        draw_snake(snake)
        draw_food(food)
        draw_score(score, lang)
        pygame.display.update()
        clock.tick(fps)

def end_screen(score, win, lang):
    pygame.event.clear()
    last_mouse_click = pygame.mouse.get_pressed()[0]
    while True:
        screen.fill(COLORS['BLACK'])
        msg = text('you_win' if win else 'game_over', lang)
        color = COLORS['YELLOW'] if win else COLORS['WHITE']
        title = big_font.render(msg, True, color)
        screen.blit(title, (W//2 - title.get_width()//2, H//2 - 80))

        score_surf = font.render(f"{text('score', lang)}: {score}", True, COLORS['WHITE'])
        screen.blit(score_surf, (W//2 - score_surf.get_width()//2, H//2 - 20))

        restart_hover = draw_button(text('restart', lang), W//2-150, H//2+40, 120, 50, COLORS['GREEN'], COLORS['DARK_GREEN'])
        menu_hover = draw_button(text('menu', lang), W//2+30, H//2+40, 120, 50, COLORS['BLUE'], COLORS['LIGHT_BLUE'])

        hint = font.render("R - Restart | M - Menu", True, COLORS['WHITE'])
        screen.blit(hint, (W//2 - hint.get_width()//2, H//2+110))

        pygame.display.update()
        clock.tick(30)

        mouse_click = pygame.mouse.get_pressed()[0]
        if mouse_click and not last_mouse_click:
            if restart_hover:
                wait_mouse_release()          # 等待鼠标松开
                return 'restart'
            if menu_hover:
                wait_mouse_release()          # 等待鼠标松开
                return 'menu'
        last_mouse_click = mouse_click

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return 'restart'
                if event.key == pygame.K_m: return 'menu'

# ==================== 设置界面 ====================
def settings_screen(fps_idx, mode, lang):
    pygame.event.clear()
    last_mouse_click = pygame.mouse.get_pressed()[0]
    while True:
        screen.fill(COLORS['BLACK'])
        title = big_font.render(text('settings', lang), True, COLORS['WHITE'])
        screen.blit(title, (W//2 - title.get_width()//2, 50))

        fps_y = 150
        fps_txt = f"{text('fps', lang)}: {FPS_OPTS[fps_idx]}"
        fps_surf = font.render(fps_txt, True, COLORS['YELLOW'])
        fps_rect = fps_surf.get_rect(center=(W//2, fps_y))
        screen.blit(fps_surf, fps_rect)
        fps_hint = font.render("←  →", True, COLORS['GRAY'])
        screen.blit(fps_hint, (W//2 + fps_surf.get_width()//2 + 10, fps_y - 15))

        mode_y = 250
        mode_disp = text('mode_traditional', lang) if mode == MODE_TRAD else text('mode_leftright', lang)
        mode_surf = font.render(f"{text('mode', lang)}: {mode_disp}", True, COLORS['YELLOW'])
        mode_rect = mode_surf.get_rect(center=(W//2, mode_y))
        screen.blit(mode_surf, mode_rect)
        mode_hint = font.render("↑  ↓", True, COLORS['GRAY'])
        screen.blit(mode_hint, (W//2 + mode_surf.get_width()//2 + 10, mode_y - 15))

        lang_y = 350
        lang_disp = text('chinese', lang) if lang == LANG_CN else text('english', lang)
        lang_surf = font.render(f"{text('language', lang)}: {lang_disp}", True, COLORS['YELLOW'])
        lang_rect = lang_surf.get_rect(center=(W//2, lang_y))
        screen.blit(lang_surf, lang_rect)
        lang_hint = font.render("L", True, COLORS['GRAY'])
        screen.blit(lang_hint, (W//2 + lang_surf.get_width()//2 + 10, lang_y - 15))

        back_hover = draw_button(text('back', lang), W//2-60, 450, 120, 50, COLORS['GRAY'], (100,100,100))
        esc_hint = font.render("ESC", True, COLORS['GRAY'])
        screen.blit(esc_hint, (W//2 + 70, 465))

        pygame.display.update()
        clock.tick(30)

        mouse_click = pygame.mouse.get_pressed()[0]
        if mouse_click and not last_mouse_click:
            if fps_rect.collidepoint(pygame.mouse.get_pos()):
                fps_idx = (fps_idx + 1) % len(FPS_OPTS)
                pygame.time.wait(200)
            elif mode_rect.collidepoint(pygame.mouse.get_pos()):
                mode = MODE_LR if mode == MODE_TRAD else MODE_TRAD
                pygame.time.wait(200)
            elif lang_rect.collidepoint(pygame.mouse.get_pos()):
                new_lang = LANG_EN if lang == LANG_CN else LANG_CN
                if new_lang == LANG_CN and not CHINESE_OK:
                    warn = font.render("Chinese font not available", True, COLORS['RED'])
                    screen.blit(warn, (W//2 - warn.get_width()//2, 500))
                    pygame.display.update()
                    pygame.time.wait(1000)
                else:
                    lang = new_lang
                    pygame.time.wait(200)
            elif back_hover:
                wait_mouse_release()          # 等待鼠标松开
                return fps_idx, mode, lang
        last_mouse_click = mouse_click

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return fps_idx, mode, lang
                elif event.key == pygame.K_LEFT:
                    fps_idx = (fps_idx - 1) % len(FPS_OPTS)
                elif event.key == pygame.K_RIGHT:
                    fps_idx = (fps_idx + 1) % len(FPS_OPTS)
                elif event.key == pygame.K_UP:
                    mode = MODE_LR if mode == MODE_TRAD else MODE_TRAD
                elif event.key == pygame.K_DOWN:
                    mode = MODE_TRAD if mode == MODE_LR else MODE_LR
                elif event.key == pygame.K_l:
                    new_lang = LANG_EN if lang == LANG_CN else LANG_CN
                    if new_lang == LANG_CN and not CHINESE_OK:
                        warn = font.render("Chinese font not available", True, COLORS['RED'])
                        screen.blit(warn, (W//2 - warn.get_width()//2, 500))
                        pygame.display.update()
                        pygame.time.wait(1000)
                    else:
                        lang = new_lang

# ==================== 帮助界面 ====================
def help_screen(mode, lang):
    pygame.event.clear()
    while True:
        screen.fill(COLORS['BLACK'])
        title = big_font.render(text('how_to_play_title', lang), True, COLORS['YELLOW'])
        screen.blit(title, (W//2 - title.get_width()//2, 50))

        how = text('how_to_traditional' if mode == MODE_TRAD else 'how_to_leftright', lang)
        lines = how.split('\n')
        y = 200
        for line in lines:
            line_surf = font.render(line, True, COLORS['WHITE'])
            screen.blit(line_surf, (W//2 - line_surf.get_width()//2, y))
            y += 40

        common = text('common_controls', lang)
        common_surf = font.render(common, True, COLORS['WHITE'])
        screen.blit(common_surf, (W//2 - common_surf.get_width()//2, y + 20))

        back_hint = font.render(text('any_key', lang), True, COLORS['GRAY'])
        screen.blit(back_hint, (W//2 - back_hint.get_width()//2, H - 80))

        pygame.display.update()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                wait_mouse_release()          # 等待鼠标松开
                return

# ==================== 主菜单 ====================
def main():
    fps_idx = 0
    mode = MODE_TRAD
    lang = LANG_EN

    # 初始化鼠标状态
    main.last_click = pygame.mouse.get_pressed()[0]

    while True:
        screen.fill(COLORS['BLACK'])
        title = big_font.render(text('title', lang), True, COLORS['GREEN'])
        screen.blit(title, (W//2 - title.get_width()//2, 100))

        enter = font.render(text('press_enter', lang), True, COLORS['WHITE'])
        screen.blit(enter, (W//2 - enter.get_width()//2, 250))

        set_hover = draw_button(text('settings', lang), W//2-140, 350, 120, 50, COLORS['BLUE'], COLORS['LIGHT_BLUE'])
        how_hover = draw_button(text('how_to_play', lang), W//2+20, 350, 120, 50, COLORS['BLUE'], COLORS['LIGHT_BLUE'])

        hint = font.render("S - Settings | H - How to Play | Enter - Start", True, COLORS['GRAY'])
        screen.blit(hint, (W//2 - hint.get_width()//2, 450))

        pygame.display.update()
        clock.tick(30)

        # 鼠标点击检测（上升沿）
        mouse_click = pygame.mouse.get_pressed()[0]
        if mouse_click and not main.last_click:
            if set_hover:
                pygame.event.clear()
                fps_idx, mode, lang = settings_screen(fps_idx, mode, lang)
                main.last_click = pygame.mouse.get_pressed()[0]   # 重置鼠标状态
            elif how_hover:
                pygame.event.clear()
                help_screen(mode, lang)
                main.last_click = pygame.mouse.get_pressed()[0]   # 重置鼠标状态
        main.last_click = mouse_click

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    result = 'restart'
                    while result == 'restart':
                        result = game_loop(FPS_OPTS[fps_idx], mode, lang)
                    # 从游戏返回后，重置鼠标状态
                    main.last_click = pygame.mouse.get_pressed()[0]
                elif event.key == pygame.K_s:
                    pygame.event.clear()
                    fps_idx, mode, lang = settings_screen(fps_idx, mode, lang)
                    main.last_click = pygame.mouse.get_pressed()[0]
                elif event.key == pygame.K_h:
                    pygame.event.clear()
                    help_screen(mode, lang)
                    main.last_click = pygame.mouse.get_pressed()[0]

if __name__ == '__main__':
    main()
