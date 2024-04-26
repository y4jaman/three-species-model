import pygame
import random
import math
import matplotlib.pyplot as plt

# Initialize matplotlib plot
plt.ion()  # Turn on interactive mode
figure, ax = plt.subplots()
sheep_counts = []
wolf_counts = []
grass_counts = []
ax.set_title('Population over Time')
ax.set_xlabel('Ticks')
ax.set_ylabel('Population')

WIDTH, HEIGHT = 800, 800  
GRID_SIZE = 50
CELL_SIZE = WIDTH // GRID_SIZE
GREEN = (1, 50, 32)
BROWN = (150, 75, 0)
WHITE = (255, 255, 255)
SHEEP_REPRODUCTION_CHANCE = 0.04
WOLF_REPRODUCTION_CHANCE = 0.05
DEAD_TO_LIVE = 30 
MOVEMENT_MULTIPLIER = 1
INITIAL_WOLVES = 50
INITIAL_SHEEP = 100

# Constants for energy levels
GRASS_ENERGY_GAIN = 4
SHEEP_ENERGY_GAIN = 20
SHEEP_ENERGY_MIN = 0
SHEEP_ENERGY_MAX = GRASS_ENERGY_GAIN * 2
WOLF_ENERGY_MIN = 0
WOLF_ENERGY_MAX = SHEEP_ENERGY_GAIN * 2
ENERGY_LOSS_PER_TICK = 1

def update_graph(sheep_count, wolf_count, grass_count):
    grass_counts.append(grass_count)
    sheep_counts.append(sheep_count)
    wolf_counts.append(wolf_count)
    ax.clear()
    ax.plot(sheep_counts, label='Sheep')
    ax.plot(wolf_counts, label='Wolves')
    ax.plot(grass_counts, label ='Grass')
    ax.legend()
    plt.draw()
    plt.pause(0.001)  # Pause to ensure the plot updates


def draw_status_box(window, sheep_count, wolf_count, grass_count):
    # Define the status box properties
    box_width, box_height = 120, 90  # Adjust size as needed
    box_x, box_y = WIDTH - box_width - 10, 10  # 10 pixels from the top-right corner
    background_color = (255, 255, 255)  # White background
    text_color = (0, 0, 0)  # Black text

    # Draw the background box
    pygame.draw.rect(window, background_color, (box_x, box_y, box_width, box_height))

    # Prepare the text
    font = pygame.font.SysFont(None, 24)
    sheep_text = font.render(f"Sheep: {sheep_count}", True, text_color)
    wolf_text = font.render(f"Wolves: {wolf_count}", True, text_color)
    grass_text = font.render(f"Grass: {grass_count}", True, text_color)

    # Blit the text onto the window
    window.blit(sheep_text, (box_x + 5, box_y + 5))
    window.blit(wolf_text, (box_x + 5, box_y + 30))
    window.blit(grass_text, (box_x + 5, box_y + 55))

def reproduce_sheep(sheep_list):
    newborn_sheep = []
    for parent in sheep_list:
        if random.random() < SHEEP_REPRODUCTION_CHANCE:
            # Set the child's energy to half of the parent's
            child_energy = parent.energy // 2
            newborn_sheep.append(Sheep(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), child_energy))
            # Halve the parent's energy
            parent.energy = child_energy
    return newborn_sheep

def reproduce_wolves(wolf_list):
    newborn_wolves = []
    for parent in wolf_list:
        if random.random() < WOLF_REPRODUCTION_CHANCE:
            # Set the child's energy to half of the parent's
            child_energy = parent.energy // 2
            newborn_wolves.append(Wolf(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), child_energy))
            # Halve the parent's energy
            parent.energy = child_energy
    return newborn_wolves

def count_grass(grid):
    count = 0
    for row in grid:
        for cell in row:
            if cell.is_alive:
                count +=1
    return count//4

class Cell:
    def __init__(self, is_alive):
        self.is_alive = is_alive
        if(is_alive):
            self.tick_count = 0 
        else:
            self.tick_count = random.randint(0,DEAD_TO_LIVE-1)

    def update(self):
        if not self.is_alive:
            self.tick_count += 1
            if self.tick_count >= DEAD_TO_LIVE:
                self.is_alive = True
                self.tick_count = 0

class Animal:
    def __init__(self, x, y, energy):
        self.x = x
        self.y = y
        self.energy = energy

    def move_freely(self):
        angle = random.uniform(0, 2 * math.pi)
        self.x += math.cos(angle) * CELL_SIZE
        self.y += math.sin(angle) * CELL_SIZE

        # Wrap around the screen
        self.x = self.x % WIDTH
        self.y = self.y % HEIGHT
    
    def lose_energy(self):
        self.energy -= ENERGY_LOSS_PER_TICK

