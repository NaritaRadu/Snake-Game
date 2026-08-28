import random
import pygame
import sys
import json
import os

class Snake:
    def __init__(self, init_body, init_direction):
        self.body = init_body
        self.direction = init_direction

    def head(self):
        return self.body[-1]

    def take_step(self, position):
        self.body.pop(0)
        self.body.append(position)

    def extend_body(self, position):
        self.body.append(position)

    def set_direction(self, direction):
        self.direction = direction


class Apple:
    def __init__(self, location):
        self.location = location


class PygameSnakeGame:
    DIR_UP = (0, -1)
    DIR_DOWN = (0, 1)
    DIR_LEFT = (-1, 0)
    DIR_RIGHT = (1, 0)

    CELL_SIZE = 20  
    SCORE_FILE="highscore.json"
    
    STATE_MENU=0
    STATE_PLAYING=1
    STATE_GAMEOVER=2
    
    def __init__(self, width=30, height=20):
        self.width = width
        self.height = height
        
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.width * self.CELL_SIZE, self.height * self.CELL_SIZE))
        pygame.display.set_caption("Snake Game-Enhanced")
        self.clock = pygame.time.Clock()
        self.font=pygame.font.SysFont("arial",24)
        self.large_font=pygame.font.SysFont("arial",36)
        self.state=self.STATE_MENU
        self.high_score=self._load_high_score()
        self.score=0

        self._init_sounds()
        self.reset_game()
    
    def _init_sounds(self):
        try:
            self.eat_sound=pygame.mixer.Sound(buffer=bytes([128+int(127 *(i % 10 < 5)) for i in range(1000)]))
            self.gameover_sound=pygame.mixer.Sound(buffer=bytes([128+int(127 *(i % 30 < 15)) for i in range(3000)]))
        except Exception:
            self.eat_sound=None
            self.gameover_sound=None
    
    def _load_high_score(self):
        if os.path.exists(self.SCORE_FILE):
            try:
                with open(self.SCORE_FILE,"r")as f:
                    data=json.load(f)
                    return data.get("high_score",0)
            except (json.JSONDecodeError,IOError):
                return 0
        return 0
    
    def _save_high_score(self):
        with open(self.SCORE_FILE,"w") as f:
            json.dump({"high_score":self.high_score},f)
    
    def reset_game(self):
        init_body=[(0,0),(1,0),(2,0),(3,0),(4,0)]
        self.snake=Snake(init_body,self.DIR_RIGHT)
        self.score=0
        self._regenerate_apple()
        
        
    def _regenerate_apple(self):
        snake_set = set(self.snake.body)
        while True:
            loc = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if loc not in snake_set:
                self.current_apple = Apple(loc)
                break

    def run(self):
        running = True
        while running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(10)
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == self.STATE_MENU:
                    if event.key==pygame.K_SPACE:
                        self.reset_game()
                        self.state=self.STATE_PLAYING
                elif self.state==self.STATE_PLAYING:
                    if event.key == pygame.K_UP and self.snake.direction != self.DIR_DOWN:
                        self.snake.set_direction(self.DIR_UP)
                    elif event.key == pygame.K_DOWN and self.snake.direction != self.DIR_UP:
                        self.snake.set_direction(self.DIR_DOWN)
                    elif event.key == pygame.K_LEFT and self.snake.direction != self.DIR_RIGHT:
                        self.snake.set_direction(self.DIR_LEFT)
                    elif event.key == pygame.K_RIGHT and self.snake.direction != self.DIR_LEFT:
                        self.snake.set_direction(self.DIR_RIGHT)
                elif self.state==self.STATE_GAMEOVER:
                    if event.key==pygame.K_SPACE:
                        self.reset_game()
                        self.state=self.STATE_PLAYING
                    elif event.key==pygame.K_ESCAPE:
                        self.state=self.STATE_MENU
    def _update(self):
        if self.state!=self.STATE_PLAYING:
            return
        
           
        head_x, head_y = self.snake.head()
        dir_x, dir_y = self.snake.direction
        next_pos = ((head_x + dir_x) % self.width, (head_y + dir_y) % self.height)

        if next_pos in self.snake.body:
            if self.gameover_sound:
                self.gameover_sound.play()
            
            if self.score> self.high_score:
                self.high_score=self.score
                self._save_high_score()
            self.state=self.STATE_GAMEOVER
            return

        if next_pos == self.current_apple.location:
            self.snake.extend_body(next_pos)
            self.score+=10
            if self.eat_sound:
                self.eat_sound.play()
            self._regenerate_apple()
        else:
            self.snake.take_step(next_pos)
    
    def _draw(self):
        self.screen.fill((15, 15, 15))  
        
        if self.state==self.STATE_MENU:
            title=self.large_font.render("SNAKE GAME",True,(46,204,113))
            start_txt=self.font.render("PRESS SPACE to start",True,(255,255,255))
            hs_txt=self.font.render(f"HIGH SCORE:{self.high_score}",True,(241,196,15))
            self.screen.blit(title,(self.width*self.CELL_SIZE // 2 -title.get_width() // 2, 120))
            self.screen.blit(start_txt, (self.width * self.CELL_SIZE // 2 - start_txt.get_width() // 2, 200))
            self.screen.blit(hs_txt, (self.width * self.CELL_SIZE // 2 - hs_txt.get_width() // 2, 260))

        elif self.state==self.STATE_PLAYING:
                
            ax, ay = self.current_apple.location
            pygame.draw.rect(self.screen, (230, 50, 50), 
                             (ax * self.CELL_SIZE, ay * self.CELL_SIZE, self.CELL_SIZE - 1, self.CELL_SIZE - 1))

            
            for x, y in self.snake.body:
                pygame.draw.rect(self.screen, (46, 204, 113), 
                                 (x * self.CELL_SIZE, y * self.CELL_SIZE, self.CELL_SIZE - 1, self.CELL_SIZE - 1))

            score_txt=self.font.render(f"Score:{self.score}",True,(255,255,255))
            self.screen.blit(score_txt,(10,10))
        elif self.state==self.STATE_GAMEOVER:
            go_title=self.large_font.render("GAME OVER",True,(231,76,60))
            final_score=self.font.render(f"SCORE OBTAINED:{self.score}",True,(255,255,255))
            hs_txt=self.font.render(f"BEST SCORE:{self.high_score}",True,(241,196,15))
            restart_txt=self.font.render("PRESS SPACE for RESTART \nESC for MENU",True,(150,150,150))
            
            self.screen.blit(go_title, (self.width * self.CELL_SIZE // 2 - go_title.get_width() // 2, 100))
            self.screen.blit(final_score, (self.width * self.CELL_SIZE // 2 - final_score.get_width() // 2, 170))
            self.screen.blit(hs_txt, (self.width * self.CELL_SIZE // 2 - hs_txt.get_width() // 2, 210))
            self.screen.blit(restart_txt, (self.width * self.CELL_SIZE // 2 - restart_txt.get_width() // 2, 280))
        
        pygame.display.flip()
              

        

if __name__ == "__main__":
    game = PygameSnakeGame(30, 20)
    game.run()