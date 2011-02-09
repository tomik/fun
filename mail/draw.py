
import Image, ImageDraw
import random

ROUTES_FN = "routes.txt"
CENTER_SEP = " "
ROUTE_SEP = "->"
EDGE_SIZE = 20
IMG_SIZE = 640 
WORLD_SIZE = 32
UNIT = IMG_SIZE / float(WORLD_SIZE)

def _make_pt(city):
    pt = (int(city) % WORLD_SIZE, int(city) / WORLD_SIZE)
    pt = (EDGE_SIZE + pt[0] * UNIT, EDGE_SIZE + pt[1] * UNIT)
    return pt

def _draw_city(draw, pt, color, size=1):
    draw.rectangle((pt[0] - size, pt[1] - size, pt[0] + size, pt[1] + size), fill=color)

def _draw_road(draw, pt_from, pt_to, color, direct=False):
    if direct or pt_from[0] == pt_to[0] or pt_from[1] == pt_to[1]:
        draw.line((pt_from, pt_to), fill=color, width=0)
    else:
        draw.line((pt_from[0], pt_from[1], pt_from[0], pt_to[1]), fill=color, width=0)
        draw.line((pt_from[0], pt_to[1], pt_to[0], pt_to[1]), fill=color, width=0)

def draw_routes(): 

    im = Image.new("RGB", (IMG_SIZE + 2 * EDGE_SIZE, IMG_SIZE + 2 * EDGE_SIZE), "#FFFFFF")

    f = open(ROUTES_FN, "r")
    
    # draw centers
    points = map(_make_pt, f.readline().strip().split(CENTER_SEP))
    for pt in points:
        _draw_city(ImageDraw.Draw(im), pt, "black", size=5)


    line = f.readline()
    # draw routes
    while line:
        points = map(_make_pt, line.split(ROUTE_SEP))
        pt_from = points[0]
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw = ImageDraw.Draw(im)
        _draw_city(draw, pt_from, color)
        for pt_to in points[1:]:
            _draw_road(draw, pt_from, pt_to, color, True)
            _draw_city(draw, pt_to, color)
            pt_from = pt_to
        line = f.readline()

    # write to stdout
    im.save("world.png")

if __name__ == "__main__":
    draw_routes()