class Sheep(Animal):
    def __init__(self, x, y, energy=None):
        if energy is None:
            energy = random.randint(SHEEP_ENERGY_MIN, SHEEP_ENERGY_MAX)
        super().__init__(x, y, energy)

    def eat_grass(self):
        self.energy += GRASS_ENERGY_GAIN

    def move(self, grid):
        closest_dist = float('inf')
        target_x, target_y = None, None

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if grid[i][j].is_alive:
                    dx = (i * CELL_SIZE + CELL_SIZE // 2) - self.x
                    dy = (j * CELL_SIZE + CELL_SIZE // 2) - self.y

                    # Consider wrap-around distance
                    dx = min(dx, dx - WIDTH, dx + WIDTH, key=abs)
                    dy = min(dy, dy - HEIGHT, dy + HEIGHT, key=abs)

                    dist = math.sqrt(dx**2 + dy**2)
                    if dist < closest_dist:
                        closest_dist = dist
                        target_x = self.x + dx
                        target_y = self.y + dy

        if target_x is not None and target_y is not None:
            angle = math.atan2(target_y - self.y, target_x - self.x)
            self.x += (math.cos(angle) * CELL_SIZE) * MOVEMENT_MULTIPLIER
            self.y += (math.sin(angle) * CELL_SIZE) * MOVEMENT_MULTIPLIER

            # Wrap around the screen
            self.x = self.x % WIDTH
            self.y = self.y % HEIGHT

class Wolf(Animal):
    def __init__(self, x, y, energy=None):
        if energy is None:
            energy = random.randint(WOLF_ENERGY_MIN, WOLF_ENERGY_MAX)
        super().__init__(x, y, energy)
    
    def eat_sheep(self):
        self.energy += SHEEP_ENERGY_GAIN

    def move(self, sheep_list):
        closest_dist = float('inf')
        target_sheep = None

        for sheep in sheep_list:
            dx = sheep.x - self.x
            dy = sheep.y - self.y

            # Consider wrap-around distance
            dx = min(dx, dx - WIDTH, dx + WIDTH, key=abs)
            dy = min(dy, dy - HEIGHT, dy + HEIGHT, key=abs)

            dist = math.sqrt(dx**2 + dy**2)
            if dist < closest_dist:
                closest_dist = dist
                target_sheep = sheep

        if target_sheep is not None:
            dx = target_sheep.x - self.x
            dy = target_sheep.y - self.y

            # Consider wrap-around distance for movement
            dx = min(dx, dx - WIDTH, dx + WIDTH, key=abs)
            dy = min(dy, dy - HEIGHT, dy + HEIGHT, key=abs)

            angle = math.atan2(dy, dx)
            self.x += (math.cos(angle) * CELL_SIZE) * MOVEMENT_MULTIPLIER 
            self.y += (math.sin(angle) * CELL_SIZE) * MOVEMENT_MULTIPLIER

            # Wrap around the screen
            self.x = self.x % WIDTH
            self.y = self.y % HEIGHT

def draw_grid(window, grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            rect = pygame.Rect(i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = GREEN if grid[i][j].is_alive else BROWN
            pygame.draw.rect(window, color, rect)

def draw_animals(window, animals):
    font = pygame.font.SysFont(None, 15)  # You can choose another font and size

    for animal in animals:
        color = WHITE if isinstance(animal, Sheep) else (0, 0, 0)  # Wolves are black
        pygame.draw.circle(window, color, (int(animal.x), int(animal.y)), CELL_SIZE // 4)

        # Render the energy level and display it next to the animal
        energy_text = font.render(str(animal.energy), True, (255, 255, 255))
        window.blit(energy_text, (animal.x + CELL_SIZE // 2, animal.y - CELL_SIZE // 2))

        
def main():
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sheep, Wolves, and Grass Simulation")   

    # Initialize grid
    grid = [[Cell(random.choice([True, False])) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Initialize animals
    sheep = [Sheep(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(INITIAL_SHEEP)]
    wolves = [Wolf(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(INITIAL_WOLVES)]

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update grid for grass growth
        for row in grid:
            for cell in row:
                cell.update()

        # Move animals
        for s in sheep:
            s.move_freely()
            s.lose_energy()
            grid_x, grid_y = int(s.x // CELL_SIZE), int(s.y // CELL_SIZE)
            if grid[grid_x][grid_y].is_alive:
                grid[grid_x][grid_y].is_alive = False
                grid[grid_x][grid_y].tick_count = 0
                s.eat_grass()

        for w in wolves:
            w.move_freely()
            w.lose_energy()

    # Check for sheep-wolf collisions
        for w in wolves:
            # Find all sheep in the same cell as this wolf
            sheep_in_same_cell = [s for s in sheep if int(s.x // CELL_SIZE) == int(w.x // CELL_SIZE) and int(s.y // CELL_SIZE) == int(w.y // CELL_SIZE)]

            if sheep_in_same_cell:
                chosen_sheep = random.choice(sheep_in_same_cell)  # Randomly select one sheep
                w.eat_sheep()  # The wolf eats the sheep
                sheep.remove(chosen_sheep)  # Remove the eaten sheep from the list

        # Remove animals with no energy
        sheep = [s for s in sheep if s.energy >= 0]
        wolves = [w for w in wolves if w.energy >= 0]
            
        sheep += reproduce_sheep(sheep)
        wolves += reproduce_wolves(wolves)

        grass_count = count_grass(grid)

        update_graph(len(sheep), len(wolves), grass_count)

        # Update the screen
        window.fill((0, 0, 0))
        draw_grid(window, grid)
        draw_animals(window, sheep + wolves)
        #draw_status_box(window, len(sheep), len(wolves),grass_count)

        pygame.display.flip()
        clock.tick(150)

    pygame.quit()
    plt.ioff()  # Turn off interactive mode
    plt.show()  # Show the final plot before exiting

if __name__ == "__main__":
    main()