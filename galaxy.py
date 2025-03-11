import numpy as np
import pygame
import sys
import random
from pygame import gfxdraw
import math

# Pygame başlatma
pygame.init()

# Ekran boyutları
width, height = 1200, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Gelişmiş Galaksi Simülasyonu")

# Renkler
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (75, 105, 255)
YELLOW = (255, 255, 180)
RED = (255, 90, 90)
PURPLE = (180, 90, 255)
STAR_COLORS = [WHITE, BLUE, YELLOW, RED, PURPLE]
STAR_WEIGHTS = [50, 20, 20, 10, 5]  # Beyaz yıldızlar daha yaygın

# Arka plan yıldızları
background_stars = []
for _ in range(1000):
    x = random.randint(0, width)
    y = random.randint(0, height)
    color = random.choices(STAR_COLORS, STAR_WEIGHTS)[0]
    size = random.uniform(0.5, 1.5) if color == WHITE else random.uniform(1.0, 2.5)
    brightness = random.uniform(150, 255)
    color = tuple(int(c * brightness / 255) for c in color)
    background_stars.append((x, y, color, size))

# Galaksi parametreleri
num_stars = 5000
spiral_arms = 5
arm_width_factor = 0.5
arm_wind_factor = 2.0
galaxy_radius = 350
central_bulge_size = 100
central_darkness = 0  # Merkez kara delik efekti için

# Galaksi yıldızları
galaxy_stars = []
for i in range(num_stars):
    # Rastgele açı ve merkeze olan uzaklık
    distance = random.random() ** 2 * galaxy_radius
    # Spiral kollarını oluşturmak için açı modülasyonu
    arm = random.randint(0, spiral_arms - 1)
    angle = 2 * np.pi * (arm / spiral_arms + arm_wind_factor * (distance / galaxy_radius))
    
    # Rastgele saçılma ekle
    scatter = np.random.normal(0, arm_width_factor * (distance / galaxy_radius))
    angle += scatter
    
    # 3D koordinatlara dönüştür
    x = distance * np.cos(angle)
    y = distance * np.sin(angle) * 0.6  # Eliptik görünüm için basıklaştır
    
    # Z koordinatı - merkeze yakın yıldızlar daha yakın düzleme
    central_factor = max(0, 1 - distance / galaxy_radius)
    z_scatter = np.random.normal(0, 20 * (1 - central_factor * 0.8))
    z = z_scatter
    
    # Merkeze yakınlığa göre renk ve parlaklık belirle
    if distance < central_bulge_size:
        color_index = random.choices([1, 2, 3, 4], [5, 20, 60, 15])[0]  # Merkez bölgede sarı/kırmızı yoğun
        size = random.uniform(1.0, 2.5)
    else:
        arm_phase = (angle * spiral_arms / (2 * np.pi)) % 1
        if arm_phase < 0.2:  # Spiral kol üzerinde
            color_index = random.choices([0, 1, 2], [5, 60, 35])[0]  # Kollarda mavi/beyaz yoğun
            size = random.uniform(1.5, 3.0)
        else:
            color_index = random.choices([0, 1, 2, 3], [35, 30, 25, 10])[0]
            size = random.uniform(0.8, 1.8)
            
    color = STAR_COLORS[color_index]
    
    # Merkeze yakın yıldızlar daha parlak
    brightness_factor = 0.7 + 0.3 * central_factor
    color = tuple(int(c * brightness_factor) for c in color)
    
    # Merkezde kara delik efekti
    if distance < central_darkness:
        continue
        
    galaxy_stars.append((x, y, z, color, size))

# Sis/toz bulutu parçacıkları
dust_particles = []
for _ in range(2000):
    distance = random.random() ** 2 * galaxy_radius
    arm = random.randint(0, spiral_arms - 1)
    angle = 2 * np.pi * (arm / spiral_arms + arm_wind_factor * (distance / galaxy_radius))
    
    scatter = np.random.normal(0, arm_width_factor * 0.8 * (distance / galaxy_radius))
    angle += scatter
    
    x = distance * np.cos(angle)
    y = distance * np.sin(angle) * 0.6
    z = np.random.normal(0, 15)
    
    alpha = random.randint(5, 30)
    if distance < central_bulge_size:
        color = (180, 170, 130, alpha)
    else:
        color = (100, 120, 180, alpha)
    
    size = random.uniform(10, 50) if random.random() > 0.9 else random.uniform(3, 15)
    dust_particles.append((x, y, z, color, size))

# Rotasyon matrisleri
def rotate_x(x, y, z, angle):
    new_y = y * np.cos(angle) - z * np.sin(angle)
    new_z = y * np.sin(angle) + z * np.cos(angle)
    return x, new_y, new_z

def rotate_y(x, y, z, angle):
    new_x = x * np.cos(angle) + z * np.sin(angle)
    new_z = -x * np.sin(angle) + z * np.cos(angle)
    return new_x, y, new_z

def rotate_z(x, y, z, angle):
    new_x = x * np.cos(angle) - y * np.sin(angle)
    new_y = x * np.sin(angle) + y * np.cos(angle)
    return new_x, new_y, z

