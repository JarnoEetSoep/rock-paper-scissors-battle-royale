try:
    import pyi_splash
except:
    pass

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
import matplotlib.figure
matplotlib.use("Agg") 
import matplotlib.axes
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import argparse

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

class Debug(Flag):
    HITBOXES = auto()
    DIRECTION = auto()
    TEAMS_COUNTS = auto()

class RPSEntityType(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

class RPSEntity:
    def __init__(self, entity_type: RPSEntityType, width, height) -> None:
        self.entity_type = entity_type

        self.dir = random() * 2 * pi
        self.x = random() * width
        self.y = random() * height

class Game(tk.Frame):
    def __init__(self, master, params, debug: Debug) -> None:
        super().__init__(master)
        self.master = master
        self.params = params
        self.place(x=0, y=0, relwidth=1, relheight=1)

        self.debug = debug

        self.master.protocol("WM_DELETE_WINDOW", self.quit)

        self.load_assets()
        self.initialise_game()

        if params.draw_graph:
            self.graph_window = GraphWindow(self)

        self.master.update()

    def load_assets(self) -> None:
        self.rock_sprite = ImageTk.PhotoImage(Image.open(resource_path("rock.png")).resize((16, 16)))
        self.paper_sprite = ImageTk.PhotoImage(Image.open(resource_path("paper.png")).resize((16, 16)))
        self.scissors_sprite = ImageTk.PhotoImage(Image.open(resource_path("scissors.png")).resize((16, 16)))
        self.hitbox = ImageTk.PhotoImage(Image.open(resource_path("hitbox.png")).resize((16, 16)))
        self.overlay = ImageTk.PhotoImage(Image.open(resource_path("overlay.png")).resize((self.params.width, self.params.height)))
    
    def get_sprite(self, entity: RPSEntity) -> tk.PhotoImage:
        match entity.entity_type:
            case RPSEntityType.ROCK: return self.rock_sprite
            case RPSEntityType.PAPER: return self.paper_sprite
            case RPSEntityType.SCISSORS: return self.scissors_sprite

    def initialise_game(self) -> None:
        self.game = tk.Canvas(self, width=self.params.width, height=self.params.height, bd=0, highlightthickness=0, background="#e4d5b7")
        self.game.pack()

        self.entities = [RPSEntity(RPSEntityType.ROCK, self.params.width, self.params.height) for _ in range(self.params.spawn_amount[0])] + \
            [RPSEntity(RPSEntityType.PAPER, self.params.width, self.params.height) for _ in range(self.params.spawn_amount[1])] + \
            [RPSEntity(RPSEntityType.SCISSORS, self.params.width, self.params.height) for _ in range(self.params.spawn_amount[2])]

        self.VELOCITY = .2
        self.SIZE = 8


    def update_game(self) -> None:
        self.game.delete("all")

        self.delta_time = time.time() - self.prev_time
        self.prev_time = time.time()
        
        counts = [0, 0, 0]
        for entity in self.entities:
            if not (self.SIZE / 2) < (entity.x + cos(entity.dir) * self.VELOCITY / self.delta_time) < (self.params.width - self.SIZE / 2):
                entity.dir += entity.dir + pi
                entity.dir %= 2 * pi
            
            if not (self.SIZE / 2) < (entity.y + sin(entity.dir) * self.VELOCITY / self.delta_time) < (self.params.height - self.SIZE / 2):
                entity.dir = -entity.dir + 2 * pi

            move_dir = random() * 2 * pi
            move_size = (cos(entity.dir - move_dir) + 1) * self.VELOCITY / self.delta_time

            entity.x += cos(move_dir) * move_size
            entity.y += sin(move_dir) * move_size

            entity.x = clamp(entity.x, self.SIZE / 2, self.params.width - self.SIZE / 2)
            entity.y = clamp(entity.y, self.SIZE / 2, self.params.height - self.SIZE / 2)

            self.game.create_image(entity.x, entity.y, image=self.get_sprite(entity))
            if Debug.HITBOXES in self.debug: self.game.create_image(entity.x, entity.y, image=self.hitbox)
            if Debug.DIRECTION in self.debug: self.game.create_line(entity.x, entity.y, entity.x + cos(entity.dir) * 50, entity.y + sin(entity.dir) * 50, fill="black")

            counts[entity.entity_type.value - 1] += 1

        if self.params.draw_graph and self.graph_window.winfo_exists():
            self.graph_window.update_graph(counts)
        
        if counts.count(0) == 2:
            self.game.create_image(self.params.width / 2, self.params.height / 2, image=self.overlay)
            
            winner = {
                1: "ROCK",
                2: "PAPER",
                3: "SCISSORS",
            }[counts.index(len(self.entities)) + 1]

            self.game.create_text(self.params.width / 2, 0.3 * self.params.height, text=f"{winner} WON!", font="verdana 28 bold", fill="white")

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
        
        self.next_after = self.master.after(50, self.update_game)

    def mainloop(self) -> Never:
        self.prev_time = time.time()
        self.next_after = self.master.after(50, self.update_game)

        super().mainloop()
    
    def quit(self) -> None:
        self.master.after_cancel(self.next_after)
        self.master.destroy()

class GraphWindow(tk.Toplevel):
    def __init__(self, master: Game) -> None:
        super().__init__(master)
        self.master = master

        self.title("Teams graph")
        self.resizable(False, False)

        plt.style.use("fivethirtyeight")

        self.x = []
        self.rock = []
        self.paper = []
        self.scissors = []

        self.index = count()

        self.fig = plt.figure(figsize=(7,4), dpi=100)
        self.ax = self.fig.add_subplot()
        self.ax.set_ylim(0, 100)

        self.ax.plot(0, 0, color="red", label="Rock %")
        self.ax.plot(0, 0, color="green", label="Paper %")
        self.ax.plot(0, 0, color="blue", label="Scissors %")

        self.fig.legend(loc="upper left", bbox_to_anchor=((0.1, 1)))

        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.get_tk_widget().pack()

        self.thread = threading.Thread()
    
    def update_graph(self, counts):
        self.x = np.append(self.x, next(self.index))
        self.rock = np.append(self.rock, counts[0])
        self.paper = np.append(self.paper, counts[1])
        self.scissors = np.append(self.scissors, counts[2])

        if not self.thread.is_alive():
            self.thread = threading.Thread(target=GraphWindow.__update_graph_thread, args=(self.fig, self.ax, not self.master.params.no_blit, self.x, self.rock / sum(counts) * 100, self.paper / sum(counts) * 100, self.scissors / sum(counts) * 100), daemon=True)
            self.thread.start()

            if not self.master.params.no_blit:
                self.x = self.x[-2:]
                self.rock = self.rock[-2:]
                self.paper = self.paper[-2:]
                self.scissors = self.scissors[-2:]
    
    def __update_graph_thread(fig: matplotlib.figure.Figure, ax: matplotlib.axes.Axes, blit, x, rock, paper, scissors):
        if blit:
            bg = fig.canvas.copy_from_bbox(ax.bbox)

            r = ax.plot(x, rock, color="red", linewidth=2)[0]
            p = ax.plot(x, paper, color="green", linewidth=2)[0]
            s = ax.plot(x, scissors, color="blue", linewidth=2)[0]

            fig.canvas.restore_region(bg)

            ax.draw_artist(r)
            ax.draw_artist(p)
            ax.draw_artist(s)

            fig.canvas.blit(ax.bbox)
        else:
            ax.cla()

            ax.plot(x, rock, color="red", label="Rock %", linewidth=2)
            ax.plot(x, paper, color="green", label="Paper %", linewidth=2)
            ax.plot(x, scissors, color="blue", label="Scissors %", linewidth=2)
            ax.set_ylim([0, 100])

            fig.legend(loc="upper left", bbox_to_anchor=((0.1, 1)))

        try:
            fig.canvas.draw()
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description="A rock-paper-scissors battle royale")

    parser.add_argument("-W", "--width", type=int, nargs=1, metavar="WIDTH", default=350, help="Width of the game window, will default to 350")
    parser.add_argument("-H", "--height", type=int, nargs=1, metavar="HEIGHT", default=500, help="Height of the game window, will default to 500")
    parser.add_argument("-G", "--draw-graph", action="store_true", help="Draw a live graph of the populations of rock, paper and scissors")
    parser.add_argument("-B", "--no-blit", action="store_true", help="Disable blitting for drawing the live graph (not recommended)")
    parser.add_argument("-N", "--spawn_amount", type=int, metavar="NUM", nargs=3, default=[20, 20, 20], help="Number of rocks, papers and scissors (respectively) to spawn")

    args = parser.parse_args()

    if isinstance(args.width, list):
        args.width = args.width[0]
    
    if isinstance(args.height, list):
        args.height = args.height[0]

    root = tk.Tk()
    root.lift()
    root.resizable(False, False)
    root.minsize(args.width, args.height)
    root.title("Rock Paper Scissors Battle Royale")

    game = Game(root, args, [])

    try:
        pyi_splash.close()
    except:
        pass

    game.mainloop()

if __name__ == "__main__":
    main()
