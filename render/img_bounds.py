def img_bounds_from_matching(img_size, match1, match2):
    (width, height) = img_size
    (x1, z1), (u1, v1) = match1
    (x2, z2), (u2, v2) = match2
    x_scale = (x1 - x2) / (u1 - u2)
    z_scale = (z1 - z2) / (v1 - v2)
    print('scale:', x_scale, z_scale)
    n = z1 - v1 * z_scale
    w = x1 - u1 * x_scale
    s = z1 - (v1 - height) * z_scale
    e = x1 - (u1 - width) * x_scale
    return round(n), round(w), round(s), round(e)

if __name__ == '__main__':
    print(img_bounds_from_matching((10,20),
        ((0,0), (0,0)),
        ((10,20), (10,20))))
    print((0, 0, 20, 10))
    print()
    print(img_bounds_from_matching((20,20),
        ((-20,-10), (0,0)),
        ((40,30), (20,20))))
    print((-10, -20, 30, 40))
