import time
import pygame

margin = 0.05

class Display:
    def __init__(self, board, width = 1440, height = 900):
        self.board = board

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

    # Assuming x, y vary from 0 to 1
    def pos(self, xy):
        return (int(self.x0 + self.dx * xy[0]), int(self.y0 + self.dy * xy[1]))

    def draw(self):
        self.surface.fill(pygame.Color(0, 0, 0))

        # Draw edges
        for i in range(self.board.n):
            for j in self.board.edges[i]:
                color = self.unclaimed_color
                pygame.draw.line(self.surface, color,
                        self.pos(self.board.xy[i]),
                        self.pos(self.board.xy[j]), 2)

        # Draw vertices
        for i in range(self.board.n):
            if self.board.ismine[i]:
                color = self.mine_color
            else:
                color = self.nonmine_color
            pygame.draw.circle(self.surface, color, self.pos(self.board.xy[i]), 5)

        pygame.display.flip()

    def quit(self):
        pygame.display.quit()
        pygame.quit()

def display(board, timeout = 3):
    d = Display(board)
    d.draw()

    if timeout > 0:
        time.sleep(timeout)
    else:
        input("Press enter to close window.")

    d.quit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        import board
        b = board.Board.from_json_file(sys.argv[1])
        b.layout_normalize()

        if True:
            b.layout_initial()
            b.layout_relax(1000)

        display(b, 5)
    else:
        print("Usage: python3 draw_board <path-to-map-file>")
