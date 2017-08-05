import time
import pygame

margin = 0.05

class Display:
    def __init__(self, game, width = 1440, height = 900):
        self.game = game

        pygame.init()
        self.surface = pygame.display.set_mode((width, height))

        self.width = width
        self.height = height

        self.x0 = width * margin
        self.x1 = width * (1 - margin)
        self.y0 = height * margin
        self.y1 = height * (1 - margin)
        self.dx = self.x1 - self.x0
        self.dy = self.y1 - self.y0

        self.mine_color = pygame.Color(255, 0, 0) # red
        self.nonmine_color = pygame.Color(0, 0, 255) # blue

        self.unclaimed_color = pygame.Color(255, 255, 255) # white

        self.claimed_colors = [
            pygame.Color(255, 255, 0),
            pygame.Color(255, 0, 255),
            pygame.Color(0, 255, 255),
            pygame.Color(255, 0, 0),
            pygame.Color(0, 255, 0),
            pygame.Color(0, 0, 255)
            ]

    # Assuming node.x, node.y vary from 0 to 1
    def pos(self, node):
        return (int(self.x0 + self.dx * node.x), int(self.y0 + self.dy * node.y))

    def draw(self):
        self.surface.fill(pygame.Color(0, 0, 0))

        # Draw edges
        for edge in self.game.edges:
            if edge.owner == -1:
                color = self.unclaimed_color
            else:
                color = self.claimed_colors[edge.owner % len(self.claimed_colors)]
            pygame.draw.line(self.surface, color,
                    self.pos(self.game.nodes[edge.source]),
                    self.pos(self.game.nodes[edge.target]), 2)

        # Draw vertices
        for node in self.game.nodes.values():
            if node.ismine:
                color = self.mine_color
            else:
                color = self.nonmine_color
            pygame.draw.circle(self.surface, color, self.pos(node), 5)

        pygame.display.flip()

    def quit(self):
        pygame.display.quit()
        pygame.quit()

def display(game, timeout = 3):
    d = Display(game)
    d.draw()

    if timeout > 0:
        time.sleep(timeout)
    else:
        input("Press enter to close window.")

    d.quit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        import json
        import game_state as GS
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            j = json.load(f)

        message = {'punters' : 2, 'punter' : 0, 'map' : j}
        g = GS.Game.from_json_setup(message)
        g.layout_normalize()

        if True:
            g.layout_initial()
            g.layout_relax(1000)

        display(g, 5)
    else:
        print("Usage: python3 draw_game_state <path-to-map-file>")
