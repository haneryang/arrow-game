# -*- coding: utf-8 -*-
"""
一箭又一箭 - 串珠风格丰富版
学号：102402154
运行：python arrow_game.py
依赖：pip install pygame-ce
操作：鼠标点箭头 / R重开 / Esc暂停 / U撤销 / H提示
"""
import pygame, sys, time, random

# ============ 配置 ============
CELL = 64
MARGIN_X = 110
TOP_BAR = 90
BOTTOM_BAR = 90
ROWS, COLS = 6, 6
BOARD_W = CELL * COLS
BOARD_H = CELL * ROWS
WIDTH = MARGIN_X * 2 + BOARD_W
HEIGHT = TOP_BAR + BOARD_H + BOTTOM_BAR

# 方向 0=上 1=右 2=下 3=左
DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]
ARROW_CH = ["^", ">", "v", "<"]

WOOD = (120, 72, 40)
WOOD_DARK = (80, 45, 25)
MAT = (38, 48, 72)
MAT_EDGE = (90, 110, 150)
WHITE = (245, 240, 225)
ORANGE = (245, 165, 60)
ORANGE_DARK = (200, 120, 30)
RED = (220, 70, 70)
GREEN = (110, 200, 130)
GRAY = (150, 155, 165)
GOLD = (255, 215, 100)

BEAD_COLOR = [
    (90, 160, 230),    # 上 蓝
    (220, 140, 80),    # 右 橙棕
    (140, 180, 220),   # 下 浅蓝
    (180, 130, 200),   # 左 紫
]

