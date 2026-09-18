import math
import os
import random
import sys
import pygbag.aio as asyncio
import pygame
from pygame.locals import *

# 初始化
pygame.init()
pygame.mixer.init()

BLACK = (0, 0, 0)
SILVER = (192, 208, 224)
RED = (255, 0, 0)
CYAN = (0, 224, 255)

# 影像與音效全域變數
img_galaxy = []
img_sship = []
img_weapon = None
img_shield = None
img_enemy = []
img_explode = []
img_title = []

se_barrage = None
se_damage = None
se_explosion = None
se_shot = None

idx = 0
tmr = 0
score = 0
hisco = 10000
new_record = False
bg_speed = 4
bg_positions = [0, -720, -1440, -2160]

ss_x = 480
ss_y = 600
ss_d = 0
ss_shield = 100
ss_muteki = 0
key_spc = 0
key_z = 0
paused = False

MISSILE_MAX = 200
msl_no = 0
msl_f = [False] * MISSILE_MAX
msl_x = [0] * MISSILE_MAX
msl_y = [0] * MISSILE_MAX
msl_a = [0] * MISSILE_MAX

ENEMY_MAX = 100
emy_no = 0
emy_f = [False] * ENEMY_MAX
emy_x = [0] * ENEMY_MAX
emy_y = [0] * ENEMY_MAX
emy_a = [0] * ENEMY_MAX
emy_type = [0] * ENEMY_MAX
emy_speed = [0] * ENEMY_MAX
emy_shield = [0] * ENEMY_MAX
emy_count = [0] * ENEMY_MAX

EMY_BULLET = 0
EMY_ZAKO = 1
EMY_BOSS = 5
LINE_T = -80
LINE_B = 800
LINE_L = -80
LINE_R = 1040

EFFECT_MAX = 100
eff_no = 0
eff_p = [0] * EFFECT_MAX
eff_x = [0] * EFFECT_MAX
eff_y = [0] * EFFECT_MAX


def get_dis(x1, y1, x2, y2):
  return (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)


def draw_text(scrn, txt, x, y, siz, col):
  try:
    fnt = pygame.font.Font(None, siz)
  except:
    return
  cr = int(col[0] / 2)
  cg = int(col[1] / 2)
  cb = int(col[2] / 2)
  sur = fnt.render(txt, True, (cr, cg, cb))
  x = x - sur.get_width() / 2
  y = y - sur.get_height() / 2
  scrn.blit(sur, [x + 1, y + 1])
  cr = min(255, col[0] + 128)
  cg = min(255, col[1] + 128)
  cb = min(255, col[2] + 128)
  sur = fnt.render(txt, True, (cr, cg, cb))
  scrn.blit(sur, [x - 1, y - 1])
  sur = fnt.render(txt, True, col)
  scrn.blit(sur, [x, y])


def move_starship(scrn, key):
  global idx, tmr, ss_x, ss_y, ss_d, ss_shield, ss_muteki, key_spc, key_z
  ss_d = 0
  if key[K_UP]:
    ss_y = max(80, ss_y - 20)
  if key[K_DOWN]:
    ss_y = min(640, ss_y + 20)
  if key[K_LEFT]:
    ss_d = 1
    ss_x = max(40, ss_x - 20)
  if key[K_RIGHT]:
    ss_d = 2
    ss_x = min(920, ss_x + 20)

  key_spc = (key_spc + 1) * key[K_SPACE]
  if key_spc % 5 == 1:
    set_missile(0)
    if se_shot:
      se_shot.play()

  key_z = (key_z + 1) * key[K_z]
  if key_z == 1 and ss_shield > 10:
    set_missile(10)
    ss_shield -= 10
    if se_barrage:
      se_barrage.play()

  if ss_muteki % 2 == 0:
    if len(img_sship) > 1 and img_sship[1]:
      scrn.blit(img_sship[1], [ss_x - 8, ss_y + 40 + (tmr % 3) * 2])
    if len(img_sship) > 0 and img_sship[0]:
      scrn.blit(img_sship[0], [ss_x - 37, ss_y - 48])

  if ss_muteki > 0:
    ss_muteki -= 1
    return
  elif idx == 1:
    for i in range(ENEMY_MAX):
      if emy_f[i]:
        if emy_type[i] < len(img_enemy) and img_enemy[emy_type[i]]:
          w = img_enemy[emy_type[i]].get_width()
          h = img_enemy[emy_type[i]].get_height()
          r = int((w + h) / 4 + (74 + 96) / 4)
          if get_dis(emy_x[i], emy_y[i], ss_x, ss_y) < r * r:
            set_effect(ss_x, ss_y)
            ss_shield -= 10
            if ss_shield <= 0:
              ss_shield = 0
              idx = 2
              tmr = 0
            if ss_muteki == 0:
              ss_muteki = 60
              if se_damage:
                se_damage.play()
            if emy_type[i] < EMY_BOSS:
              emy_f[i] = False


