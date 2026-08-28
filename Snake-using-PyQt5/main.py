import sys
import random
import json
import os
from PyQt5.QtWidgets import QApplication,QWidget,QMessageBox
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtGui import QPainter,QColor,QFont

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

class PyQtSnakeGame(QWidget):
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
        super().__init__()
        self.board_width = width
        self.board_height = height
        
        self.setWindowTitle("Snake Game - PyQt5")
        self.setFixedSize(self.board_width*self.CELL_SIZE,self.board_height*self.CELL_SIZE)
        self.state=self.STATE_MENU
        self.score=0
        self.high_score=self._load_high_score()
        
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.game_loop)
        
        self.reset_game()
    
    def _load_high_score(self):
        if os.path.exists(self.SCORE_FILE):
            try:
                with open(self.SCORE_FILE,"r") as f:
                    return json.load(f).get("high_score",0)
            except (json.JSONDecodeError,IOError):
                return 0
        return 0
    
    def _save_high_score(self):
        with open(self.SCORE_FILE,"w") as f:
            json.dump({"high_score":self.high_score},f)
    
    def reset_game(self):
        init_body=[(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
        self.snake=Snake(init_body,self.DIR_RIGHT)
        self.score=0
        self._regenerate_apple()
    
    def _regenerate_apple(self):
        snake_set=set(self.snake.body)
        while True:
            loc=(random.randint(0,self.board_width-1),random.randint(0,self.board_height-1))
            if loc not in snake_set:
                self.current_apple=Apple(loc)
                break
    
    def keyPressEvent(self,event):
        key=event.key()
        
        if self.state==self.STATE_MENU:
            if key==Qt.Key_Space:
                self.reset_game()
                self.state=self.STATE_PLAYING
                self.timer.start(100)
        elif self.state== self.STATE_PLAYING:
            if key in (Qt.Key_Up, Qt.Key_W) and self.snake.direction != self.DIR_DOWN:
                self.snake.set_direction(self.DIR_UP)
            elif key in (Qt.Key_Down, Qt.Key_S) and self.snake.direction != self.DIR_UP:
                self.snake.set_direction(self.DIR_DOWN)
            elif key in (Qt.Key_Left, Qt.Key_A) and self.snake.direction != self.DIR_RIGHT:
                self.snake.set_direction(self.DIR_LEFT)
            elif key in (Qt.Key_Right, Qt.Key_D) and self.snake.direction != self.DIR_LEFT:
                self.snake.set_direction(self.DIR_RIGHT)
        
        elif self.state== self.STATE_GAMEOVER:
            if key== Qt.Key_Space:
                self.reset_game()
                self.state=self.STATE_PLAYING
                self.timer.start(100)
            elif key==Qt.Key_Escape:
                self.state==self.STATE_MENU
                self.update()
    
    def game_loop(self):
        if self.state!=self.STATE_PLAYING:
            return
        
        head_x, head_y = self.snake.head()
        dir_x, dir_y = self.snake.direction
        next_pos = ((head_x + dir_x) % self.board_width, (head_y + dir_y) % self.board_height)

        
        if next_pos in self.snake.body:
            self.timer.stop()
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()
            self.state = self.STATE_GAMEOVER
            self.update()
            return

        
        if next_pos == self.current_apple.location:
            self.snake.extend_body(next_pos)
            self.score += 10
            self._regenerate_apple()
        else:
            self.snake.take_step(next_pos)

        
        self.update()
    
    def paintEvent(self, event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.fillRect(self.rect(),QColor(15,15,15))
        if self.state == self.STATE_MENU:
            painter.setPen(QColor(46, 204, 113))
            painter.setFont(QFont("Arial", 26, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignHCenter | Qt.AlignVCenter, "SNAKE GAME\n\n[ SPACE ] for Start")

        elif self.state == self.STATE_PLAYING:
            
            painter.setBrush(QColor(230, 50, 50))
            painter.setPen(Qt.NoPen)
            ax, ay = self.current_apple.location
            painter.drawRect(ax * self.CELL_SIZE, ay * self.CELL_SIZE, self.CELL_SIZE - 1, self.CELL_SIZE - 1)

            
            painter.setBrush(QColor(46, 204, 113))
            for x, y in self.snake.body:
                painter.drawRect(x * self.CELL_SIZE, y * self.CELL_SIZE, self.CELL_SIZE - 1, self.CELL_SIZE - 1)

            
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(10, 20, f"Scor: {self.score}")

        elif self.state == self.STATE_GAMEOVER:
            painter.setPen(QColor(231, 76, 60))
            painter.setFont(QFont("Arial", 22, QFont.Bold))
            msg = f"GAME OVER\n\nScore: {self.score}\nHigh Score: {self.high_score}\n\n[ SPACE ] Restart | [ ESC ] Meniu"
            painter.drawText(self.rect(), Qt.AlignCenter, msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = PyQtSnakeGame(30, 20)
    game.show()
    sys.exit(app.exec_())