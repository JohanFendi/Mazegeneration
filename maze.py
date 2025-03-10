import pygame as pg
import random

from constants import * 


class Cell:
    def __init__(self, object_type, x_cord, y_cord):
        self.object_type = object_type
        self.x_cord = x_cord # Not in pixels
        self.y_cord = y_cord 
    

    def convert_to_wall(self):
        self.object_type = WALL


    def convert_to_path(self):
        self.object_type = PATH


#Main datastructure
class Maze:
    def __init__(self, maze_height, maze_width):
        self.max_edge_weight = MAX_EDGE_WEIGHT
        self.width = maze_width
        self.height = maze_height
        self.cell_width = CELL_WIDTH
        self.grid = self.create_grid()
        self.edges = self.create_edges()
        self.disjointed_set = Disjointed_set(self)
        self.graphical_corner_x = MAX_GRAPHICAL_MAZE_WIDTH // 2 - (maze_width * CELL_WIDTH) // 2
        self.graphical_corner_y = WINDOW_HEIGHT // 2 - (maze_height * CELL_WIDTH) // 2

        
    #Draws maze from its top left corner position in the window
    def draw(self, window):
        for y in range(self.height):
            for x in range(self.width):
                start_x = x * self.cell_width + self.graphical_corner_x
                start_y = y * self.cell_width + self.graphical_corner_y
                end_x = start_x + self.cell_width 
                end_y = start_y + self.cell_width

                pg.draw.polygon(window, MAZE_COLORS[self.grid[y][x].object_type],
                ((start_x, start_y), (end_x, start_y), (end_x, end_y), (start_x, end_y)))


    #Creates grid in a checkered pattern
    def create_grid(self):
        grid = [[] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
               
                if y % 2 == 0: #If y is even, then alternate between path and undecided cells
                    if x % 2 == 1:
                        grid[y].append(Cell(UNDECIDED, x, y))
                    else:
                        grid[y].append(Cell(PATH, x, y))
                else:  #If y is odd, then alternate between undecided and wall cells
                    if x % 2 == 0:
                        grid[y].append(Cell(UNDECIDED, x, y))
                    else:
                        grid[y].append(Cell(WALL, x, y))
        return grid


    #Returns edges in the following format: [(weight, cell1, edge_cell, cell2)]
    def create_edges(self):
        edges = [] 
        for cell_y_cord in range(0, self.height, 2):
            for cell_x_cord in range(0, self.width, 2):

                if cell_x_cord < self.width-1: #Adds the path 2 cells to the right
                    horisontal_edge = (random.randint(1, self.max_edge_weight),self.grid[cell_y_cord][cell_x_cord],
                                        self.grid[cell_y_cord][cell_x_cord+1], self.grid[cell_y_cord][cell_x_cord+2])
                    edges.append(horisontal_edge)

                if cell_y_cord < self.height-1: #Adds the path 2 cells down
                    vertical_edge = (random.randint(1, self.max_edge_weight),self.grid[cell_y_cord][cell_x_cord],
                                        self.grid[cell_y_cord+1][cell_x_cord], self.grid[cell_y_cord+2][cell_x_cord])
                    edges.append(vertical_edge)

        edges.sort(key=lambda edge:edge[0]) #Sorts edges based on the weight
        return edges

    
    #Executes exactly one iteration of the kruskals algorithm, 
    #changes the colors of the cells being processed
    def kruskals_step(self, window, clock):
        _, cell1, edge_cell, cell2 = self.edges.pop()
        edge_cell.object_type = EDGE_BEING_PROCESSED
        cell1.object_type = CONNECTION_BEING_PROCESSED
        cell2.object_type = CONNECTION_BEING_PROCESSED
        
        self.draw(window)    
        pg.display.update()  
        clock.tick(FPS)          

        if self.disjointed_set.union(cell1, cell2):
            edge_cell.convert_to_path()
        else:
            edge_cell.convert_to_wall()
        
        cell1.object_type = PATH
        cell2.object_type = PATH
        

#Creates disjointed set and fill it with the cells of the maze
class Disjointed_set:
    def __init__(self, maze):
        self.parent = {}
        self.rank = {}

        for row in maze.grid:
            for cell in row:
                self.parent[cell] = cell
                self.rank[cell] = 0


    #Connects two cells if they have different parents/roots
    def union(self, cell1, cell2):
        parent1 = self.find(cell1)
        parent2 = self.find(cell2)

        if parent1 == parent2:
            return False
        
        if self.rank[parent1] == self.rank[parent2]:
            self.rank[parent1] += 1
            self.parent[parent2] = parent1
        elif self.rank[parent1] > self.rank[parent2]:
            self.parent[parent2] = parent1
        else:
            self.parent[parent1] = parent2

        return True


    #Finds root of set with path compression
    def find(self, cell):
        if self.parent[cell] == cell:
            return cell
    
        self.parent[cell] = self.find(self.parent[cell])
        return self.parent[cell]

