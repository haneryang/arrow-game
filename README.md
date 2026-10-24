# 一箭又一箭

福州大学软件工程第二次个人作业——用 Python + Pygame 实现的箭头方向解谜小游戏。
学号：102402154

## 游戏简介

棋盘上有若干朝向上/下/左/右的箭头，点击箭头后检查其前进方向是否有其他箭头阻挡：
- 无阻挡：箭头飞出棋盘并消失
- 有阻挡：箭头闪烁提示，失误次数减 1
- 清空所有箭头进入下一关，失误 3 次游戏失败

## 开发环境

- Python 3.10+
- pygame

## 安装和运行

```bash
pip install pygame
python arrow_game.py
```

## 游戏操作说明

- 鼠标点击箭头：发射/检查路径
- R 键：重开本关
- 鼠标点击任意处：开始/继续

<img width="790" height="767" alt="image" src="https://github.com/user-attachments/assets/4dcbcb06-a914-4f58-b514-0b4c1f5f9e57" />
<img width="801" height="740" alt="image" src="https://github.com/user-attachments/assets/4820cebf-7c02-423a-a2ca-f471f19a4a90" />


