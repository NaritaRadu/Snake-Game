import random
import pygame
import sys

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

    CELL_SIZE = 20  # Dimensiunea unui pătrat în pixeli

    def __init__(self, width=30, height=20):
        self.width = width
        self.height = height
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.CELL_SIZE, self.height * self.CELL_SIZE))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        init_body = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
        self.snake = Snake(init_body, self.DIR_RIGHT)
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
            # 1. Handling Input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.snake.direction != self.DIR_DOWN:
                        self.snake.set_direction(self.DIR_UP)
                    elif event.key == pygame.K_DOWN and self.snake.direction != self.DIR_UP:
                        self.snake.set_direction(self.DIR_DOWN)
                    elif event.key == pygame.K_LEFT and self.snake.direction != self.DIR_RIGHT:
                        self.snake.set_direction(self.DIR_LEFT)
                    elif event.key == pygame.K_RIGHT and self.snake.direction != self.DIR_LEFT:
                        self.snake.set_direction(self.DIR_RIGHT)

            # 2. Game Logic Update
            head_x, head_y = self.snake.head()
            dir_x, dir_y = self.snake.direction
            next_pos = ((head_x + dir_x) % self.width, (head_y + dir_y) % self.height)

            if next_pos in self.snake.body:
                print("Game Over!")
                running = False
                continue

            if next_pos == self.current_apple.location:
                self.snake.extend_body(next_pos)
                self._regenerate_apple()
            else:
                self.snake.take_step(next_pos)

            # 3. Render Graphics
            self.screen.fill((15, 15, 15))  # Fundal închis

            # Desenează marul
            ax, ay = self.current_apple.location
            pygame.draw.rect(self.screen, (230, 50, 50), 
                             (ax * self.CELL_SIZE, ay * self.CELL_SIZE, self.CELL_SIZE - 1, self.CELL_SIZE - 1))

            # Desenează șarpele
            for x, y in self.snake.body:
                pygame.draw.rect(self.screen, (46, 204, 113), 
                                 (x * self.CELL_SIZE, y * self.CELL_SIZE, self.CELL_SIZE - 1, self.CELL_SIZE - 1))

            pygame.display.flip()
            self.clock.tick(10)  # Viteza jocului (10 FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PygameSnakeGame(30, 20)
    game.run()