def set_missile(typ):
  global msl_no
  if typ == 0:
    msl_f[msl_no] = True
    msl_x[msl_no] = ss_x
    msl_y[msl_no] = ss_y - 50
    msl_a[msl_no] = 270
    msl_no = (msl_no + 1) % MISSILE_MAX
  elif typ == 10:
    for a in range(160, 390, 10):
      msl_f[msl_no] = True
      msl_x[msl_no] = ss_x
      msl_y[msl_no] = ss_y - 50
      msl_a[msl_no] = a
      msl_no = (msl_no + 1) % MISSILE_MAX


def move_missile(scrn):
  for i in range(MISSILE_MAX):
    if msl_f[i]:
      msl_x[i] += 36 * math.cos(math.radians(msl_a[i]))
      msl_y[i] += 36 * math.sin(math.radians(msl_a[i]))
      if img_weapon:
        img_rz = pygame.transform.rotozoom(img_weapon, -90 - msl_a[i], 1.0)
        scrn.blit(
            img_rz,
            [
                msl_x[i] - img_rz.get_width() / 2,
                msl_y[i] - img_rz.get_height() / 2,
            ],
        )
      else:
        pygame.draw.circle(scrn, (255, 255, 0), [int(msl_x[i]), int(msl_y[i])], 4)
      if msl_y[i] < 0 or msl_x[i] < 0 or msl_x[i] > 960:
        msl_f[i] = False


def bring_enemy():
  sec = tmr / 30
  if 0 < sec < 25 and tmr % 15 == 0:
    set_enemy(random.randint(20, 940), LINE_T, 90, EMY_ZAKO, 8, 1)
  if 30 < sec < 55 and tmr % 10 == 0:
    set_enemy(random.randint(20, 940), LINE_T, 90, EMY_ZAKO + 1, 12, 1)
  if 60 < sec < 85 and tmr % 15 == 0:
    set_enemy(
        random.randint(100, 860),
        LINE_T,
        random.randint(60, 120),
        EMY_ZAKO + 2,
        6,
        3,
    )
  if 90 < sec < 115 and tmr % 20 == 0:
    set_enemy(random.randint(100, 860), LINE_T, 90, EMY_ZAKO + 3, 12, 2)
  if 120 < sec < 145 and tmr % 20 == 0:
    set_enemy(random.randint(20, 940), LINE_T, 90, EMY_ZAKO, 8, 1)
    set_enemy(
        random.randint(100, 860),
        LINE_T,
        random.randint(60, 120),
        EMY_ZAKO + 2,
        6,
        3,
    )
  if 150 < sec < 175 and tmr % 20 == 0:
    set_enemy(random.randint(20, 940), LINE_B, 270, EMY_ZAKO, 8, 1)
    set_enemy(
        random.randint(20, 940), LINE_T, random.randint(70, 110), EMY_ZAKO + 1, 12, 1
    )
  if 180 < sec < 205 and tmr % 20 == 0:
    set_enemy(
        random.randint(100, 860),
        LINE_T,
        random.randint(60, 120),
        EMY_ZAKO + 2,
        6,
        3,
    )
    set_enemy(random.randint(100, 860), LINE_T, 90, EMY_ZAKO + 3, 12, 2)
  if 210 < sec < 235 and tmr % 20 == 0:
    set_enemy(LINE_L, random.randint(40, 680), 0, EMY_ZAKO, 12, 1)
    set_enemy(LINE_R, random.randint(40, 680), 180, EMY_ZAKO + 1, 18, 1)
  if 240 < sec < 265 and tmr % 30 == 0:
    set_enemy(random.randint(20, 940), LINE_T, 90, EMY_ZAKO, 8, 1)
    set_enemy(random.randint(20, 940), LINE_T, 90, EMY_ZAKO + 1, 12, 1)
    set_enemy(
        random.randint(100, 860),
        LINE_T,
        random.randint(60, 120),
        EMY_ZAKO + 2,
        6,
        3,
    )
    set_enemy(random.randint(100, 860), LINE_T, 90, EMY_ZAKO + 3, 12, 2)
  if tmr == 30 * 270:
    set_enemy(480, -210, 90, EMY_BOSS, 4, 200)


