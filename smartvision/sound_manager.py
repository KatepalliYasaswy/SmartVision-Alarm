from pathlib import Path
import pygame


class SoundManager:
    def __init__(self, sound_path: str):
        self.sound_path = str(sound_path)
        self.ready = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(self.sound_path)
            self.ready = True
        except Exception as exc:
            print(f"Could not initialize alarm audio: {exc}")

    def play_loop(self):
        if self.ready:
            try:
                pygame.mixer.music.load(self.sound_path)
                pygame.mixer.music.play(-1)
            except Exception as exc:
                print(f"Could not play alarm audio: {exc}")

    def stop(self):
        if self.ready:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
