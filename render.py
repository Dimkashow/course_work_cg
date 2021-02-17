from object_3d import *
from camera import *
from projection import *
from interface import *


def inPolygon(x, y, xp, yp):
    c = 0
    for i in range(len(xp)):
        if (((yp[i] <= y < yp[i - 1]) or (yp[i - 1] <= y < yp[i])) and
                (x > (xp[i - 1] - xp[i]) * (y - yp[i]) / (yp[i - 1] - yp[i]) + xp[i])):
            c = 1 - c
    return c


class SoftwareRender:
    def __init__(self):
        pg.init()
        self.RES = self.WIDTH, self.HEIGHT = WIDTH_SCREEN, HEIGHT_SCREEN
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = FPS_MAX
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.create_objects()

        self.camera = Camera(self, CAMERA_STD_POS)
        self.camera.camera_yaw(CAMERA_STD_ANGLE)

        self.projection = Projection(self)
        self.grid = Grid(self)
        self.sup_grid = SupportGrid(self)
        self.world_axes = Axes(self)
        self.world_axes.movement_flag = False
        self.world_axes.scale(WORLD_AXES_SIZE)

        self.interface = Interface(self)

        self.cubes = []

        self.game_process = False
        self.game_matrix = []
        self.level_passed = False

    def load_level(self, pos):
        for cube in self.cubes:
            self.del_cube(cube.position)
        self.cubes = []
        self.level_passed = False
        f = open(str(pos[0]) + '.lvl', 'r')
        new_size = int(f.read(1))
        change_grid_size(new_size)
        self.game_process = True
        self.game_matrix = []

        for i in range(len(self.sup_grid.color_faces)):
            self.sup_grid.color_faces[i][2] = False

        for i in range(new_size * new_size * 3):
            self.game_matrix.append(int(f.read(1)))
        f.close()

        for i in range(len(self.sup_grid.color_faces)):
            if self.game_matrix[i]:
                self.sup_grid.color_faces[i][2] = NEED_COLOR
        self.check_level()

    def save_level(self, pos):
        self.level_passed = False
        self.game_process = False
        f = open(str(pos[0]) + '.lvl', 'w')
        f.write(str(GRID_SIZE))
        for face in self.sup_grid.color_faces:
            if face[2] == MARK_COLOR:
                f.write('1')
            else:
                f.write('0')
        f.close()

    def add_cube(self, pos):
        if pos[0] >= GRID_SIZE or pos[1] >= GRID_SIZE or pos[2] >= GRID_SIZE:
            return

        cube = Cube(self, pos)
        # cube.translate([pos[0], pos[1], pos[2]])
        self.cubes.append(cube)

        if not self.game_process:
            self.sup_grid.color_faces[pos[0] + pos[1] * GRID_SIZE][2] = MARK_COLOR
            self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE][2] = MARK_COLOR
            self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE][2] = MARK_COLOR
        else:
            if self.game_matrix[pos[0] + pos[1] * GRID_SIZE] == 1:
                self.sup_grid.color_faces[pos[0] + pos[1] * GRID_SIZE][2] = MARK_COLOR
            else:
                self.sup_grid.color_faces[pos[0] + pos[1] * GRID_SIZE][2] = BAD_COLOR

            if self.game_matrix[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE] == 1:
                self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE][2] = MARK_COLOR
            else:
                self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE][2] = BAD_COLOR

            if self.game_matrix[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE] == 1:
                self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE][2] = MARK_COLOR
            else:
                self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE][2] = BAD_COLOR

        self.check_level()

    def del_cube(self, pos):
        self.cubes = [self.cubes.pop(i) for i in reversed(range(len(self.cubes))) if
                      self.cubes[i].position[0] != pos[0] or
                      self.cubes[i].position[1] != pos[1] or
                      self.cubes[i].position[2] != pos[2]]

        if not self.game_process:
            # check XY
            self.sup_grid.color_faces[pos[0] + pos[1] * GRID_SIZE][2] = False
            for cube in self.cubes:
                if cube.position[0] == pos[0] and cube.position[1] == pos[1]:
                    self.sup_grid.color_faces[pos[0] + pos[1] * GRID_SIZE][2] = MARK_COLOR
                    break

            # check XZ
            self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE][2] = False
            for cube in self.cubes:
                if cube.position[0] == pos[0] and cube.position[2] == pos[2]:
                    self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE][2] = MARK_COLOR
                    break

            # check YZ
            self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE][2] = False
            for cube in self.cubes:
                if cube.position[1] == pos[1] and cube.position[2] == pos[2]:
                    self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE][2] = MARK_COLOR
                    break
        else:
            # check XY
            if self.game_matrix[pos[0] + pos[1] * GRID_SIZE] == 1:
                self.sup_grid.color_faces[pos[0] + pos[1] * GRID_SIZE][2] = NEED_COLOR
            else:
                self.sup_grid.color_faces[pos[0] + pos[1] * GRID_SIZE][2] = False
            for cube in self.cubes:
                if cube.position[0] == pos[0] and cube.position[1] == pos[1]:
                    if self.game_matrix[pos[0] + pos[1] * GRID_SIZE] == 1:
                        self.sup_grid.color_faces[pos[0] + pos[1] * GRID_SIZE][2] = MARK_COLOR
                    else:
                        self.sup_grid.color_faces[pos[0] + pos[1] * GRID_SIZE][2] = BAD_COLOR
                    break

            # check XZ
            if self.game_matrix[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE] == 1:
                self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE][2] = NEED_COLOR
            else:
                self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE][2] = False
            for cube in self.cubes:
                if cube.position[0] == pos[0] and cube.position[2] == pos[2]:
                    if self.game_matrix[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE] == 1:
                        self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE][2] = MARK_COLOR
                    else:
                        self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE + pos[0] + pos[2] * GRID_SIZE][2] = BAD_COLOR
                    break

            # check YZ
            if self.game_matrix[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE] == 1:
                self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE][2] = NEED_COLOR
            else:
                self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE][2] = False
            for cube in self.cubes:
                if cube.position[1] == pos[1] and cube.position[2] == pos[2]:
                    if self.game_matrix[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE] == 1:
                        self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE][
                            2] = MARK_COLOR
                    else:
                        self.sup_grid.color_faces[GRID_SIZE * GRID_SIZE * 2 + pos[1] + pos[2] * GRID_SIZE][
                            2] = BAD_COLOR
                    break

        self.check_level()

    def check_level(self):
        if not self.game_process:
            return

        for face in self.sup_grid.color_faces:
            if face[2] == BAD_COLOR or face[2] == NEED_COLOR:
                return
        self.level_passed = True

    def create_objects(self):
        pass
        # self.object = Object3D(self)
        # self.object.translate([0.0, 0.0, 0.0])

        # self.object2 = Object3D(self)
        # self.object2.translate([1, 0.0, 0.0])

        # self.object.rotate_y(math.pi / 6)
        # self.axes = Axes(self)
        # self.axes.translate([0.5, 0.5, 0.5])

        # xcsself.axes.translate([0.0001, 0.0001, 0.0001])

    def draw(self):
        self.screen.fill(pg.Color('darkslategray'))
        self.grid.draw()
        self.sup_grid.draw()
        self.world_axes.draw()

        lens_to_cube = []

        for i in range(len(self.cubes)):
            lens_to_cube.append((i, self.cubes[i].len_to_cube(self.camera.position)))

        lens_to_cube.sort(key=lambda j: -j[1])

        for i in lens_to_cube:
            self.cubes[i[0]].draw()

        self.interface.draw()
        # self.axes.draw()
        # self.object.draw()
        # self.object2.draw()

    def check_add_block(self, pos):
        pos_place = False
        polygons = self.grid.get_polygon()
        for index, color_face in enumerate(self.grid.color_faces):
            color, face, fill = color_face
            polygon = polygons[face]
            polygon = polygon[:, :2]

            xp = [polygon[0][0], polygon[1][0], polygon[2][0], polygon[3][0]]
            xy = [polygon[0][1], polygon[1][1], polygon[2][1], polygon[3][1]]

            if inPolygon(pos[0], pos[1], xp, xy):
                if index < GRID_SIZE * GRID_SIZE:
                    pos_place = [int(index % GRID_SIZE), int(index / GRID_SIZE), 0]
                elif index < GRID_SIZE * GRID_SIZE * 2:
                    index = index - GRID_SIZE * GRID_SIZE
                    pos_place = [int(index % GRID_SIZE), 0, int(index / GRID_SIZE)]
                else:
                    index = index - GRID_SIZE * GRID_SIZE * 2
                    pos_place = [0, int(index % GRID_SIZE), int(index / GRID_SIZE)]

        min_len = 9999

        for i in range(len(self.cubes)):
            polygons = self.cubes[i].get_polygon()
            for index, color_face in enumerate(self.cubes[i].color_faces):
                color, face, fill = color_face
                polygon = polygons[face]
                polygon = polygon[:, :2]

                xp = [polygon[0][0], polygon[1][0], polygon[2][0], polygon[3][0]]
                xy = [polygon[0][1], polygon[1][1], polygon[2][1], polygon[3][1]]

                if inPolygon(pos[0], pos[1], xp, xy):
                    len_to_obj = self.cubes[i].len_to_faces(index, self.camera.position)
                    if len_to_obj < min_len:
                        min_len = len_to_obj
                        pos_place = [self.cubes[i].position[0] + tap_to_cube[index][0],
                                     self.cubes[i].position[1] + tap_to_cube[index][1],
                                     self.cubes[i].position[2] + tap_to_cube[index][2]]
        if pos_place:
            self.add_cube(pos_place)

    def check_del_block(self, pos):
        pos_place = False
        min_len = 9999

        for i in range(len(self.cubes)):
            polygons = self.cubes[i].get_polygon()
            for index, color_face in enumerate(self.cubes[i].color_faces):
                color, face, fill = color_face
                polygon = polygons[face]
                polygon = polygon[:, :2]

                xp = [polygon[0][0], polygon[1][0], polygon[2][0], polygon[3][0]]
                xy = [polygon[0][1], polygon[1][1], polygon[2][1], polygon[3][1]]

                if inPolygon(pos[0], pos[1], xp, xy):
                    len_to_obj = self.cubes[i].len_to_faces(index, self.camera.position)
                    if len_to_obj < min_len:
                        min_len = len_to_obj
                        pos_place = [self.cubes[i].position[0],
                                     self.cubes[i].position[1],
                                     self.cubes[i].position[2]]
        if pos_place:
            self.del_cube(pos_place)

    def run(self):
        while True:
            self.draw()
            self.camera.control()
            self.interface.control()
            # [exit() for i in pg.event.get() if i.type == pg.QUIT]
            pg.display.set_caption(str(self.clock.get_fps()))
            pg.display.flip()
            self.clock.tick(self.FPS)
            # print(self.camera.position)
