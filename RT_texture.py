# Texture class
import math
import random
from PIL import Image as im
import RT_utility as rtu
import numpy as np

class Texture:
    def __init__(self) -> None:
        pass

    def tex_value(self, fu, fv, vPoint):
        pass

# solid color as a texture
class SolidColor(Texture):
    def __init__(self, cColor) -> None:
        super().__init__()
        self.solid_color = cColor

    def value(self, u, v, p):
        return self.tex_value(u, v, p)

    def tex_value(self, fu, fv, vPoint):
        return self.solid_color

def stripe(u, v):
    if int(u * 10) % 2 == 0:
        return rtu.Color(1,1,1)
    return rtu.Color(0,0,0)

# checker board as a texture    
class CheckerTexture(Texture):
    def __init__(self, fScale, cColor1, cColor2) -> None:
        super().__init__()
        self.inv_scale = 1.0/fScale
        self.even_texture = SolidColor(cColor1)
        self.odd_texture = SolidColor(cColor2)

    def value(self, u, v, p):
        return self.tex_value(u, v, p)

    def tex_value(self, fu, fv, vPoint):

        xInteger = int(math.floor(vPoint.x()*self.inv_scale))
        yInteger = int(math.floor(vPoint.y()*self.inv_scale))
        zInteger = int(math.floor(vPoint.z()*self.inv_scale))

        isEven = (xInteger + yInteger + zInteger) % 2 == 0

        if isEven:
            return self.even_texture.tex_value(fu, fv, vPoint)
        
        return self.odd_texture.tex_value(fu, fv, vPoint)
    
# an PNG,JPG image as a texture
class ImageTexture(Texture):
    def __init__(self, strImgFilename) -> None:
        super().__init__()
        self.invalid = False
        try:
            # แก้จาก opem เป็น open
            temp_img = im.open(strImgFilename).convert("RGB")
            self.width, self.height = temp_img.size
            
            # เก็บเป็น numpy array ไว้ใน RAM (เร็วกว่า getpixel)
            self.data = np.asarray(temp_img)
            temp_img.close()
            print(f'Texture loaded and stored in RAM: {strImgFilename}')
        except Exception as e:
            print(f'The texture file could not be loaded: {strImgFilename}\nError: {e}')
            self.invalid = True

    def value(self, u, v, p):
        return self.tex_value(u, v, p)

    def tex_value(self, fu, fv, vPoint):
        if self.invalid:
            return rtu.Color(0, 1, 1) # สี Cyan สำหรับ Debug
        
        # clamping values to (0,1)
        u = max(0.0, min(fu, 1.0))
        v = 1.0 - max(0.0, min(fv, 1.0)) 

        i = int(u * (self.width - 1))
        j = int(v * (self.height - 1))

        pixel = self.data[j, i]

        scale = 1.0 / 255.0
        return rtu.Color(pixel[0] * scale, pixel[1] * scale, pixel[2] * scale)
    
class Noise:
    def __init__(self):
        self.randvec = [rtu.Vec3.random(-1,1) for _ in range(256)]
        self.perm = list(range(256))
        random.shuffle(self.perm)

    def noise(self, p):
        i = int(math.floor(p.x())) & 255
        j = int(math.floor(p.y())) & 255
        k = int(math.floor(p.z())) & 255

        return rtu.Vec3.dot_product(
            self.randvec[self.perm[i] ^ self.perm[j] ^ self.perm[k]],
            p
        )

    def turbulence(self, p, depth=7):
        accum = 0.0
        weight = 1.0
        temp_p = p

        for i in range(depth):
            accum += weight * self.noise(temp_p)
            weight *= 0.5
            temp_p = temp_p * 2

        return abs(accum)
