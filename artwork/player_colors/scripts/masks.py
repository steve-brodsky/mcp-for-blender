"""Initial paint masks. Reviewed PNG masks are retained on rebuild."""
import numpy as np

def smooth(low, high, x):
    t = np.clip((x-low)/(high-low), 0, 1)
    return t*t*(3-2*t)


def classify(source, carrier=False, emission=None):
    h, w = source.shape[:2]
    hull = np.zeros((h, w), np.uint8)
    stripe = np.zeros((h, w), np.uint8)
    for start in range(0, h, 256):
        end = min(h, start+256)
        a = source[start:end, :, :3].astype(np.float32)/255
        r, g, b = np.moveaxis(a, -1, 0)
        value = a.max(axis=-1)
        sat = (value-a.min(axis=-1))/np.maximum(value, .001)
        # Warm ceramic/paint; neutral gray titanium and saturated hazards stay protected.
        warm = smooth(.006, .038, r-b) * (1-smooth(.44, .58, sat))
        warm *= smooth(.17, .36, value)
        warm *= (g >= b*.98) & (r >= g*.99) & (g >= r*.72)
        red = smooth(.045, .12, r-g) * smooth(.05, .14, r-b)
        red *= smooth(.12, .26, r) * (1-smooth(.53, .72, g/np.maximum(r, .001)))
        # Oxide red has green and blue close together. Amber safety paint does not.
        red *= (g-b < .17)
        warm *= (1-red)
        if carrier:
            yy = np.arange(start, end)[:, None]/h
            xx = np.arange(w)[None, :]/w
            warm = ((yy >= .75) & (xx < .5)).astype(np.float32)*np.ones_like(value)
            red = ((yy >= .5) & (yy < .75) & (xx < .25)).astype(np.float32)*np.ones_like(value)
        if emission is not None:
            protect = emission[start:end].max(axis=-1) > 8
            warm[protect] = 0; red[protect] = 0
        alpha = source[start:end, :, 3] > 0
        hull[start:end] = np.rint(warm*alpha*255).astype(np.uint8)
        stripe[start:end] = np.rint(red*alpha*255).astype(np.uint8)
    return hull, stripe


