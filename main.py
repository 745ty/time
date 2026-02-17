import sys
import traceback
import pygame
from game import Game
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE

def main():
    try:
        # Initialize only what we need to avoid crashes with audio/joystick drivers on some Android devices
        try:
            pygame.display.init()
            pygame.font.init()
        except Exception as e:
            print(f"Init Error: {e}")

        # Explicitly do NOT initialize mixer to prevent crashes
        # pygame.mixer.init() 

        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        clock = pygame.time.Clock()
        
        game = Game(screen)
        
        while True:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                game.handle_input(event)
                
            # Update
            game.update()
            
            # Draw
            game.draw()
            
            pygame.display.flip()
            clock.tick(60)

    except Exception:
        # Crash Handler - Show error on screen
        error_msg = traceback.format_exc()
        try:
            if not pygame.display.get_init():
                pygame.display.init()
            if not pygame.font.get_init():
                pygame.font.init()
            
            screen = pygame.display.get_surface()
            if not screen:
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # Try to get a font
            try:
                font = pygame.font.SysFont("droid sans fallback", 20)
            except:
                font = pygame.font.Font(None, 20)
            
            screen.fill((50, 0, 0)) # Dark Red Screen of Death
            
            # Render error line by line
            y = 20
            # Split lines and limit length to fit screen roughly
            lines = error_msg.split('\n')
            for line in lines[-20:]: # Show last 20 lines (most relevant)
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (10, y))
                y += 22
            
            pygame.display.flip()
            
            # Wait loop
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                        waiting = False
        except:
            # If even the crash handler fails, just print
            print("CRITICAL CRASH AND HANDLER FAILED")
            print(error_msg)

if __name__ == "__main__":
    main()
