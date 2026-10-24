# -*- coding: utf-8 -*-
"""
一箭又一箭 - 福州大学软件工程第二次个人作业
学号：102402154
运行：python arrow_game.py
依赖：pip install pygame
"""
import pygame
import sys

# ============ 配置 ============
CELL = 80            # 每格像素
MARGIN = 60          # 边距
ROWS, COLS = 6, 6
WIDTH = MARGIN * 2 + CELL * COLS
HEIGHT = MARGIN * 2 + CELL * ROWS + 120  # 底部留信息栏
FPS = 30

# 方向: 0=上 1=右 2=下 3=左
DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]
ARROW_ANGLE = [90, 0, 270, 180]  # 旋转角度

# 颜色
BG = (30, 34, 48)
GRID = (50, 56, 78)
ARROW_COLOR = (90, 180, 255)
ARROW_BLOCK = (255, 120, 120)
WHITE = (240, 240, 240)
GREEN = (80, 220, 140)
RED = (255, 100, 100)
YELLOW = (255, 210, 90)

# ============ 关卡设计 ============
# 0=空, 1=上, 2=右, 3=下, 4=左
LEVELS = [
    # 关卡1: 简单，按顺序点
    [
        [0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 2, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ],
    # 关卡2: 有阻挡关系
    [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 3, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 4, 0, 0, 2, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ],
    # 关卡3: 稍复杂，需要按正确顺序
    [
        [0, 0, 0, 0, 0, 0],
        [0, 2, 0, 2, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 1, 0, 3, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ],
]

MAX_MISTAKES = 3

# ============ 游戏类 ============
class ArrowGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("一箭又一箭 - 102402154")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        # 中文字体兼容：优先微软雅黑，找不到就用默认字体
        self.font = pygame.font.SysFont(["microsoftyahei", "Microsoft YaHei", "simhei", "arial"], 22)
        self.big_font = pygame.font.SysFont(["microsoftyahei", "Microsoft YaHei", "simhei", "arial"], 48)
        self.state = "start"  # start / play / win / fail
        self.reset_level(0)

    def reset_level(self, lv):
        self.level = lv
        self.grid = [row[:] for row in LEVELS[lv]]
        self.mistakes = 0
        self.shake = None       # 被阻挡时的闪烁效果 (r,c,frame)
        self.fly_out = None     # 飞出动画 (r,c,dir,frame)

    def count_arrows(self):
        return sum(1 for row in self.grid for v in row if v != 0)

    def can_fly(self, r, c, d):
        """检查(r,c)朝方向d是否能飞出（路径上无其他箭头）"""
        nr, nc = r + DY[d], c + DX[d]
        while 0 <= nr < ROWS and 0 <= nc < COLS:
            if self.grid[nr][nc] != 0:
                return False
            nr += DY[d]
            nc += DX[d]
        return True

    def click(self, r, c):
        v = self.grid[r][c]
        if v == 0:
            return
        d = v - 1  # 1->上(0), 2->右(1), 3->下(2), 4->左(3)
        if self.can_fly(r, c, d):
            self.fly_out = (r, c, d, 0)
            self.grid[r][c] = 0
        else:
            self.mistakes += 1
            self.shake = (r, c, 0)
            if self.mistakes >= MAX_MISTAKES:
                self.state = "fail"

    def check_win(self):
        if self.count_arrows() == 0:
            if self.level < len(LEVELS) - 1:
                self.state = "win_next"
            else:
                self.state = "win_final"

    # ---------- 绘制 ----------
    def draw_arrow(self, x, y, direction, color=ARROW_COLOR):
        """在(x,y)画一个指向direction的箭头"""
        s = CELL // 2 - 10
        # 三角形箭头
        if direction == 0:    # 上
            pts = [(x, y-s), (x-s, y+s//2), (x+s, y+s//2)]
        elif direction == 1:  # 右
            pts = [(x+s, y), (x-s//2, y-s), (x-s//2, y+s)]
        elif direction == 2:  # 下
            pts = [(x, y+s), (x-s, y-s//2), (x+s, y-s//2)]
        else:                # 左
            pts = [(x-s, y), (x+s//2, y-s), (x+s//2, y+s)]
        pygame.draw.polygon(self.screen, color, pts)
        # 箭尾杆
        if direction == 0:
            pygame.draw.line(self.screen, color, (x, y+s//2), (x, y+s), 3)
        elif direction == 2:
            pygame.draw.line(self.screen, color, (x, y-s//2), (x, y-s), 3)
        elif direction == 1:
            pygame.draw.line(self.screen, color, (x-s//2, y), (x-s, y), 3)
        else:
            pygame.draw.line(self.screen, color, (x+s//2, y), (x+s, y), 3)

    def draw(self):
        self.screen.fill(BG)

        if self.state == "start":
            title = self.big_font.render("一箭又一箭", True, WHITE)
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
            tip = self.font.render("点击任意处开始游戏", True, YELLOW)
            self.screen.blit(tip, (WIDTH//2 - tip.get_width()//2, HEIGHT//2 + 20))
            tip2 = self.font.render("学号: 102402154", True, (150,150,150))
            self.screen.blit(tip2, (WIDTH//2 - tip2.get_width()//2, HEIGHT//2 + 60))
            pygame.display.flip()
            return

        if self.state in ("fail", "win_next", "win_final"):
            if self.state == "fail":
                txt = self.big_font.render("游戏失败", True, RED)
            elif self.state == "win_final":
                txt = self.big_font.render("全部通关！", True, GREEN)
            else:
                txt = self.big_font.render(f"第{self.level+1}关通过", True, GREEN)
            self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 60))
            tip = self.font.render("点击任意处继续 / 重新开始", True, WHITE)
            self.screen.blit(tip, (WIDTH//2 - tip.get_width()//2, HEIGHT//2 + 20))
            pygame.display.flip()
            return

        # 画棋盘
        for r in range(ROWS):
            for c in range(COLS):
                x = MARGIN + c * CELL
                y = MARGIN + r * CELL
                pygame.draw.rect(self.screen, GRID, (x, y, CELL, CELL), 1)
                v = self.grid[r][c]
                if v != 0:
                    color = ARROW_COLOR
                    if self.shake and self.shake[0]==r and self.shake[1]==c:
                        # 闪烁红
                        if self.shake[2] // 5 % 2 == 0:
                            color = ARROW_BLOCK
                    self.draw_arrow(x + CELL//2, y + CELL//2, v-1, color)

        # 飞出动画
        if self.fly_out:
            r, c, d, frame = self.fly_out
            ox = MARGIN + c*CELL + CELL//2 + DX[d] * frame * 8
            oy = MARGIN + r*CELL + CELL//2 + DY[d] * frame * 8
            self.draw_arrow(ox, oy, d, GREEN)

        # 底部信息栏
        info_y = MARGIN + ROWS * CELL + 20
        s1 = self.font.render(f"关卡: {self.level+1}/{len(LEVELS)}", True, WHITE)
        s2 = self.font.render(f"剩余箭头: {self.count_arrows()}", True, WHITE)
        s3 = self.font.render(f"失误: {self.mistakes}/{MAX_MISTAKES}", True,
                              RED if self.mistakes >= 2 else WHITE)
        s4 = self.font.render("R: 重开本关", True, YELLOW)
        self.screen.blit(s1, (MARGIN, info_y))
        self.screen.blit(s2, (MARGIN+200, info_y))
        self.screen.blit(s3, (MARGIN+380, info_y))
        self.screen.blit(s4, (WIDTH-MARGIN-120, info_y))
        pygame.display.flip()

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = e.pos
                    if self.state == "start":
                        self.reset_level(0)
                        self.state = "play"
                    elif self.state in ("fail", "win_next", "win_final"):
                        if self.state == "win_next":
                            self.reset_level(self.level + 1)
                        elif self.state == "win_final":
                            self.reset_level(0)
                        else:
                            self.reset_level(self.level)
                        self.state = "play"
                    elif self.state == "play":
                        c = (mx - MARGIN) // CELL
                        r = (my - MARGIN) // CELL
                        if 0 <= r < ROWS and 0 <= c < COLS:
                            self.click(r, c)
                            self.check_win()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r and self.state == "play":
                        self.reset_level(self.level)

            # 动画帧
            if self.shake:
                self.shake = (self.shake[0], self.shake[1], self.shake[2]+1)
                if self.shake[2] > 20:
                    self.shake = None
            if self.fly_out:
                self.fly_out = (self.fly_out[0], self.fly_out[1], self.fly_out[2], self.fly_out[3]+1)
                if self.fly_out[3] > 20:
                    self.fly_out = None

            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    ArrowGame().run()