def set_enemy(x, y, a, ty, sp, sh):
  global emy_no
  while True:
    if not emy_f[emy_no]:
      emy_f[emy_no] = True
      emy_x[emy_no] = x
      emy_y[emy_no] = y
      emy_a[emy_no] = a
      emy_type[emy_no] = ty
      emy_speed[emy_no] = sp
      emy_shield[emy_no] = sh
      emy_count[emy_no] = 0
      break
    emy_no = (emy_no + 1) % ENEMY_MAX


def move_enemy(scrn):
  global idx, tmr, score, hisco, new_record, ss_shield
  for i in range(ENEMY_MAX):
    if emy_f[i]:
      ang = -90 - emy_a[i]
      png = emy_type[i]
      if emy_type[i] < EMY_BOSS:
        emy_x[i] += emy_speed[i] * math.cos(math.radians(emy_a[i]))
        emy_y[i] += emy_speed[i] * math.sin(math.radians(emy_a[i]))
        if emy_type[i] == 4:
          emy_count[i] += 1
          ang = emy_count[i] * 10
          if emy_y[i] > 240 and emy_a[i] == 90:
            emy_a[i] = random.choice([50, 70, 110, 130])
            set_enemy(emy_x[i], emy_y[i], 90, EMY_BULLET, 6, 0)
        if (
            emy_x[i] < LINE_L
            or LINE_R < emy_x[i]
            or emy_y[i] < LINE_T
            or LINE_B < emy_y[i]
        ):
          emy_f[i] = False
      else:
        if emy_count[i] == 0:
          emy_y[i] += 2
          if emy_y[i] >= 200:
            emy_count[i] = 1
        elif emy_count[i] == 1:
          emy_x[i] -= emy_speed[i]
          if emy_x[i] < 200:
            for j in range(10):
              set_enemy(emy_x[i], emy_y[i] + 80, j * 20, EMY_BULLET, 6, 0)
            emy_count[i] = 2
        else:
          emy_x[i] += emy_speed[i]
          if emy_x[i] > 760:
            for j in range(10):
              set_enemy(emy_x[i], emy_y[i] + 80, j * 20, EMY_BULLET, 6, 0)
            emy_count[i] = 1
        if emy_shield[i] < 100 and tmr % 30 == 0:
          set_enemy(
              emy_x[i], emy_y[i] + 80, random.randint(60, 120), EMY_BULLET, 6, 0
          )

      if emy_type[i] < len(img_enemy) and img_enemy[emy_type[i]]:
        if emy_type[i] != EMY_BULLET:
          w = img_enemy[emy_type[i]].get_width()
          h = img_enemy[emy_type[i]].get_height()
          r = int((w + h) / 4) + 12
          er = int((w + h) / 4)
          for n in range(MISSILE_MAX):
            if (
                msl_f[n]
                and get_dis(emy_x[i], emy_y[i], msl_x[n], msl_y[n]) < r * r
            ):
              msl_f[n] = False
              set_effect(
                  emy_x[i] + random.randint(-er, er),
                  emy_y[i] + random.randint(-er, er),
              )
              if emy_type[i] == EMY_BOSS:
                png = emy_type[i] + 1
              emy_shield[i] -= 1
              score += 100
              if score > hisco:
                hisco = score
                new_record = True
              if emy_shield[i] <= 0:
                emy_f[i] = False
                if ss_shield < 100:
                  ss_shield += 1
                if emy_type[i] == EMY_BOSS and idx == 1:
                  idx = 3
                  tmr = 0
                  for _ in range(10):
                    set_effect(
                        emy_x[i] + random.randint(-er, er),
                        emy_y[i] + random.randint(-er, er),
                    )
                  if se_explosion:
                    se_explosion.play()

        img_rz = pygame.transform.rotozoom(img_enemy[png], ang, 1.0)
        scrn.blit(
            img_rz,
            [
                emy_x[i] - img_rz.get_width() / 2,
                emy_y[i] - img_rz.get_height() / 2,
            ],
        )
      else:
        pygame.draw.circle(
            scrn, (255, 0, 0), [int(emy_x[i]), int(emy_y[i])], 12
        )


