import RT_utility as rtu
import RT_camera as rtc
import RT_renderer as rtren
import RT_material as rtm
import RT_scene as rts
import RT_object as rto
import RT_integrator as rti
import RT_texture as rtt
import RT_light as rtl

def renderScene():
    main_camera = rtc.Camera()
    main_camera.aspect_ratio = 16.0 / 9.0
    main_camera.img_width = 960  # สำหรับ Test (ส่งงานจริงปรับเป็น 3840)
    main_camera.samples_per_pixel = 1024 # แนะนำ 1024 สำหรับ Final
    main_camera.max_depth = 5
    main_camera.vertical_fov = 45

    main_camera.look_from = rtu.Vec3(0, 2.5, 9)
    main_camera.look_at = rtu.Vec3(0, 1.5, 0)
    main_camera.vec_up = rtu.Vec3(0, 1, 0)
    main_camera.init_camera(0.0, 10.0)

    # ---------------- Texture ----------------
    tex_wood = rtt.ImageTexture("textures/wood.jpeg")
    mat_wood = rtm.TextureColor(tex_wood)

    tex_cement = rtt.ImageTexture("textures/cement.jpeg")
    mat_cement = rtm.TextureColor(tex_cement)

    tex_door = rtt.ImageTexture("textures/door.jpeg")
    mat_door = rtm.TextureColor(tex_door)

    mat_black_sphere = rtm.Metal(rtu.Color(0.02, 0.02, 0.02), 0.05)
    mat_ceiling_light = rtl.Diffuse_light(rtu.Color(25, 25, 20))
    mat_white = rtm.TextureColor(rtt.SolidColor(rtu.Color(0.3, 0.3, 0.3)))

    world = rts.Scene()

    # ---------------- Main Object ----------------
    #Floor
    world.add_object(rto.Quad(rtu.Vec3(-5, 0, 5), rtu.Vec3(10, 0, 0), rtu.Vec3(0, 0, -10), mat_wood))
    
    #Ceiling
    world.add_object(rto.Quad(rtu.Vec3(-5, 5, 5), rtu.Vec3(10, 0, 0), rtu.Vec3(0, 0, -10), mat_white))
    
    #Back Wall
    world.add_object(rto.Quad(rtu.Vec3(-5, 0, -5), rtu.Vec3(10, 0, 0), rtu.Vec3(0, 5, 0), mat_cement))
    
    #Left Wall
    world.add_object(rto.Quad(rtu.Vec3(-5, 0, 5), rtu.Vec3(0, 0, -10), rtu.Vec3(0, 5, 0), mat_cement))
    
    #Right Wall
    world.add_object(rto.Quad(rtu.Vec3(5, 0, 5), rtu.Vec3(0, 0, -10), rtu.Vec3(0, 5, 0), mat_cement))

    #Black Ball
    world.add_object(rto.Sphere(rtu.Vec3(0, 1.2, 0), 1.2, mat_black_sphere))

    #Ceiling Light
    world.add_object(rto.Sphere(rtu.Vec3(-1.5, 4.9, 0), 0.3, mat_ceiling_light))
    world.add_object(rto.Sphere(rtu.Vec3(1.5, 4.9, 0), 0.3, mat_ceiling_light)) 
    
    #DOOR จุดเริ่ม
    door_q = rtu.Vec3(-4.98, 0, -3.5) 
    # เวกเตอร์ U: ความกว้างของประตู กางออกมาทางแกน Z 
    door_u = rtu.Vec3(0, 0, 1.2)
    # เวกเตอร์ V: ความสูงของประตู กางขึ้นไปทางแกน Y 
    door_v = rtu.Vec3(0, 3.2, 0)
    world.add_object(rto.Quad(door_q, door_u, door_v, mat_door))

    # ---------------- Render ----------------
    intg = rti.Integrator(bSkyBG=False) 
    renderer = rtren.Renderer(main_camera, intg, world)

    renderer.render_parallel()
    renderer.write_img2png('Gantz Room 4k true.png')

if __name__ == "__main__":
    renderScene()