# 3D noktayı 2D'ye projeksiyon
def project(x, y, z):
    distance = 800
    factor = distance / (distance + z)
    return int(x * factor + width // 2), int(y * factor + height // 2)

# Parlak yıldız çizim fonksiyonu
def draw_star(surface, x, y, color, size):
    if 0 <= x < width and 0 <= y < height:
        # Temel nokta
        pygame.gfxdraw.filled_circle(surface, x, y, int(size), color)
        
        # Parlama efekti
        if size > 1.5:
            glow_surf = pygame.Surface((int(size*6), int(size*6)), pygame.SRCALPHA)
            for radius in range(1, int(size*3)):
                alpha = max(0, 100 - radius * 30)
                glow_color = (color[0], color[1], color[2], alpha)
                pygame.gfxdraw.filled_circle(glow_surf, int(size*3), int(size*3), radius, glow_color)
            
            surface.blit(glow_surf, (x - int(size*3), y - int(size*3)), special_flags=pygame.BLEND_ADD)
            
            # Parlama çizgileri
            if size > 2:
                for i in range(4):
                    angle = i * np.pi/2
                    length = size * 3
                    end_x = x + int(np.cos(angle) * length)
                    end_y = y + int(np.sin(angle) * length)
                    pygame.draw.line(surface, (color[0]//2, color[1]//2, color[2]//2), (x, y), (end_x, end_y), 1)

# Sis/toz bulutu çizim fonksiyonu
def draw_dust(surface, x, y, color, size):
    if 0 <= x < width and 0 <= y < height:
        dust_surf = pygame.Surface((int(size*2), int(size*2)), pygame.SRCALPHA)
        pygame.gfxdraw.filled_circle(dust_surf, int(size), int(size), int(size), color)
        surface.blit(dust_surf, (x-int(size), y-int(size)), special_flags=pygame.BLEND_ADD)

# Ana döngü
clock = pygame.time.Clock()
angle_x, angle_y, angle_z = 0, np.pi/4, 0
rotate_speed = 0.003

# Post-processing için yüzeyler
bloom_surf = pygame.Surface((width, height), pygame.SRCALPHA)
main_surf = pygame.Surface((width, height))

running = True
paused = False
auto_rotate = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                auto_rotate = not auto_rotate
    
    # Fare kontrolü
    if pygame.mouse.get_pressed()[0]:
        rel_x, rel_y = pygame.mouse.get_rel()
        angle_y += rel_x * 0.01
        angle_x += rel_y * 0.01
    else:
        pygame.mouse.get_rel()  # Sıfırla
    
    if not paused:
        # Otomatik döndürme
        if auto_rotate:
            angle_y += rotate_speed
            
        # Ekranı temizle
        main_surf.fill(BLACK)
        bloom_surf.fill((0, 0, 0, 0))
        
        # Arka plan yıldızları çiz
        for x, y, color, size in background_stars:
            pygame.gfxdraw.filled_circle(main_surf, x, y, int(size), color)
        
        # Galaksi toz bulutlarını çiz - derinliğe göre sırala
        visible_dust = []
        for x, y, z, color, size in dust_particles:
            # Rotasyon uygula
            x, y, z = rotate_x(x, y, z, angle_x)
            x, y, z = rotate_y(x, y, z, angle_y)
            x, y, z = rotate_z(x, y, z, angle_z)
            
            # Projeksiyon yap
            proj_x, proj_y = project(x, y, z)
            visible_dust.append((proj_x, proj_y, z, color, size))
        
        # Z-sıralama ve çizim
        visible_dust.sort(key=lambda p: p[2], reverse=True)
        for x, y, _, color, size in visible_dust:
            draw_dust(bloom_surf, x, y, color, size)
        
        # Galaksi yıldızlarını çiz - derinliğe göre sırala
        visible_stars = []
        for x, y, z, color, size in galaxy_stars:
            # Rotasyon uygula
            x, y, z = rotate_x(x, y, z, angle_x)
            x, y, z = rotate_y(x, y, z, angle_y)
            x, y, z = rotate_z(x, y, z, angle_z)
            
            # Projeksiyon yap
            proj_x, proj_y = project(x, y, z)
            visible_stars.append((proj_x, proj_y, z, color, size))
        
        # Z-sıralama ve çizim
        visible_stars.sort(key=lambda p: p[2], reverse=True)
        for x, y, _, color, size in visible_stars:
            draw_star(bloom_surf, x, y, color, size)
        
        # Post-processing efektlerini birleştir
        main_surf.blit(bloom_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Bilgi metni göster
        font = pygame.font.SysFont("Arial", 16)
        info_text = [
            f"FPS: {int(clock.get_fps())}",
            f"Yıldız Sayısı: {num_stars}",
            f"Spiral Kol: {spiral_arms}",
            "Otomatik Döndürme: " + ("Açık" if auto_rotate else "Kapalı"),
            "Döndürmek için fareyi sürükleyin",
            "Durdur/Devam: SPACE",
            "Otomatik Döndürme: R"
        ]
        
        for i, text in enumerate(info_text):
            text_surf = font.render(text, True, WHITE)
            main_surf.blit(text_surf, (10, 10 + i * 20))
        
        # Ekrana çiz
        screen.blit(main_surf, (0, 0))
        pygame.display.flip()
        
    clock.tick(60)

pygame.quit()
sys.exit()