import pygame
import sys
import math
import random
import asyncio  # 웹 변환을 위해 필수적인 모듈입니다.

# 1. 초기화 및 설정
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The 3D Backrooms - Mobile Web")

clock = pygame.time.Clock()

# 2. 2D 미로 맵 (0: 빈 공간, 1: 백룸 벽)
MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,0,1,0,0,1,1,1,1,0,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,1],
    [1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1],
    [1,1,1,0,0,0,1,0,0,1,0,0,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,1,1,0,0,1,1,1,0,0,1],
    [1,0,0,1,0,0,0,1,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,1,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]
MAP_SIZE = 16
TILE_SIZE = 64 

# 3. 플레이어 및 시야 설정
player_x = 120.0
player_y = 120.0
player_angle = 0.0
player_speed = 3.0
rot_speed = 0.04

FOV = math.pi / 3  
HALF_FOV = FOV / 2
NUM_RAYS = 120  
RAY_STEP = FOV / NUM_RAYS
SCALE = SCREEN_WIDTH / NUM_RAYS

# 4. 색상 정의
YELLOW_WALL = (210, 185, 110)
FLOOR_COLOR = (100, 90, 60)
CEILING_COLOR = (50, 45, 35)

# 5. 📱 모바일 가상 조이스틱 설정 (화면 우측 하단 배치)
JOYSTICK_CENTER_X = 680
JOYSTICK_CENTER_Y = 480
JOYSTICK_OUTER_RADIUS = 70
JOYSTICK_INNER_RADIUS = 30

# 조이스틱 입력 상태 변수
joystick_dx = 0.0
joystick_dy = 0.0
is_touching_joystick = False

# 6. 비동기 메인 루프 함수 (웹 빌드를 위해 코드를 함수로 감싸야 합니다)
async def main():
    global player_x, player_y, player_angle, is_touching_joystick, joystick_dx, joystick_dy
    
    while True:
        clock.tick(60)

        # 마우스 및 터치 포지션 가져오기
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # 터치 또는 마우스 클릭 시작
            if event.type == pygame.MOUSEBUTTONDOWN:
                dist_to_joystick = math.hypot(mouse_pos[0] - JOYSTICK_CENTER_X, mouse_pos[1] - JOYSTICK_CENTER_Y)
                if dist_to_joystick <= JOYSTICK_OUTER_RADIUS:
                    is_touching_joystick = True
                    
            # 터치 또는 마우스 뗌
            if event.type == pygame.MOUSEBUTTONUP:
                is_touching_joystick = False
                joystick_dx = 0
                joystick_dy = 0

        # --- 조이스틱 계산 및 플레이어 이동 ---
        if is_touching_joystick and mouse_buttons[0]:
            # 조이스틱 중심에서 손가락이 얼마나 멀어졌는지 계산
            raw_dx = mouse_pos[0] - JOYSTICK_CENTER_X
            raw_dy = mouse_pos[1] - JOYSTICK_CENTER_Y
            dist = math.hypot(raw_dx, raw_dy)
            
            if dist > 0:
                # 조이스틱 내부 조절용 벡터 정규화
                clamped_dist = min(dist, JOYSTICK_OUTER_RADIUS)
                joystick_dx = (raw_dx / dist) * clamped_dist
                joystick_dy = (raw_dy / dist) * clamped_dist
                
                # 조이스틱 패드 방향에 따른 회전 및 이동 연산
                # 가로축(X)은 시점 회전
                player_angle += (joystick_dx / JOYSTICK_OUTER_RADIUS) * rot_speed
                
                # 세로축(Y)은 앞뒤 전진/후진
                move_factor = -(joystick_dy / JOYSTICK_OUTER_RADIUS) * player_speed
                new_x = player_x + math.cos(player_angle) * move_factor
                new_y = player_y + math.sin(player_angle) * move_factor
                
                # 벽 충돌 체크
                if MAP[int(new_y / TILE_SIZE)][int(new_x / TILE_SIZE)] == 0:
                    player_x = new_x
                    player_y = new_y

        # --- 키보드 조작도 그대로 유지 (테스트용) ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  player_angle -= rot_speed
        if keys[pygame.K_RIGHT]: player_angle += rot_speed
        
        k_new_x, k_new_y = player_x, player_y
        if keys[pygame.K_UP]:
            k_new_x += math.cos(player_angle) * player_speed
            k_new_y += math.sin(player_angle) * player_speed
        if keys[pygame.K_DOWN]:
            k_new_x -= math.cos(player_angle) * player_speed
            k_new_y -= math.sin(player_angle) * player_speed
            
        if MAP[int(k_new_y / TILE_SIZE)][int(k_new_x / TILE_SIZE)] == 0:
            player_x = k_new_x
            player_y = k_new_y

        # --- 3D 레이캐스팅 화면 렌더링 ---
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, CEILING_COLOR, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        pygame.draw.rect(screen, FLOOR_COLOR, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        start_angle = player_angle - HALF_FOV

        for ray in range(NUM_RAYS):
            current_ray_angle = start_angle + ray * RAY_STEP
            sin_a = math.sin(current_ray_angle)
            cos_a = math.cos(current_ray_angle)

            for depth in range(1, 800):
                target_x = player_x + depth * cos_a
                target_y = player_y + depth * sin_a

                map_col = int(target_x / TILE_SIZE)
                map_row = int(target_y / TILE_SIZE)

                if map_col < 0 or map_col >= MAP_SIZE or map_row < 0 or map_row >= MAP_SIZE:
                    break
                if MAP[map_row][map_col] == 1:
                    depth *= math.cos(player_angle - current_ray_angle)
                    wall_height = min(int((TILE_SIZE * 500) / (depth + 0.0001)), SCREEN_HEIGHT)
                    
                    intensity = 1.0 - (depth / 500.0)
                    if intensity < 0: intensity = 0
                    
                    r = int(YELLOW_WALL[0] * intensity)
                    g = int(YELLOW_WALL[1] * intensity)
                    b = int(YELLOW_WALL[2] * intensity)
                    
                    pygame.draw.rect(screen, (r, g, b), (ray * SCALE, (SCREEN_HEIGHT // 2) - (wall_height // 2), SCALE + 1, wall_height))
                    break

        # --- 📱 화면에 모바일 조이스틱 UI 그리기 ---
        # 바깥쪽 큰 원 (반투명 회색)
        pygame.draw.circle(screen, (150, 150, 150, 100), (JOYSTICK_CENTER_X, JOYSTICK_CENTER_Y), JOYSTICK_OUTER_RADIUS, 4)
        # 안쪽 움직이는 작은 조종 패드 원 (하얀색)
        pygame.draw.circle(screen, (240, 240, 240), (int(JOYSTICK_CENTER_X + joystick_dx), int(JOYSTICK_CENTER_Y + joystick_dy)), JOYSTICK_INNER_RADIUS)

        pygame.display.flip()
        
        # ★★★ 웹 브라우저가 과부하로 멈추지 않게 쉼표를 주는 핵심 코드입니다.
        await asyncio.sleep(0)

# 게임 실행
asyncio.run(main())