# media.py
import os
import random

class MediaLibrary:
    IMAGE_EXT = {"jpg", "jpeg", "png", "bmp", "gif"}
    AUDIO_EXT = {"mp3", "wav", "ogg"}
    VIDEO_EXT = {"mp4", "avi", "mkv", "mov"}

    def __init__(self, config):
        self.config = config
        self.pool = {"image": [], "audio": [], "video": []}
        self.rescan()

    def rescan(self):
        self.pool = {"image": [], "audio": [], "video": []}

        for folder in self.config["media_folders"]:
            for root, _, files in os.walk(folder):
                for f in files:
                    ext = f.lower().split(".")[-1]
                    full = os.path.join(root, f)

                    if ext in self.IMAGE_EXT:
                        self.pool["image"].append(full)
                    elif ext in self.AUDIO_EXT:
                        self.pool["audio"].append(full)
                    elif ext in self.VIDEO_EXT:
                        self.pool["video"].append(full)

    def choose(self, allowed):
        """
        allowed: list[str] e.g. ["image", "audio"]
        returns: (path, type) or (None, None)
        """
        types = [t for t in allowed if self.pool[t] and self.config["media"][t]["enabled"]]
        # types = [t for t in allowed if self.pool[t]]
        if not types:
            return None, None

        weights = [self.config["media"][t]["weight"] for t in types]
        # weights = [self.config["media_weights"][t] for t in types]
        chosen_type = random.choices(types, weights=weights, k=1)[0]
        return random.choice(self.pool[chosen_type]), chosen_type