# 5 个关卡：0空 1上 2右 3下 4左
LEVELS = [
    # L1: 入门
    [
        [0,0,0,0,0,0],
        [0,2,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,2,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
    ],
    # L2: 四向
    [
        [0,0,0,0,0,0],
        [0,1,0,0,3,0],
        [0,0,0,0,0,0],
        [0,4,0,0,2,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
    ],
    # L3: 连锁
    [
        [0,0,0,0,0,0],
        [0,2,0,2,0,0],
        [0,0,0,0,0,0],
        [0,1,0,3,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
    ],
    # L4: 稍密
    [
        [0,1,0,0,3,0],
        [0,0,0,0,0,0],
        [4,0,2,0,0,2],
        [0,0,0,0,0,0],
        [0,3,0,0,2,0],
        [0,0,0,0,0,0],
    ],
    # L5: 终关
    [
        [1,0,0,0,0,3],
        [0,0,2,0,1,0],
        [0,0,0,0,0,0],
        [0,4,0,0,2,0],
        [0,0,0,3,0,0],
        [4,0,1,0,0,0],
    ],
]

MAX_MISTAKES = 3


def round_rect(surf, rect, radius, color, width=0):
    pygame.draw.rect(surf, color, rect, width, border_radius=radius)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("一箭又一箭 - 102402154")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(["microsoftyahei","Microsoft YaHei","simhei","arial"], 20)
        self.small_font = pygame.font.SysFont(["microsoftyahei","Microsoft YaHei","simhei","arial"], 16)
        self.big_font = pygame.font.SysFont(["microsoftyahei","Microsoft YaHei","simhei","arial"], 52, bold=True)
        self.mid_font = pygame.font.SysFont(["microsoftyahei","Microsoft YaHei","simhei","arial"], 30, bold=True)
        self.state = "start"   # start/play/pause/win_next/win_final/fail
        self.start_btn = None
        self.pause_btns = {}
        self.reset_level(0)

    def reset_level(self, lv):
        self.level = lv
        self.grid = [r[:] for r in LEVELS[lv]]
        self.mistakes = 0
        self.score = 0
        self.combo = 0
        self.best_combo = 0
        self.shake = None
        self.fly_out = None
        self.collide = None
        self.hint = None
        self.history = []   # 撤销栈: (r,c,dir)
        self.start_time = time.time()

    def count_arrows(self):
        return sum(1 for row in self.grid for v in row if v)

    def can_fly(self, r, c, d):
        nr, nc = r+DY[d], c+DX[d]
        while 0 <= nr < ROWS and 0 <= nc < COLS:
            if self.grid[nr][nc]:
                return False
            nr += DY[d]; nc += DX[d]
        return True

    def click(self, r, c):
        v = self.grid[r][c]
        if not v: return
        d = v - 1
        if self.can_fly(r, c, d):
            self.fly_out = (r, c, d, 0)
            self.grid[r][c] = 0
            self.combo += 1
            self.best_combo = max(self.best_combo, self.combo)
            self.score += 100 * self.combo
            self.history.append((r, c, d))
            self.hint = None
        else:
            self.mistakes += 1
            self.combo = 0
            self.collide = (r, c, d, 0)
            if self.mistakes >= MAX_MISTAKES:
                self.state = "fail"

    def undo(self):
        if not self.history or self.state != "play":
            return
        r, c, d = self.history.pop()
        self.grid[r][c] = d + 1
        self.combo = 0
        self.score = max(0, self.score - 100)

    def give_hint(self):
        if self.state != "play": return
        for r in range(ROWS):
            for c in range(COLS):
                v = self.grid[r][c]
                if v and self.can_fly(r, c, v-1):
                    self.hint = (r, c)
                    return

    def check_win(self):
        if self.count_arrows() == 0:
            self.state = "win_next" if self.level < len(LEVELS)-1 else "win_final"

    # ---------- 绘制 ----------
    def draw_wood_bg(self):
        self.screen.fill(WOOD)
        for y in range(0, HEIGHT, 36):
            pygame.draw.line(self.screen, WOOD_DARK, (0, y), (WIDTH, y), 1)

    def draw_bead(self, x, y, direction, color, r=22, glow=False):
        if glow:
            pygame.draw.circle(self.screen, GOLD, (x, y), r+6, 2)
        pygame.draw.circle(self.screen, (20,20,30), (x+2, y+3), r)
        pygame.draw.circle(self.screen, color, (x, y), r)
        pygame.draw.circle(self.screen, (255,255,255), (x-6, y-6), r//3)
        txt = self.mid_font.render(ARROW_CH[direction], True, WHITE)
        self.screen.blit(txt, (x-txt.get_width()//2, y-txt.get_height()//2))

    def draw_heart(self, x, y, color):
        pygame.draw.circle(self.screen, color, (x-6, y-4), 7)
        pygame.draw.circle(self.screen, color, (x+6, y-4), 7)
        pygame.draw.polygon(self.screen, color, [(x-12,y-2),(x+12,y-2),(x,y+12)])

    def draw_top_bar(self):
        bar = pygame.Rect(0, 0, WIDTH, TOP_BAR)
        pygame.draw.rect(self.screen, MAT, bar)
        pygame.draw.line(self.screen, MAT_EDGE, (0, TOP_BAR-2), (WIDTH, TOP_BAR-2), 2)
        lv = self.font.render(f"LEVEL {self.level+1}/{len(LEVELS)}", True, WHITE)
        self.screen.blit(lv, (20, 15))
        sc = self.small_font.render(f"SCORE {self.score}", True, GOLD)
        self.screen.blit(sc, (20, 48))
        elapsed = int(time.time() - self.start_time) if self.state == "play" else 0
        t = self.font.render(f"TIME {elapsed//60:02d}:{elapsed%60:02d}", True, WHITE)
        self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 30))
        for i in range(MAX_MISTAKES):
            filled = i < MAX_MISTAKES - self.mistakes
            self.draw_heart(WIDTH-180+i*38, 35, RED if filled else GRAY)
        # 暂停按钮
        btn = pygame.Rect(WIDTH-50, 20, 30, 30)
        pygame.draw.rect(self.screen, GRAY, btn, 2, border_radius=4)
        pygame.draw.line(self.screen, WHITE, (WIDTH-40, 27), (WIDTH-40, 43), 3)
        pygame.draw.line(self.screen, WHITE, (WIDTH-30, 27), (WIDTH-30, 43), 3)

    def draw_board(self):
        rect = pygame.Rect(MARGIN_X-15, TOP_BAR+15, BOARD_W+30, BOARD_H+30)
        round_rect(self.screen, rect, 20, MAT)
        pygame.draw.rect(self.screen, MAT_EDGE, rect, 2, border_radius=20)

        for r in range(ROWS):
            for c in range(COLS):
                x = MARGIN_X + c*CELL + CELL//2
                y = TOP_BAR + r*CELL + CELL//2 + 15
                v = self.grid[r][c]
                if v:
                    color = BEAD_COLOR[v-1]
                    if self.shake and self.shake[0]==r and self.shake[1]==c:
                        if self.shake[2] // 4 % 2 == 0:
                            color = RED
                    glow = self.hint == (r, c)
                    self.draw_bead(x, y, v-1, color, glow=glow)

        if self.collide:
            r, c, d, f = self.collide
            # 前10帧朝blocker走，后10帧退回
            if f < 10:
                ox = DX[d]*f*3; oy = DY[d]*f*3
            else:
                ox = DX[d]*(20-f)*3; oy = DY[d]*(20-f)*3
            x = MARGIN_X + c*CELL + CELL//2 + ox
            y = TOP_BAR + r*CELL + CELL//2 + 15 + oy
            self.draw_bead(x, y, self.grid[r][c]-1 if self.grid[r][c] else 0, RED)

        if self.fly_out:
            r, c, d, f = self.fly_out
            ox = MARGIN_X + c*CELL + CELL//2 + DX[d]*f*12
            oy = TOP_BAR + r*CELL + CELL//2 + 15 + DY[d]*f*12
            self.draw_bead(ox, oy, d, GREEN, r=18)

    def draw_bottom_bar(self):
        y = TOP_BAR + BOARD_H + 30
        items = [("R 重开", 30), ("U 撤销", 130), ("H 提示", 230), ("Esc 暂停", 330)]
        for text, x in items:
            t = self.small_font.render(text, True, WHITE)
            self.screen.blit(t, (x, y))
        if self.combo >= 2:
            cb = self.mid_font.render(f"x{self.combo} COMBO!", True, ORANGE)
            self.screen.blit(cb, (WIDTH-180, y-5))

    def draw_start(self):
        self.draw_wood_bg()
        rect = pygame.Rect(WIDTH//2-340, 110, 680, 480)
        round_rect(self.screen, rect, 24, MAT)
        pygame.draw.rect(self.screen, MAT_EDGE, rect, 3, border_radius=24)
        t1 = self.big_font.render("一箭又一箭", True, WHITE)
        self.screen.blit(t1, (WIDTH//2-t1.get_width()//2, 180))
        t2 = self.font.render("Arrow Puzzle · 102402154", True, GRAY)
        self.screen.blit(t2, (WIDTH//2-t2.get_width()//2, 260))
        # 玩法说明
        lines = [
            "点击箭头，沿方向无阻挡即可飞出",
            "被挡住会扣一次生命，共 3 次机会",
            "清空全部箭头进入下一关",
        ]
        for i, line in enumerate(lines):
            tl = self.small_font.render(line, True, WHITE)
            self.screen.blit(tl, (WIDTH//2-tl.get_width()//2, 310+i*28))
        btn = pygame.Rect(WIDTH//2-130, 420, 260, 64)
        round_rect(self.screen, btn, 16, ORANGE)
        pygame.draw.rect(self.screen, ORANGE_DARK, btn, 3, border_radius=16)
        bt = self.mid_font.render("开始游戏", True, (60,30,10))
        self.screen.blit(bt, (WIDTH//2-bt.get_width()//2, 435))
        self.start_btn = btn

    def draw_pause(self):
        self.draw_wood_bg(); self.draw_top_bar(); self.draw_board()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        self.screen.blit(overlay, (0,0))
        t = self.big_font.render("暂停", True, WHITE)
        self.screen.blit(t, (WIDTH//2-t.get_width()//2, 150))
        buttons = [("继续", 260), ("重开本关", 340), ("返回主菜单", 420)]
        self.pause_btns = {}
        for text, y in buttons:
            btn = pygame.Rect(WIDTH//2-110, y, 220, 50)
            round_rect(self.screen, btn, 10, ORANGE)
            t = self.font.render(text, True, (60,30,10))
            self.screen.blit(t, (WIDTH//2-t.get_width()//2, y+13))
            self.pause_btns[text] = btn

    def draw_end(self):
        self.draw_wood_bg(); self.draw_top_bar(); self.draw_board()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        self.screen.blit(overlay, (0,0))
        if self.state == "fail":
            txt = self.big_font.render("游戏失败", True, RED)
        elif self.state == "win_final":
            txt = self.big_font.render("全部通关！", True, GREEN)
        else:
            txt = self.big_font.render(f"第{self.level+1}关通过", True, GREEN)
        self.screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT//2-80))
        info = self.small_font.render(f"得分 {self.score}   最高连击 x{self.best_combo}", True, GOLD)
        self.screen.blit(info, (WIDTH//2-info.get_width()//2, HEIGHT//2))
        tip = self.font.render("点击任意处继续", True, WHITE)
        self.screen.blit(tip, (WIDTH//2-tip.get_width()//2, HEIGHT//2+50))

    def draw(self):
        if self.state == "start":
            self.draw_start()
        elif self.state == "pause":
            self.draw_pause()
        elif self.state in ("fail","win_next","win_final"):
            self.draw_end()
        else:
            self.draw_wood_bg()
            self.draw_top_bar()
            self.draw_board()
            self.draw_bottom_bar()
        pygame.display.flip()

    def handle_click(self, mx, my):
        if self.state == "start":
            self.reset_level(0); self.state = "play"
        elif self.state in ("fail","win_next","win_final"):
            if self.state == "win_next":
                self.reset_level(self.level+1)
            elif self.state == "win_final":
                self.reset_level(0)
            else:
                self.reset_level(self.level)
            self.state = "play"
        elif self.state == "pause":
            for text, btn in self.pause_btns.items():
                if btn.collidepoint(mx, my):
                    if text == "继续":
                        self.state = "play"
                    elif text == "重开本关":
                        self.reset_level(self.level); self.state = "play"
                    else:
                        self.state = "start"
                    return
        elif self.state == "play":
            # 暂停按钮
            if pygame.Rect(WIDTH-50, 20, 30, 30).collidepoint(mx, my):
                self.state = "pause"; return
            c = (mx - MARGIN_X) // CELL
            r = (my - TOP_BAR - 15) // CELL
            if 0 <= r < ROWS and 0 <= c < COLS:
                self.click(r, c); self.check_win()

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(*e.pos)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r and self.state == "play":
                        self.reset_level(self.level)
                    elif e.key == pygame.K_u and self.state == "play":
                        self.undo()
                    elif e.key == pygame.K_h and self.state == "play":
                        self.give_hint()
                    elif e.key == pygame.K_ESCAPE:
                        if self.state == "play":
                            self.state = "pause"
                        elif self.state == "pause":
                            self.state = "play"

            if self.shake:
                self.shake = (self.shake[0], self.shake[1], self.shake[2]+1)
                if self.shake[2] > 18: self.shake = None
            if self.fly_out:
                self.fly_out = (self.fly_out[0], self.fly_out[1], self.fly_out[2], self.fly_out[3]+1)
                if self.fly_out[3] > 20: self.fly_out = None
            if self.collide:
                self.collide = (self.collide[0], self.collide[1], self.collide[2], self.collide[3]+1)
                if self.collide[3] > 20:
                    self.shake = (self.collide[0], self.collide[1], 0)
                    self.collide = None

            self.draw()
            self.clock.tick(30)


if __name__ == "__main__":
    Game().run()
