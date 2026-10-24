# -*- coding: utf-8 -*-
"""
一箭又一箭 - 拼豆风格版
学号：102402154
操作：鼠标点箭头 / R重开 / U撤销 / H提示 / Esc暂停
"""
import pygame, sys, time, math

CELL = 60
MARGIN_X = 110
TOP_BAR = 90
BOTTOM_BAR = 80
ROWS, COLS = 7, 7
BOARD_W = CELL * COLS
BOARD_H = CELL * ROWS
WIDTH = MARGIN_X * 2 + BOARD_W
HEIGHT = TOP_BAR + BOARD_H + BOTTOM_BAR

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
BEAD_BG = (60, 72, 100)

BEAD_COLOR = [
    (90, 160, 230),
    (220, 140, 80),
    (140, 180, 220),
    (180, 130, 200),
]

# 每关: (grid, mask)
# mask=True 才是棋盘内格子，False 是背景外（不画格子）
# grid: 0=空, 1=上,2=右,3=下,4=左
def M(rows):
    return [[v != -1 for v in row] for row in rows]

LEVELS = [
    # L1: 入门小十字
    {
        "grid": [
            [0,0,0,0,0,0,0],
            [0,0,2,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,2,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
        ],
        "mask": [
            [0,0,0,0,0,0,0],
            [0,0,1,0,1,0,0],
            [0,0,1,0,1,0,0],
            [0,0,1,0,1,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
        ],
    },
    # L2: 四向方块
    {
        "grid": [
            [0,0,0,0,0,0,0],
            [0,1,0,0,3,0,0],
            [0,0,0,0,0,0,0],
            [0,4,0,0,2,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
        ],
        "mask": [
            [0,0,0,0,0,0,0],
            [0,1,1,1,1,0,0],
            [0,1,1,1,1,0,0],
            [0,1,1,1,1,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
        ],
    },
    # L3: 心形
    {
        "grid": [
            [0,0,0,0,0,0,0],
            [0,2,0,2,0,0,0],
            [0,0,0,0,0,0,0],
            [0,1,0,3,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
        ],
        "mask": [
            [0,1,1,1,1,0,0],
            [1,1,1,1,1,1,0],
            [1,1,1,1,1,1,0],
            [0,1,1,1,1,0,0],
            [0,0,1,1,0,0,0],
            [0,0,0,1,0,0,0],
            [0,0,0,0,0,0,0],
        ],
    },
    # L4: 花朵
    {
        "grid": [
            [0,0,1,0,0,0,0],
            [0,0,0,0,3,0,0],
            [4,0,2,0,0,2,0],
            [0,0,0,0,0,0,0],
            [0,3,0,0,2,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
        ],
        "mask": [
            [0,0,1,0,0,0,0],
            [0,1,1,1,1,0,0],
            [1,1,1,1,1,1,1],
            [0,1,1,1,1,0,0],
            [0,1,1,1,1,0,0],
            [0,0,1,0,0,0,0],
            [0,0,0,0,0,0,0],
        ],
    },
    # L5: 箭头阵
    {
        "grid": [
            [1,0,0,0,0,0,3],
            [0,0,2,0,1,0,0],
            [0,0,0,0,0,0,0],
            [0,4,0,0,2,0,0],
            [0,0,0,3,0,0,0],
            [4,0,1,0,0,0,0],
            [0,0,0,0,0,0,0],
        ],
        "mask": [
            [1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1],
            [0,0,0,0,0,0,0],
        ],
    },
    # L6: 终局
    {
        "grid": [
            [0,0,0,0,0,0,0],
            [0,2,0,0,0,2,0],
            [0,0,0,3,0,0,0],
            [1,0,0,0,0,0,2],
            [0,0,2,0,1,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
        ],
        "mask": [
            [0,1,1,1,1,1,0],
            [1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1],
            [0,1,1,1,1,1,0],
            [0,0,0,0,0,0,0],
        ],
    },
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
        self.small_font = pygame.font.SysFont(["microsoftyahei","Microsoft YaHei","simhei","arial"], 15)
        self.big_font = pygame.font.SysFont(["microsoftyahei","Microsoft YaHei","simhei","arial"], 48, bold=True)
        self.mid_font = pygame.font.SysFont(["microsoftyahei","Microsoft YaHei","simhei","arial"], 26, bold=True)
        self.state = "start"
        self.pause_btns = {}
        self.action_btns = {}
        self.reset_level(0)

    def reset_level(self, lv):
        self.level = lv
        lv_data = LEVELS[lv]
        self.grid = [r[:] for r in lv_data["grid"]]
        self.mask = [r[:] for r in lv_data["mask"]]
        self.mistakes = 0
        self.score = 0
        self.combo = 0
        self.best_combo = 0
        self.shake = None
        self.fly_out = None
        self.collide = None
        self.hint = None
        self.history = []
        self.start_time = time.time()
        self.level_time = 0

    def count_arrows(self):
        return sum(1 for row in self.grid for v in row if v)

    def in_mask(self, r, c):
        return 0 <= r < ROWS and 0 <= c < COLS and self.mask[r][c]

    def can_fly(self, r, c, d):
        nr, nc = r+DY[d], c+DX[d]
        while self.in_mask(nr, nc):
            if self.grid[nr][nc]:
                return False
            nr += DY[d]; nc += DX[d]
        return True

    def click(self, r, c):
        if not self.in_mask(r, c): return
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
        if not self.history or self.state != "play": return
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
                    self.hint = (r, c); return

    def stars(self):
        if self.mistakes == 0: return 3
        if self.mistakes == 1: return 2
        return 1

    def check_win(self):
        if self.count_arrows() == 0:
            self.level_time = int(time.time() - self.start_time)
            if self.level < len(LEVELS)-1:
                self.state = "win_next"
            else:
                self.state = "win_final"

    def draw_wood_bg(self):
        self.screen.fill(WOOD)
        for y in range(0, HEIGHT, 36):
            pygame.draw.line(self.screen, WOOD_DARK, (0, y), (WIDTH, y), 1)

    def draw_bead(self, x, y, direction, color, r=20, glow=False):
        if glow:
            pygame.draw.circle(self.screen, GOLD, (x, y), r+5, 2)
        pygame.draw.circle(self.screen, (20,20,30), (x+2, y+3), r)
        pygame.draw.circle(self.screen, color, (x, y), r)
        # 用三角形画箭头方向
        s = 9
        if direction == 0:    # 上
            pts = [(x, y-s), (x-s, y+s), (x+s, y+s)]
        elif direction == 1:  # 右
            pts = [(x+s, y), (x-s, y-s), (x-s, y+s)]
        elif direction == 2:  # 下
            pts = [(x, y+s), (x-s, y-s), (x+s, y-s)]
        else:                 # 左
            pts = [(x-s, y), (x+s, y-s), (x+s, y+s)]
        pygame.draw.polygon(self.screen, WHITE, pts)
        pygame.draw.polygon(self.screen, (255,255,255), pts, 2)

    def draw_heart(self, x, y, color):
        pygame.draw.circle(self.screen, color, (x-5, y-4), 6)
        pygame.draw.circle(self.screen, color, (x+5, y-4), 6)
        pygame.draw.polygon(self.screen, color, [(x-10,y-2),(x+10,y-2),(x,y+10)])

    def draw_star(self, x, y, filled, size=14):
        col = GOLD if filled else GRAY
        pts = []
        for i in range(10):
            ang = -3.14/2 + i * 3.14/5
            rad = size if i % 2 == 0 else size//2
            pts.append((x + rad*math.cos(ang), y + rad*math.sin(ang)))
        pygame.draw.polygon(self.screen, col, pts)

    def draw_top_bar(self):
        pygame.draw.rect(self.screen, MAT, (0, 0, WIDTH, TOP_BAR))
        pygame.draw.line(self.screen, MAT_EDGE, (0, TOP_BAR-2), (WIDTH, TOP_BAR-2), 2)
        self.screen.blit(self.font.render(f"LEVEL {self.level+1}/{len(LEVELS)}", True, WHITE), (20, 12))
        self.screen.blit(self.small_font.render(f"SCORE {self.score}", True, GOLD), (20, 45))
        elapsed = int(time.time() - self.start_time) if self.state == "play" else self.level_time
        self.screen.blit(self.font.render(f"TIME {elapsed//60:02d}:{elapsed%60:02d}", True, WHITE),
                         (WIDTH//2-40, 28))
        for i in range(MAX_MISTAKES):
            self.draw_heart(WIDTH-170+i*34, 35, RED if i < MAX_MISTAKES-self.mistakes else GRAY)
        pygame.draw.rect(self.screen, GRAY, (WIDTH-45, 18, 28, 28), 2, border_radius=4)
        pygame.draw.line(self.screen, WHITE, (WIDTH-36, 25), (WIDTH-36, 41), 3)
        pygame.draw.line(self.screen, WHITE, (WIDTH-27, 25), (WIDTH-27, 41), 3)

    def draw_board(self):
        rect = pygame.Rect(MARGIN_X-15, TOP_BAR+10, BOARD_W+30, BOARD_H+30)
        round_rect(self.screen, rect, 20, MAT)
        pygame.draw.rect(self.screen, MAT_EDGE, rect, 2, border_radius=20)
        for r in range(ROWS):
            for c in range(COLS):
                if not self.in_mask(r, c): continue
                x = MARGIN_X + c*CELL + CELL//2
                y = TOP_BAR + r*CELL + CELL//2 + 10
                pygame.draw.circle(self.screen, BEAD_BG, (x, y), 22)
                v = self.grid[r][c]
                if v:
                    color = BEAD_COLOR[v-1]
                    if self.shake and self.shake[0]==r and self.shake[1]==c and self.shake[2]//4%2==0:
                        color = RED
                    self.draw_bead(x, y, v-1, color, glow=(self.hint==(r,c)))
        if self.collide:
            r,c,d,f = self.collide
            ox = DX[d]*min(f,10)*3 - DX[d]*max(0,f-10)*3
            oy = DY[d]*min(f,10)*3 - DY[d]*max(0,f-10)*3
            x = MARGIN_X+c*CELL+CELL//2+ox
            y = TOP_BAR+r*CELL+CELL//2+10+oy
            if self.grid[r][c]:
                self.draw_bead(x, y, self.grid[r][c]-1, RED)
        if self.fly_out:
            r,c,d,f = self.fly_out
            x = MARGIN_X+c*CELL+CELL//2 + DX[d]*f*10
            y = TOP_BAR+r*CELL+CELL//2+10 + DY[d]*f*10
            self.draw_bead(x, y, d, GREEN, r=18)

    def draw_bottom_bar(self):
        y = TOP_BAR + BOARD_H + 25
        self.action_btns = {}
        labels = ["R重开", "U撤销", "H提示", "Esc暂停"]
        bw, gap = 78, 10
        total = len(labels) * bw + (len(labels)-1) * gap
        start_x = (WIDTH - total) // 2
        for i, text in enumerate(labels):
            x = start_x + i * (bw + gap)
            rect = pygame.Rect(x, y-5, bw, 30)
            round_rect(self.screen, rect, 6, (60,72,100))
            pygame.draw.rect(self.screen, MAT_EDGE, rect, 1, border_radius=6)
            self.screen.blit(self.small_font.render(text, True, WHITE), (x+12, y+3))
            self.action_btns[text] = rect
        if self.combo >= 2:
            self.screen.blit(self.mid_font.render(f"x{self.combo}", True, ORANGE), (WIDTH-120, y-5))

    def draw_start(self):
        self.draw_wood_bg()
        rect = pygame.Rect(WIDTH//2-320, 100, 640, 500)
        round_rect(self.screen, rect, 24, MAT)
        pygame.draw.rect(self.screen, MAT_EDGE, rect, 3, border_radius=24)
        self.screen.blit(self.big_font.render("一箭又一箭", True, WHITE),
                         (WIDTH//2-140, 160))
        self.screen.blit(self.small_font.render("Arrow Puzzle · 102402154", True, GRAY),
                         (WIDTH//2-100, 230))
        for i, line in enumerate(["点击箭头，沿方向无阻挡即可飞出",
                                   "被挡住扣一颗心，共 3 颗",
                                   "清空全部箭头进入下一关，共 6 关"]):
            self.screen.blit(self.small_font.render(line, True, WHITE),
                             (WIDTH//2-150, 280+i*26))
        btn = pygame.Rect(WIDTH//2-120, 400, 240, 60)
        round_rect(self.screen, btn, 14, ORANGE)
        pygame.draw.rect(self.screen, ORANGE_DARK, btn, 3, border_radius=14)
        self.screen.blit(self.mid_font.render("开始游戏", True, (60,30,10)),
                         (WIDTH//2-70, 415))

    def draw_pause(self):
        self.draw_wood_bg(); self.draw_top_bar(); self.draw_board()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,160)); self.screen.blit(overlay, (0,0))
        self.screen.blit(self.big_font.render("暂停", True, WHITE), (WIDTH//2-60, 150))
        self.pause_btns = {}
        for text, y in [("继续",260),("重开本关",330),("返回主菜单",400)]:
            btn = pygame.Rect(WIDTH//2-100, y, 200, 46)
            round_rect(self.screen, btn, 10, ORANGE)
            self.screen.blit(self.font.render(text, True, (60,30,10)),
                             (WIDTH//2-40, y+12))
            self.pause_btns[text] = btn

    def draw_end(self):
        self.draw_wood_bg(); self.draw_top_bar(); self.draw_board()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,150)); self.screen.blit(overlay, (0,0))
        if self.state == "fail":
            txt = self.big_font.render("游戏失败", True, RED)
            self.screen.blit(txt, (WIDTH//2-90, HEIGHT//2-100))
        else:
            txt = self.big_font.render("全部通关！" if self.state=="win_final" else f"第{self.level+1}关通过", True, GREEN)
            self.screen.blit(txt, (WIDTH//2-130, HEIGHT//2-130))
            # 星星
            s = self.stars()
            for i in range(3):
                self.draw_star(WIDTH//2-50+i*50, HEIGHT//2-50, i < s, 18)
        info = self.small_font.render(f"时间 {self.level_time//60:02d}:{self.level_time%60:02d}   得分 {self.score}   最高连击 x{self.best_combo}",
                                      True, GOLD)
        self.screen.blit(info, (WIDTH//2-160, HEIGHT//2+20))
        tip = self.font.render("点击任意处继续", True, WHITE)
        self.screen.blit(tip, (WIDTH//2-80, HEIGHT//2+60))

    def draw(self):
        if self.state == "start": self.draw_start()
        elif self.state == "pause": self.draw_pause()
        elif self.state in ("fail","win_next","win_final"): self.draw_end()
        else:
            self.draw_wood_bg(); self.draw_top_bar(); self.draw_board(); self.draw_bottom_bar()
        pygame.display.flip()

    def handle_click(self, mx, my):
        if self.state == "start":
            self.reset_level(0); self.state = "play"
        elif self.state in ("fail","win_next","win_final"):
            if self.state == "win_next": self.reset_level(self.level+1)
            elif self.state == "win_final": self.reset_level(0)
            else: self.reset_level(self.level)
            self.state = "play"
        elif self.state == "pause":
            for text, btn in self.pause_btns.items():
                if btn.collidepoint(mx, my):
                    if text == "继续": self.state = "play"
                    elif text == "重开本关": self.reset_level(self.level); self.state="play"
                    else: self.state = "start"
                    return
        elif self.state == "play":
            if pygame.Rect(WIDTH-45, 18, 28, 28).collidepoint(mx, my):
                self.state = "pause"; return
            for text, btn in self.action_btns.items():
                if btn.collidepoint(mx, my):
                    if text == "R重开": self.reset_level(self.level)
                    elif text == "U撤销": self.undo()
                    elif text == "H提示": self.give_hint()
                    elif text == "Esc暂停": self.state = "pause"
                    return
            c = (mx - MARGIN_X) // CELL
            r = (my - TOP_BAR - 10) // CELL
            if 0 <= r < ROWS and 0 <= c < COLS:
                self.click(r, c); self.check_win()

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN: self.handle_click(*e.pos)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r and self.state=="play": self.reset_level(self.level)
                    elif e.key == pygame.K_u and self.state=="play": self.undo()
                    elif e.key == pygame.K_h and self.state=="play": self.give_hint()
                    elif e.key == pygame.K_ESCAPE:
                        self.state = "pause" if self.state=="play" else ("play" if self.state=="pause" else self.state)
            if self.shake:
                self.shake = (self.shake[0], self.shake[1], self.shake[2]+1)
                if self.shake[2] > 18: self.shake = None
            if self.fly_out:
                self.fly_out = (self.fly_out[0],self.fly_out[1],self.fly_out[2],self.fly_out[3]+1)
                if self.fly_out[3] > 20: self.fly_out = None
            if self.collide:
                self.collide = (self.collide[0],self.collide[1],self.collide[2],self.collide[3]+1)
                if self.collide[3] > 20:
                    self.shake = (self.collide[0],self.collide[1],0); self.collide = None
            self.draw(); self.clock.tick(30)


if __name__ == "__main__":
    Game().run()
