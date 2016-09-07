import os
import sys
from PIL import Image

def stitch_four(size, x, z, out_path, in_path):
    """
    x,z are tile coords of the nw small tile
    size is the width of a small tile
    """
    nw_path = in_path + '/%i,%i.png' % (x, z)
    sw_path = in_path + '/%i,%i.png' % (x, z+1)
    ne_path = in_path + '/%i,%i.png' % (x+1, z)
    se_path = in_path + '/%i,%i.png' % (x+1, z+1)

    out = Image.new('RGBA', (2*size, 2*size))

    if os.path.isfile(nw_path):
        out.paste(im=Image.open(nw_path), box=(0, 0))
    if os.path.isfile(sw_path):
        out.paste(im=Image.open(sw_path), box=(0, size))
    if os.path.isfile(ne_path):
        out.paste(im=Image.open(ne_path), box=(size, 0))
    if os.path.isfile(se_path):
        out.paste(im=Image.open(se_path), box=(size, size))

    out.save(out_path, 'PNG')

def stitch_all(out_path, in_path):
    os.makedirs(out_path, exist_ok=True)

    tiles = [tuple(map(int, region[:-4].split(',')))
             for region in os.listdir(in_path)
             if region[-4:] == '.png']

    size = Image.open(in_path + '/%i,%i.png' % tiles[0]).size[0]

    min_x = min(x for x,y in tiles) // 2
    min_z = min(z for x,z in tiles) // 2
    max_x = max(x for x,y in tiles) // 2
    max_z = max(z for x,z in tiles) // 2

    for x in range(min_x, max_x+1):
        for z in range(min_z, max_z+1):
            out_tile = out_path + '/%i,%i.png' % (x, z)
            stitch_four(size, 2*x, 2*z, out_tile, in_path)

def usage():
    print('Args: <large tiles out path> <small tiles in path>')
    sys.exit(1)

def main(args):
    try:
        out_path, in_path = args[1:3]
    except ValueError:
        usage()

    stitch_all(out_path, in_path)

if __name__ == '__main__':
    main(sys.argv)
