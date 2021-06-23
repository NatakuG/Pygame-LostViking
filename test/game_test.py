from pygame.locals import *
from pygame.sprite import spritecollideany, collide_rect_ratio, groupcollide
import pygame
from LostViking.src.groups import *
from LostViking.src.constants import *
from LostViking.src.level1 import *
from LostViking.src.player import *


def collide_test(a, b):
    if pygame.sprite.collide_rect(a, b):
        if pygame.sprite.collide_rect_ratio(0.5)(a, b):
            return True
    return False


def collide_detection(player1):
    """
    supply_get = pygame.sprite.spritecollideany(self.player, self.group_supply)
    if supply_get != None:
        if pygame.sprite.collide_circle_ratio(0.65)(self.player, supply_get):
            supply_get.catched(self.player)
            G.SCORE += supply_get.score
            if supply_get.type == SupplyType.Bomb:
                self.bomb_text.change_text("Bomb: " + str(G.BOMB))
            elif supply_get.type == SupplyType.Life:
                self.life_text.change_text("Life: " + str(G.LIFE))
    """
    if player1.is_active and not player1.is_invincible:
        bullet_hit = spritecollideany(player1, Enemy_Bullet_G)
        if bullet_hit is not None:
            if collide_rect_ratio(0.65)(player1, bullet_hit):
                if player1.hit(100):
                    bullet_hit.hit()
                    # G.LIFE -= 1
        enemy_hit = spritecollideany(player1, Enemy_G)
        if enemy_hit is not None:
            if collide_rect_ratio(0.65)(player1, enemy_hit):
                if enemy_hit.is_active:
                    if player1.hit(100):
                        if enemy_hit not in BOSS_G:
                            enemy_hit.hit(1000)
                        # G.LIFE -= 1

    enemy_hit = groupcollide(Enemy_G, Player_Bullet_G, False, True, collide_test)
    if len(enemy_hit) > 0:
        for enemy, bullets in enemy_hit.items():
            for each_bullets in bullets:
                enemy.hit(each_bullets.damage)
                each_bullets.hit()
    """
    if len(self.bomb) > 0:
        if self.bomb.sprite.is_active and self.bomb.sprite.explode_flag:
            self.bomb.sprite.is_active = False
            for each in self.enemies:
                if each.rect.bottom > 0 and each.is_active:
                    each.hit(800)
                    if not each.is_active:
                        G.SCORE += each.score
                        each.destroy()
                        each.kill()
                        self.enemies_die.add(each)
            self.enemy_bullets.empty()

    self.life_text.change_text("Life: " + str(G.LIFE))
    self.score_text.change_text("Score: " + str(G.SCORE))
    """


def test_game():
    # Init Environment
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SCREEN_SIZE)

    # Init Player
    init_player()
    player1, _ = create_player()

    # Init Enemy
    init_level()
    #level_event_config()
    from LostViking.src.level1.Enemy_Phoenix import add_enemy_phoenix
    add_enemy_phoenix()

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            # --------------- Key Down Events ---------------
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            level_events_handler(event=event)
            detect_player_event(event, player1=player1)
        detect_key_pressed(player1)

        collide_detection(player1=player1)

        screen.fill(BLACK)

        Destroyed_Plane_G.update()
        Destroyed_Plane_G.draw(screen)

        Bullet_G.update()
        Bullet_G.draw(screen)
        Enemy_G.update()
        Enemy_G.draw(screen)
        Shield_G.update()
        Shield_G.draw(screen)
        Player1_G.update()
        Player1_G.draw(screen)
        BOSS_G.update()
        BOSS_G.draw(screen)

        # Display
        pygame.display.flip()

        clock.tick(60)


if __name__ == "__main__":
    test_game()

    pygame.quit()
    import sys

    sys.exit()
