import pgzrun
import pygame
import random
import math
import os

# 定义游戏相关属性
TITLE = '鸡了个鸡'
WIDTH = 600
HEIGHT = 720

# 自定义游戏常量
T_WIDTH = 60
T_HEIGHT = 66

# 下方牌堆的位置
DOCK = Rect((90, 564), (T_WIDTH * 7, T_HEIGHT))

# 游戏状态
game_started = False
game_failed = False  # 游戏失败标志
countdown_time = 480  # 倒计时时间（秒），设置为480秒
time_left = countdown_time  # 剩余时间

# 上方的所有牌
tiles = []
# 牌堆里的牌
docks = []

# 分数系统和排行榜
score = 0  # 当前分数
high_scores = []  # 排行榜，存储最高分

# 自定义类Tile
class Tile(Actor):
    def __init__(self, image, tag, pos, layer, status=0):
        super().__init__(image)
        self.tag = tag  # 牌的种类
        self.layer = layer  # 牌的层级
        self.status = status  # 牌的状态
        self.pos = pos  # 牌的位置

# 读取和保存最高分
def load_high_scores():
    global high_scores
    if os.path.exists('high_scores.txt'):
        with open('high_scores.txt', 'r') as file:
            high_scores = [int(line.strip()) for line in file.readlines()]
    else:
        high_scores = []

def save_high_scores():
    with open('high_scores.txt', 'w') as file:
        for score in high_scores:
            file.write(f"{score}\n")

# 更新排行榜
def update_high_scores(new_score):
    global high_scores
    high_scores.append(new_score)
    high_scores = sorted(high_scores, reverse=True)[:5]  # 只保存前5名

# 游戏开始界面
def draw_start_screen():
    global start_button_rect

    # 绘制背景色为绿色
    screen.fill((0, 255, 0))  # 背景色绿色

    # 读取原始图像
    start_image = pygame.image.load('images/start_screen.png')
    image_width, image_height = start_image.get_size()
    x = (WIDTH - image_width) // 2
    y = (HEIGHT - image_height) // 2
    screen.blit(start_image, (x, y))

    start_button_rect = pygame.Rect(x, y, image_width, image_height)

# 绘制游戏帧
def draw():
    if not game_started:
        draw_start_screen()
    else:
        screen.clear()
        screen.blit('back.png', (0, 0))  # 背景图
        for tile in tiles:
            tile.draw()
            if tile.status == 0:
                screen.blit('mask.png', tile.topleft)
        for i, tile in enumerate(docks):
            tile.left = (DOCK.x + i * T_WIDTH)
            tile.top = DOCK.y
            tile.draw()

        # 超过7张，失败
        if len(docks) >= 7:
            screen.blit('end.png', (0, 0))
            draw_game_over()
        elif len(tiles) == 0:
            screen.blit('win.png', (0, 0))
            draw_game_over()
        elif game_failed:
            screen.blit('end.png', (0, 0))
            draw_game_over()
        else:
            # 绘制倒计时
            time_text = f"Time Left: {int(time_left)}"
            screen.draw.text(time_text, center=(WIDTH // 2, 50), fontsize=36, color="red")

            # 显示分数
            score_text = f"Score: {score}"
            screen.draw.text(score_text, topleft=(10, 10), fontsize=30, color="white")

# 显示游戏结束和排行榜
def draw_game_over():
    global score
    update_high_scores(score)  # 更新排行榜
    save_high_scores()

    # 绘制排行榜
    screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2), fontsize=50, color="white")
    screen.draw.text("High Scores:", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=40, color="yellow")
    for i, hs in enumerate(high_scores):
        screen.draw.text(f"{i + 1}. {hs}", center=(WIDTH // 2, HEIGHT // 2 + 100 + i * 30), fontsize=30, color="white")

    # 绘制“重新开始”按钮
    global restart_button_rect
    restart_button_image = pygame.image.load('images/restart_button.png')
    restart_button_width, restart_button_height = restart_button_image.get_size()
    restart_button_x = (WIDTH - restart_button_width) // 2
    restart_button_y = 20  # 将按钮放在窗口上方
    screen.blit(restart_button_image, (restart_button_x, restart_button_y))
    restart_button_rect = pygame.Rect(restart_button_x, restart_button_y, restart_button_width, restart_button_height)

# 鼠标点击响应
def on_mouse_down(pos):
    global docks, game_started, game_failed, score
    if not game_started:
        if pygame.mouse.get_pressed()[0]:
            if start_button_rect.collidepoint(pos):
                game_started = True
                initialize_game()
        return

    if len(docks) >= 7 or len(tiles) == 0 or game_failed:
        if pygame.mouse.get_pressed()[0]:
            if restart_button_rect.collidepoint(pos):
                initialize_game()
                return

    for tile in reversed(tiles):
        if tile.status == 1 and tile.collidepoint(pos):
            tile.status = 2
            tiles.remove(tile)
            diff = [t for t in docks if t.tag != tile.tag]
            if len(docks) - len(diff) < 2:
                docks.append(tile)
            else:
                docks = diff
                score += 100  # 成功消除一组牌，增加分数
            for down in tiles:
                if down.layer == tile.layer - 1 and down.colliderect(tile):
                    for up in tiles:
                        if up.layer == down.layer + 1 and up.colliderect(down):
                            break
                    else:
                        down.status = 1
            return

# 初始化游戏
def initialize_game():
    global tiles, docks, game_failed, time_left, score
    tiles.clear()
    docks.clear()
    game_failed = False
    time_left = countdown_time
    score = 0  # 重置分数

    ts = list(range(1, 13)) * 12
    random.shuffle(ts)
    n = 0
    for k in range(7):
        for i in range(7 - k):
            for j in range(7 - k):
                t = ts[n]
                n += 1
                tile = Tile(f'tile{t}', t, (120 + (k * 0.5 + j) * T_WIDTH, 100 + (k * 0.5 + i) * T_HEIGHT * 0.9), k,
                            1 if k == 6 else 0)
                tiles.append(tile)
    for i in range(4):
        t = ts[n]
        n += 1
        tile = Tile(f'tile{t}', t, (210 + i * T_WIDTH, 516), 0, 1)
        tiles.append(tile)

# 每帧调用一次
def update():
    global time_left, game_failed
    if game_started and not game_failed:
        time_left -= 1 / 60
        if time_left <= 0:
            time_left = 0
            game_failed = True

# 加载排行榜
load_high_scores()

# 播放背景音乐
music.play('bgm')

pgzrun.go()