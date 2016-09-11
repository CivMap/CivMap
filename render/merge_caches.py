import os
import sys
from shutil import copy2, copystat
from zipfile import ZipFile

region_cols = 256*256

def merge_zips(zip_out, zip_top, zip_bottom, by_time=False):
    if by_time:
        time_top = os.path.getmtime(zip_top)
        time_bottom = os.path.getmtime(zip_bottom)
        if time_top < time_bottom:
            zip_top, zip_bottom = zip_bottom, zip_top
            print('bottom is newer', zip_out)

    file_top = ZipFile(zip_top).open('data')
    file_bottom = ZipFile(zip_bottom).open('data')
    data = bytearray(region_cols*17)
    memview = memoryview(data)

    for i in range(region_cols):
        col_top = file_top.read(17)
        col_bottom = file_bottom.read(17)
        if col_top == b'\0' * 17:
            col_top = col_bottom
        memview[i*17:(i+1)*17] = col_top

    zf = ZipFile(zip_out, 'w')
    zf.writestr('data', data)
    zf.close()
    copystat(zip_top, zip_out)

def merge_worlds(out_path, in_top, in_bottom, by_time=False):
    os.makedirs(out_path, exist_ok=True)
    for region in set(os.listdir(in_top)) \
               .union(os.listdir(in_bottom)):
        if region[-4:] != '.zip': continue
        region_out = out_path + '/' + region
        region_top = in_top + '/' + region
        region_bottom = in_bottom + '/' + region
        if not os.path.isfile(region_top):
            if os.path.isfile(region_bottom) \
            and region_bottom != region_out:
                copy2(region_bottom, region_out)
        elif not os.path.isfile(region_bottom):
            if os.path.isfile(region_top) \
            and region_top != region_out:
                copy2(region_top, region_out)
        else:
            merge_zips(region_out, region_top, region_bottom, by_time=by_time)

def usage():
    print('Args: <out path> <in path 1> <over|under|time> <in path 2>')
    sys.exit(1)

def main(args):
    try:
        out_path, in_top, combination, in_bottom = args[1:5]
    except ValueError:
        usage()

    if combination not in ('over', 'under', 'time'):
        print('ERROR unknown combination "%s"' % combination)
        print('must be "over", "under", or "time"')
        usage()

    if combination == 'under':
        in_top, in_bottom = in_bottom, in_top

    by_time = combination == 'time'

    if out_path[-4:] == '.zip':
        merge_zips(out_path, in_top, in_bottom, by_time=by_time)
    else:
        merge_worlds(out_path, in_top, in_bottom, by_time=by_time)

if __name__ == '__main__':
    main(sys.argv)
