import tkinter as tk
from PIL import Image, ImageTk
import time
from math import sin, cos, pi, sqrt
from enum import Enum, Flag, auto
from random import random
from typing import Never
from itertools import combinations, count
import os
import sys
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading

try:
    import pyi_splash
except:
    pass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

WIDTH = 350
HEIGHT = 500
DRAW_GRAPH = False

class Debug(Flag):
    HITBOXES = auto()
    DIRECTION = auto()
    TEAMS_COUNTS = auto()

class RPSEntityType(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3
        

class RPSEntity:
    def __init__(self, entity_type: RPSEntityType) -> None:
        self.entity_type = entity_type

        self.dir = random() * 2 * pi
        self.x = random() * WIDTH
        self.y = random() * HEIGHT

class Game(tk.Frame):
    def __init__(self, master, debug: Debug) -> None:
        super().__init__(master)
        self.master = master
        self.place(x=0, y=0, relwidth=1, relheight=1)

        self.debug = debug

        self.master.protocol("WM_DELETE_WINDOW", self.quit)

        self.load_assets()
        self.initialise_game()

        if DRAW_GRAPH:
            self.graph_window = GraphWindow(self)

        self.master.update()

    def load_assets(self) -> None:
        self.rock_sprite = ImageTk.PhotoImage(Image.open(resource_path("rock.png")).resize((16, 16)))
        self.paper_sprite = ImageTk.PhotoImage(Image.open(resource_path("paper.png")).resize((16, 16)))
        self.scissors_sprite = ImageTk.PhotoImage(Image.open(resource_path("scissors.png")).resize((16, 16)))
        self.hitbox = ImageTk.PhotoImage(Image.open(resource_path("hitbox.png")).resize((16, 16)))
        self.overlay = ImageTk.PhotoImage(Image.open(resource_path("overlay.png")).resize((WIDTH, HEIGHT)))
    
    def get_sprite(self, entity: RPSEntity) -> tk.PhotoImage:
        match entity.entity_type:
            case RPSEntityType.ROCK: return self.rock_sprite
            case RPSEntityType.PAPER: return self.paper_sprite
            case RPSEntityType.SCISSORS: return self.scissors_sprite

    def initialise_game(self) -> None:
        self.game = tk.Canvas(self, width=WIDTH, height=HEIGHT, bd=0, highlightthickness=0, background="#e4d5b7")
        self.game.pack()

        self.entities = [RPSEntity(RPSEntityType.ROCK) for _ in range(20)] + \
            [RPSEntity(RPSEntityType.PAPER) for _ in range(20)] + \
            [RPSEntity(RPSEntityType.SCISSORS) for _ in range(20)]

        self.VELOCITY = .2
        self.SIZE = 8


    def update_game(self) -> None:
        self.game.delete("all")

        self.delta_time = time.time() - self.prev_time
        self.prev_time = time.time()
        
        counts = [0, 0, 0]
        for entity in self.entities:
            if not (self.SIZE / 2) < (entity.x + cos(entity.dir) * self.VELOCITY / self.delta_time) < (WIDTH - self.SIZE / 2):
                entity.dir += entity.dir + pi
                entity.dir %= 2 * pi
            
            if not (self.SIZE / 2) < (entity.y + sin(entity.dir) * self.VELOCITY / self.delta_time) < (HEIGHT - self.SIZE / 2):
                entity.dir = -entity.dir + 2 * pi

            move_dir = random() * 2 * pi
            move_size = (cos(entity.dir - move_dir) + 1) * self.VELOCITY / self.delta_time

            entity.x += cos(move_dir) * move_size
            entity.y += sin(move_dir) * move_size

            entity.x = clamp(entity.x, self.SIZE / 2, WIDTH - self.SIZE / 2)
            entity.y = clamp(entity.y, self.SIZE / 2, HEIGHT - self.SIZE / 2)

            self.game.create_image(entity.x, entity.y, image=self.get_sprite(entity))
            if Debug.HITBOXES in self.debug: self.game.create_image(entity.x, entity.y, image=self.hitbox)
            if Debug.DIRECTION in self.debug: self.game.create_line(entity.x, entity.y, entity.x + cos(entity.dir) * 50, entity.y + sin(entity.dir) * 50, fill="black")

            counts[entity.entity_type.value - 1] += 1

        if DRAW_GRAPH and self.graph_window.is_alive:
            self.graph_window.update_graph(counts)
        
        if counts.count(0) == 2:
            self.game.create_image(WIDTH / 2, HEIGHT / 2, image=self.overlay)
            
            winner = {
                1: "ROCK",
                2: "PAPER",
                3: "SCISSORS",
            }[counts.index(len(self.entities)) + 1]

            self.game.create_text(WIDTH / 2, 0.3 * HEIGHT, text=f"{winner} WON!", font="verdana 28 bold", fill="white")

            return

        for (entity, other) in combinations(self.entities, 2):
            if entity.entity_type == other.entity_type:
                    continue

            if sqrt((entity.x - other.x)**2 + (entity.y - other.y)**2) <= 2 * self.SIZE:
                if (entity.entity_type, other.entity_type) in [
                    (RPSEntityType.ROCK, RPSEntityType.PAPER),
                    (RPSEntityType.PAPER, RPSEntityType.SCISSORS),
                    (RPSEntityType.SCISSORS, RPSEntityType.ROCK)
                ]:
                    entity.entity_type = other.entity_type
                    #self.entities.remove(entity)
                else:
                    other.entity_type = entity.entity_type
                    #self.entities.remove(other)
        
        if Debug.TEAMS_COUNTS in self.debug:
            self.game.create_text(10, 10, text=f"Rock: {counts[0]}", fill="black", font="verdana", anchor=tk.NW)
            self.game.create_text(10, 30, text=f"Paper: {counts[1]}", fill="black", font="verdana", anchor=tk.NW)
            self.game.create_text(10, 50, text=f"scissors: {counts[2]}", fill="black", font="verdana", anchor=tk.NW)
        
        self.master.after(50, self.update_game)

    def mainloop(self) -> Never:
        self.prev_time = time.time()
        self.master.after(50, self.update_game)

        super().mainloop()
    
    def quit(self) -> None:
        self.master.destroy()

class GraphWindow(tk.Toplevel):
    def __init__(self, master) -> None:
        super().__init__(master)
        self.master = master

        self.protocol("WM_DELETE_WINDOW", self.quit)

        self.title("Teams graph")
        self.resizable(False, False)
        self.is_alive = True

        plt.style.use("fivethirtyeight")
        matplotlib.use("TkAgg") 

        self.x = []
        self.rock = []
        self.paper = []
        self.scissors = []

        self.index = count()

        self.fig = plt.figure(figsize=(7,4), dpi=100)
        self.ax = self.fig.add_subplot()
        self.ax.set_ylim([0, 100])

        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.get_tk_widget().pack()

        self.thread = threading.Thread()
    
    def update_graph(self, counts):
        self.x = np.append(self.x, next(self.index))
        self.rock = np.append(self.rock, counts[0])
        self.paper = np.append(self.paper, counts[1])
        self.scissors = np.append(self.scissors, counts[2])

        if not self.thread.is_alive():
            self.thread = threading.Thread(target=GraphWindow.__update_graph_thread, args=(self.fig, self.ax, self.x, self.rock / sum(counts) * 100, self.paper / sum(counts) * 100, self.scissors / sum(counts) * 100))
            self.thread.start()
    
    def __update_graph_thread(fig, ax, x, rock, paper, scissors):
        ax.cla()

        ax.plot(x, rock, color="red", label="Rock %")
        ax.plot(x, paper, color="green", label="Paper %")
        ax.plot(x, scissors, color="blue", label="Scissors %")
        ax.set_ylim([0, 100])

        fig.legend(loc="upper left", bbox_to_anchor=((0.1, 1)))

        fig.canvas.draw()

    def quit(self) -> None:
        self.is_alive = False
        self.destroy()

def main():
    root = tk.Tk()
    root.lift()
    root.resizable(False, False)
    root.minsize(WIDTH, HEIGHT)
    root.title("Rock Paper Scissors Battle Royale")

    game = Game(root, [])

    try:
        pyi_splash.close()
    except:
        pass

    game.mainloop()

if __name__ == "__main__":
    main()
