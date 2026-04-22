# level_manager.py
import random
from enemies import Enemy, ShieldEnemy, FastEnemy, MageEnemy, HeavyEnemy
from config import WIDTH, LEVEL_NAMES, BOSS_INFO

class LevelManager:
    def __init__(self):
        self.level = 1
        self.frame = 0
        self.enemies_killed = 0
        self.enemies_killed_in_level = 0
        
        # Số lượng quái cần giết mỗi màn
        self.enemies_needed = {
            1: 3,
            2: 4,
            3: 5,
            4: 6,
            5: 7,
        }
        
        # Tốc độ spawn (frame delay)
        self.spawn_delays = {
            1: 60,
            2: 55,
            3: 50,
            4: 45,
            5: 40,
        }
        
        # Cờ trạng thái cửa
        self.door_to_boss_spawned = False
        self.door_to_next_level_spawned = False
        self.boss_defeated = False
        self.game_completed = False

    def current_name(self):
        return LEVEL_NAMES[self.level - 1] if self.level <= 5 else "Hoàn thành!"

    def current_boss_info(self):
        return BOSS_INFO.get(self.level, BOSS_INFO[1])

    def spawn_delay(self):
        return self.spawn_delays.get(self.level, 40)

    def max_enemies(self):
        return min(5 + self.level, 8)

    def get_enemies_to_kill(self):
        return self.enemies_needed.get(self.level, 5)

    def get_remaining_enemies(self):
        needed = self.get_enemies_to_kill()
        remaining = needed - self.enemies_killed_in_level
        return max(0, remaining)

    def record_kill(self):
        self.enemies_killed += 1
        self.enemies_killed_in_level += 1
        needed = self.get_enemies_to_kill()
        print(f"⚔️ Enemy killed! {self.enemies_killed_in_level}/{needed}")
        return self.enemies_killed_in_level >= needed

    def can_advance_to_next_level(self):
        if self.level < 5:
            self.level += 1
            self.enemies_killed_in_level = 0
            self.door_to_boss_spawned = False
            self.door_to_next_level_spawned = False
            self.boss_defeated = False
            print(f"🎉 Chuyển sang {self.current_name()}!")
            return True
        else:
            self.game_completed = True
            print("🏆 HOÀN THÀNH GAME!")
            return False

    def should_spawn_door_to_boss(self):
        needed = self.get_enemies_to_kill()
        if not self.door_to_boss_spawned and self.enemies_killed_in_level >= needed:
            print(f"🚪 Đủ điều kiện spawn cửa boss! ({self.enemies_killed_in_level}/{needed})")
            return True
        return False

    def set_door_to_boss_spawned(self, spawned):
        self.door_to_boss_spawned = spawned

    def should_spawn_door_to_next_level(self):
        if not self.door_to_next_level_spawned and self.boss_defeated:
            return True
        return False

    def set_door_to_next_level_spawned(self, spawned):
        self.door_to_next_level_spawned = spawned

    def set_boss_defeated(self, defeated):
        self.boss_defeated = defeated
        if defeated:
            print("👑 Boss đã bị đánh bại!")

    def get_level_progress(self):
        needed = self.get_enemies_to_kill()
        if needed == 0:
            return 0
        return min(1.0, self.enemies_killed_in_level / needed)

    def spawn_enemies(self, width, current_enemies):
        x = lambda: random.randint(20, width - 70)
        if len(current_enemies) >= self.max_enemies():
            return []

        if self.level == 1:
            if random.random() < 0.2:
                return [ShieldEnemy(x())]
            return [Enemy(x())]
        elif self.level == 2:
            choice = random.random()
            if choice < 0.4:
                return [Enemy(x())]
            elif choice < 0.7:
                return [FastEnemy(x())]
            else:
                return [ShieldEnemy(x())]
        elif self.level == 3:
            choice = random.random()
            if choice < 0.3:
                return [Enemy(x())]
            elif choice < 0.5:
                return [FastEnemy(x())]
            elif choice < 0.7:
                return [ShieldEnemy(x())]
            else:
                return [MageEnemy(x())]
        elif self.level == 4:
            choice = random.random()
            if choice < 0.25:
                return [Enemy(x())]
            elif choice < 0.5:
                return [FastEnemy(x())]
            elif choice < 0.7:
                return [ShieldEnemy(x())]
            else:
                return [MageEnemy(x())]
        else:
            choice = random.random()
            if choice < 0.2:
                return [Enemy(x())]
            elif choice < 0.4:
                return [FastEnemy(x())]
            elif choice < 0.6:
                return [ShieldEnemy(x())]
            elif choice < 0.8:
                return [MageEnemy(x())]
            else:
                return [HeavyEnemy(x())]