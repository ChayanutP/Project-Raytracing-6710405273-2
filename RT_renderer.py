# renderer class

import RT_utility as rtu
import numpy as np
from PIL import Image as im
import math
import multiprocessing as mp
import time
from tqdm import tqdm

class Renderer():

    def __init__(self, cCamera, iIntegrator, sScene) -> None:
        self.camera = cCamera
        self.integrator = iIntegrator
        self.scene = sScene
        pass

    def render(self):
        # gather lights to the light list
        self.scene.find_lights()
        # renderbar = RT_pbar.start_animated_marker(self.camera.img_height*self.camera.img_width)
        k = 0
                
        for j in range(self.camera.img_height):
            for i in range(self.camera.img_width):

                pixel_color = rtu.Color(0,0,0)
                # shoot multiple rays at random locations inside the pixel
                for spp in range(self.camera.samples_per_pixel):
                    generated_ray = self.camera.get_ray(i, j)
                    pixel_color = pixel_color + self.integrator.compute_scattering(generated_ray, self.scene, self.camera.max_depth)

                self.camera.write_to_film(i, j, pixel_color)
                # renderbar.update(k)
                k = k+1

    def render_jittered(self):
        # gather lights to the light list
        self.scene.find_lights()
        # renderbar = RT_pbar.start_animated_marker(self.camera.img_height*self.camera.img_width)
        k = 0
        sqrt_spp = int(math.sqrt(self.camera.samples_per_pixel))
                
        for j in range(self.camera.img_height):
            for i in range(self.camera.img_width):

                pixel_color = rtu.Color(0,0,0)
                # shoot multiple rays at random locations inside the pixel
                for s_j in range(sqrt_spp):
                    for s_i in range(sqrt_spp):

                        generated_ray = self.camera.get_jittered_ray(i, j, s_i, s_j)
                        pixel_color = pixel_color + self.integrator.compute_scattering(generated_ray, self.scene, self.camera.max_depth)

                self.camera.write_to_film(i, j, pixel_color)
                # renderbar.update(k)
                k = k+1
        

    def write_img2png(self, strPng_filename):
        png_film = self.camera.film * 255
        data = im.fromarray(png_film.astype(np.uint8))
        data.save(strPng_filename)

    # compute the final color of a single pixel by averaging multiple ray samples
    def render_pixel(self, i, j):
        pixel_color = rtu.Color(0,0,0)

        for spp in range(self.camera.samples_per_pixel):
            generated_ray = self.camera.get_ray(i, j)
            pixel_color = pixel_color + self.integrator.compute_scattering(
                generated_ray, self.scene, self.camera.max_depth
            )

        return pixel_color
    
    # render the entire image in parallel by distributing rows across multiple CPU processes
    def render_parallel(self):
        print(f"Start rendering with {mp.cpu_count()} cores...")
        self.scene.find_lights()
        start = time.time()

        height = self.camera.img_height
        width = self.camera.img_width

        # เตรียมข้อมูลงาน
        tasks = [(y, self.camera, self.integrator, self.scene) for y in range(height)]

        # ใช้ Pool ร่วมกับ tqdm เพื่อแสดง ETA
        with mp.Pool(mp.cpu_count()) as pool:
            # imap_unordered เพื่อช่วยให้ tqdm อัปเดตเรียลไทม์เมื่อมีงานใดงานหนึ่งเสร็จ
            results = list(tqdm(
                pool.imap_unordered(render_row, tasks), 
                total=height, 
                desc="Rendering", 
                unit="row"
            ))

        # เนื่องจากใช้ unordered ผลลัพธ์อาจสลับบรรทัดกัน ต้อง sort ก่อนเขียนลง film
        results.sort(key=lambda x: x[0])

        for y, row in results:
            for x in range(width):
                self.camera.write_to_film(x, y, row[x])

        end = time.time()
        print(f"\nRendering Complete ^ ^ Time used: {end - start:.2f} seconds")
        
# compute all pixel colors for a single row (y) using ray tracing and return the result
def render_row(args):
    y, camera, integrator, scene = args

    row = []
    for x in range(camera.img_width):
        pixel_color = rtu.Color(0,0,0)

        for spp in range(camera.samples_per_pixel):
            ray = camera.get_ray(x, y)
            pixel_color = pixel_color + integrator.compute_scattering(
                ray, scene, camera.max_depth
            )

        row.append(pixel_color)

    return (y, row)