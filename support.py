import pygame
def import_sprite_sheet(path,frame_width,frame_height,scale=2):
    sheet=pygame.image.load(path).convert_alpha()
    sheet_width,sheet_height=sheet.get_size()
    frames = []
    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            if x + frame_width <= sheet_width and y + frame_height <= sheet_height:
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                if scale != 1:
                    new_width = int(frame_width * scale)
                    new_height = int(frame_height * scale)
                    frame = pygame.transform.scale(frame, (new_width, new_height))
                frames.append(frame)
    return frames  
    