def set_effect(x, y):
  global eff_no
  eff_p[eff_no] = 1
  eff_x[eff_no] = x
  eff_y[eff_no] = y
  eff_no = (eff_no + 1) % EFFECT_MAX


def draw_effect(scrn):
  for i in range(EFFECT_MAX):
    if eff_p[i] > 0:
      if eff_p[i] < len(img_explode) and img_explode[eff_p[i]]:
        scrn.blit(img_explode[eff_p[i]], [eff_x[i] - 48, eff_y[i] - 48])
      eff_p[i] += 1
      if eff_p[i] >= 6:
        eff_p[i] = 0


async def main():
  global idx, tmr, score, new_record, bg_positions, ss_x, ss_y, ss_d, ss_shield, ss_muteki, paused
  global se_barrage, se_damage, se_explosion, se_shot
  global img_galaxy, img_sship, img_weapon, img_shield, img_enemy, img_explode, img_title

  screen = pygame.display.set_mode((960, 720))
  pygame.display.set_caption("Galaxy Lancer")

  def safe_load(path, alpha=False):
    try:
      img = pygame.image.load(path)
      return img.convert_alpha() if alpha else img.convert()
    except Exception as e:
      print(f"無法載入檔案 {path}: {e}")
      return None

  # 網頁版路徑對應 (Assets 目錄)
  img_galaxy = [
      safe_load("Assets/image_gl/universe1.png"),
      safe_load("Assets/image_gl/universe2.png"),
      safe_load("Assets/image_gl/universe3.png"),
      safe_load("Assets/image_gl/universe4.png"),
  ]
  img_sship = [
      safe_load("Assets/image_gl/skyship.png", True),
      safe_load("Assets/image_gl/starship_burner.png", True),
  ]
  img_weapon = safe_load("Assets/image_gl/bullet.png", True)
  img_shield = safe_load("Assets/image_gl/shield.png", True)
  img_enemy = [
      safe_load("Assets/image_gl/enemy0.png", True),
      safe_load("Assets/image_gl/enemy1.png", True),
      safe_load("Assets/image_gl/enemy2.png", True),
      safe_load("Assets/image_gl/enemy3.png", True),
      safe_load("Assets/image_gl/enemy4.png", True),
      safe_load("Assets/image_gl/enemy_boss.png", True),
      safe_load("Assets/image_gl/enemy_boss_f.png", True),
  ]
  img_explode = [
      None,
      safe_load("Assets/image_gl/explosion1.png", True),
      safe_load("Assets/image_gl/explosion2.png", True),
      safe_load("Assets/image_gl/explosion3.png", True),
      safe_load("Assets/image_gl/explosion4.png", True),
      safe_load("Assets/image_gl/explosion5.png", True),
  ]
  img_title = [
      safe_load("Assets/image_gl/nebula.png", True),
      safe_load("Assets/image_gl/logo.png", True),
  ]

  try:
    se_barrage = pygame.mixer.Sound("Assets/sound_gl/barrage.ogg")
    se_damage = pygame.mixer.Sound("Assets/sound_gl/damage.ogg")
    se_explosion = pygame.mixer.Sound("Assets/sound_gl/explosion.ogg")
    se_shot = pygame.mixer.Sound("Assets/sound_gl/shot.ogg")
  except:
    pass

  running = True
  while running:
    tmr += 1
    for event in pygame.event.get():
      if event.type == QUIT:
        running = False
      if event.type == KEYDOWN:
        if event.key == K_RETURN:
          if idx == 1:
            paused = not paused
        if event.key == K_r:
          if idx == 1:
            idx = 0
            tmr = 0
            score = 0
            paused = False
            try:
              pygame.mixer.music.stop()
            except:
              pass
            for i in range(ENEMY_MAX):
              emy_f[i] = False
            for i in range(MISSILE_MAX):
              msl_f[i] = False

    # 背景移動
    for i in range(4):
      bg_positions[i] += bg_speed
      if bg_positions[i] > 720:
        bg_positions[i] -= 2880
      if i < len(img_galaxy) and img_galaxy[i]:
        screen.blit(img_galaxy[i], [0, bg_positions[i]])
      else:
        screen.fill((0, 0, 0))

    key = pygame.key.get_pressed()

    if paused:
      pause_surface = pygame.Surface((960, 720), pygame.SRCALPHA)
      pause_surface.fill((0, 40, 120, 150))
      screen.blit(pause_surface, (0, 0))
      draw_text(screen, "PAUSED", 480, 280, 80, CYAN)
      draw_text(screen, "ENTER  RESUME", 480, 380, 45, SILVER)
      draw_text(screen, "R  RESTART", 480, 440, 45, SILVER)
      pygame.display.update()
      await asyncio.sleep(0)
      continue

    if idx == 0:
      if len(img_title) > 0 and img_title[0]:
        img_rz = pygame.transform.rotozoom(img_title[0], -tmr % 360, 1.0)
        screen.blit(
            img_rz,
            [480 - img_rz.get_width() / 2, 280 - img_rz.get_height() / 2],
        )
      if len(img_title) > 1 and img_title[1]:
        screen.blit(img_title[1], [70, 160])
      draw_text(screen, "Press [SPACE] to start!", 480, 600, 50, SILVER)

      if key[K_SPACE]:
        idx = 1
        tmr = 0
        score = 0
        new_record = False
        ss_x = 480
        ss_y = 600
        ss_d = 0
        ss_shield = 100
        ss_muteki = 0
        for i in range(ENEMY_MAX):
          emy_f[i] = False
        for i in range(MISSILE_MAX):
          msl_f[i] = False
        try:
          pygame.mixer.music.load("Assets/sound_gl/battle.ogg")
          pygame.mixer.music.play(-1)
        except:
          pass

    elif idx == 1:
      move_starship(screen, key)
      move_missile(screen)
      bring_enemy()
      move_enemy(screen)

    elif idx == 2:
      move_missile(screen)
      move_enemy(screen)
      if tmr == 1:
        try:
          pygame.mixer.music.stop()
        except:
          pass
      if tmr <= 90:
        if tmr % 5 == 0:
          set_effect(
              ss_x + random.randint(-60, 60), ss_y + random.randint(-60, 60)
          )
        if tmr % 10 == 0 and se_damage:
          se_damage.play()
      if tmr == 120:
        try:
          pygame.mixer.music.load("Assets/sound_gl/gameover.ogg")
          pygame.mixer.music.play(0)
        except:
          pass
      if tmr > 120:
        draw_text(screen, "GAME OVER", 480, 300, 80, RED)
        if new_record:
          draw_text(screen, "NEW RECORD " + str(hisco), 480, 400, 60, CYAN)
      if tmr == 400:
        idx = 0
        tmr = 0

    elif idx == 3:
      move_starship(screen, key)
      move_missile(screen)
      if tmr == 1:
        try:
          pygame.mixer.music.stop()
        except:
          pass
      if tmr < 30 and tmr % 2 == 0:
        pygame.draw.rect(screen, (192, 0, 0), [0, 0, 960, 720])
      if tmr == 120:
        try:
          pygame.mixer.music.load("Assets/sound_gl/gameclear.ogg")
          pygame.mixer.music.play(0)
        except:
          pass
      if tmr > 120:
        draw_text(screen, "GAME CLEAR", 480, 300, 80, SILVER)
        if new_record:
          draw_text(screen, "NEW RECORD " + str(hisco), 480, 400, 60, CYAN)
      if tmr == 400:
        idx = 0
        tmr = 0

    draw_effect(screen)
    draw_text(screen, "SCORE " + str(score), 200, 30, 50, SILVER)
    draw_text(screen, "HISCORE " + str(hisco), 760, 30, 50, CYAN)
    if idx != 0:
      if img_shield:
        screen.blit(img_shield, [40, 680])
      pygame.draw.rect(
          screen,
          (64, 32, 32),
          [40 + ss_shield * 4, 680, (100 - ss_shield) * 4, 12],
      )

    pygame.display.update()
    await asyncio.sleep(0)

  pygame.quit()


if __name__ == "__main__":
  asyncio.run(main())