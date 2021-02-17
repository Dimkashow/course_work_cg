from matrix_functions import *
from numba import njit
from settings import *


@njit(fastmath=True)
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))


@njit(fastmath=True)
def len_to_point(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x1 - x2) * (x1 - x2) +
                     (y1 - y2) * (y1 - y2) +
                     (z1 - z2) * (z1 - z2))


class Object3D:
    def __init__(self, render):
        self.render = render
        self.vertexes = np.array([(0, 0, 0, 1),
                                  (0, 1, 0, 1),
                                  (1, 1, 0, 1),
                                  (1, 0, 0, 1),
                                  (0, 0, 1, 1),
                                  (0, 1, 1, 1),
                                  (1, 1, 1, 1),
                                  (1, 0, 1, 1)])

        self.faces = np.array([(0, 1, 2, 3),
                               (4, 5, 6, 7),
                               (0, 4, 5, 1),
                               (2, 3, 7, 6),
                               (1, 2, 6, 5),
                               (0, 3, 7, 4)])

        self.font = pg.font.SysFont('Arial', 30, bold=True)
        self.color_faces = [(pg.Color('orange'), face, False) for face in self.faces]
        self.movement_flag, self.draw_vertexes = False, True
        self.label = ''
        self.draw_3d = False

    def get_polygon(self):
        vertexes = self.vertexes @ self.render.camera.camera_matrix()
        vertexes = vertexes @ self.render.projection.projection_matrix
        vertexes /= vertexes[:, -1].reshape(-1, 1)
        vertexes[(vertexes > 2) | (vertexes < -2)] = 0
        vertexes = vertexes @ self.render.projection.to_screen_matrix
        # vertexes = vertexes[:, :3]
        return vertexes

    def draw(self):
        self.screen_projection()
        self.movement()

    def movement(self):
        if self.movement_flag:
            self.rotate_y(pg.time.get_ticks() % 0.005)

    def screen_projection(self):
        vertexes = self.vertexes @ self.render.camera.camera_matrix()
        vertexes = vertexes @ self.render.projection.projection_matrix
        vertexes /= vertexes[:, -1].reshape(-1, 1)
        vertexes[(vertexes > 2) | (vertexes < -2)] = 0
        vertexes = vertexes @ self.render.projection.to_screen_matrix

        vertexes = vertexes[:, :2]

        polygons_3d = []

        for index, color_face in enumerate(self.color_faces):
            color, face, fill = color_face
            polygon = vertexes[face]
            if not any_func(polygon, self.render.H_WIDTH, self.render.H_HEIGHT):
                if self.draw_3d:
                    polygons_3d.append((polygon, self.len_to_faces(index, self.render.camera.position)))
                    polygons_3d.sort(key=lambda j: -j[1])

                elif fill:
                    pg.draw.polygon(self.render.screen, fill, polygon)
                    pg.draw.polygon(self.render.screen, color, polygon, 1)
                else:
                    pg.draw.polygon(self.render.screen, color, polygon, 1)

                if self.label:
                    text = self.font.render(self.label[index], True, pg.Color('white'))
                    self.render.screen.blit(text, polygon[-1])

            if self.draw_3d:
                for i in polygons_3d:
                    pg.draw.polygon(self.render.screen, pg.Color('orange'), i[0])
                    pg.draw.polygon(self.render.screen, pg.Color('black'), i[0], 1)

        if self.draw_vertexes:
            for vertex in vertexes:
                if not any_func(vertex, self.render.H_WIDTH, self.render.H_HEIGHT):
                    pg.draw.circle(self.render.screen, pg.Color('white'), vertex, 6)

    def translate(self, pos):
        self.vertexes = self.vertexes @ translate(pos)

    def scale(self, scale_to):
        self.vertexes = self.vertexes @ scale(scale_to)

    def rotate_x(self, angle):
        self.vertexes = self.vertexes @ rotate_x(angle)

    def rotate_y(self, angle):
        self.vertexes = self.vertexes @ rotate_y(angle)

    def rotate_z(self, angle):
        self.vertexes = self.vertexes @ rotate_z(angle)


class Axes(Object3D):
    def __init__(self, render):
        super().__init__(render)
        self.vertexes = np.array([(0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
        self.faces = np.array([(0, 1), (0, 2), (0, 3)])
        self.colors = [pg.Color('red'), pg.Color('green'), pg.Color('blue')]
        self.color_faces = [(color, face, False) for color, face in zip(self.colors, self.faces)]
        self.draw_vertexes = False
        self.label = 'XYZ'


class Grid(Object3D):
    def __init__(self, render):
        super().__init__(render)
        grid_arr = np.empty((0, 4), int)
        faces_arr = np.empty((0, 4), int)

        # XY Grid
        for i in range(GRID_SIZE + 1):
            for j in range(GRID_SIZE + 1):
                grid_arr = np.append(grid_arr, np.array([[i, j, 0, 1]]), axis=0)

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                faces_arr = np.append(faces_arr, np.array([[i + j * (GRID_SIZE + 1),
                                                            i + j * (GRID_SIZE + 1) + 1,
                                                            i + (j + 1) * (GRID_SIZE + 1) + 1,
                                                            i + (j + 1) * (GRID_SIZE + 1)]]), axis=0)

        # XZ Grid
        for i in range(GRID_SIZE + 1):
            for j in range(GRID_SIZE + 1):
                grid_arr = np.append(grid_arr, np.array([[i, 0, j, 1]]), axis=0)

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                faces_arr = np.append(faces_arr, np.array([[(GRID_SIZE + 1) * (GRID_SIZE + 1) + i + j * (GRID_SIZE + 1),
                                                            (GRID_SIZE + 1) * (GRID_SIZE + 1) + i + j * (
                                                                        GRID_SIZE + 1) + 1,
                                                            (GRID_SIZE + 1) * (GRID_SIZE + 1) + i + (j + 1) * (
                                                                        GRID_SIZE + 1) + 1,
                                                            (GRID_SIZE + 1) * (GRID_SIZE + 1) + i + (j + 1) * (
                                                                        GRID_SIZE + 1)]]), axis=0)

        # YZ Grid
        for i in range(GRID_SIZE + 1):
            for j in range(GRID_SIZE + 1):
                grid_arr = np.append(grid_arr, np.array([[0, i, j, 1]]), axis=0)

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                faces_arr = np.append(faces_arr,
                                      np.array([[(GRID_SIZE + 1) * (GRID_SIZE + 1) * 2 + i + j * (GRID_SIZE + 1),
                                                 (GRID_SIZE + 1) * (GRID_SIZE + 1) * 2 + i + j * (GRID_SIZE + 1) + 1,
                                                 (GRID_SIZE + 1) * (GRID_SIZE + 1) * 2 + i + (j + 1) * (
                                                             GRID_SIZE + 1) + 1,
                                                 (GRID_SIZE + 1) * (GRID_SIZE + 1) * 2 + i + (j + 1) * (
                                                             GRID_SIZE + 1)]]), axis=0)

        self.vertexes = grid_arr
        self.faces = faces_arr
        self.color_faces = [(pg.Color('grey'), face, False) for face in self.faces]
        self.draw_vertexes = False
        self.label = ''


class SupportGrid(Object3D):
    def __init__(self, render):
        super().__init__(render)

        grid_arr = np.empty((0, 4), int)
        faces_arr = np.empty((0, 4), int)

        # XY Grid
        for i in range(GRID_SIZE + 1):
            for j in range(GRID_SIZE + 1):
                grid_arr = np.append(grid_arr, np.array([[i, j, -SUP_GRID_XY_FAR, 1]]), axis=0)

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                faces_arr = np.append(faces_arr, np.array([[i + j * (GRID_SIZE + 1),
                                                            i + j * (GRID_SIZE + 1) + 1,
                                                            i + (j + 1) * (GRID_SIZE + 1) + 1,
                                                            i + (j + 1) * (GRID_SIZE + 1)]]), axis=0)

        # XZ Grid
        for i in range(GRID_SIZE + 1):
            for j in range(GRID_SIZE + 1):
                grid_arr = np.append(grid_arr, np.array([[i, -SUP_GRID_XZ_FAR, j, 1]]), axis=0)

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                faces_arr = np.append(faces_arr, np.array([[(GRID_SIZE + 1) * (GRID_SIZE + 1) + i + j * (GRID_SIZE + 1),
                                                            (GRID_SIZE + 1) * (GRID_SIZE + 1) + i + j * (
                                                                        GRID_SIZE + 1) + 1,
                                                            (GRID_SIZE + 1) * (GRID_SIZE + 1) + i + (j + 1) * (
                                                                        GRID_SIZE + 1) + 1,
                                                            (GRID_SIZE + 1) * (GRID_SIZE + 1) + i + (j + 1) * (
                                                                        GRID_SIZE + 1)]]), axis=0)

        # YZ Grid
        for i in range(GRID_SIZE + 1):
            for j in range(GRID_SIZE + 1):
                grid_arr = np.append(grid_arr, np.array([[-SUP_GRID_YZ_FAR, i, j, 1]]), axis=0)

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                faces_arr = np.append(faces_arr,
                                      np.array([[(GRID_SIZE + 1) * (GRID_SIZE + 1) * 2 + i + j * (GRID_SIZE + 1),
                                                 (GRID_SIZE + 1) * (GRID_SIZE + 1) * 2 + i + j * (GRID_SIZE + 1) + 1,
                                                 (GRID_SIZE + 1) * (GRID_SIZE + 1) * 2 + i + (j + 1) * (
                                                             GRID_SIZE + 1) + 1,
                                                 (GRID_SIZE + 1) * (GRID_SIZE + 1) * 2 + i + (j + 1) * (
                                                             GRID_SIZE + 1)]]), axis=0)

        self.vertexes = grid_arr
        self.faces = faces_arr
        self.color_faces = [[pg.Color('grey'), face, False] for face in self.faces]
        self.draw_vertexes = False
        self.label = ''


class Cube(Object3D):
    def __init__(self, render, pos):
        super().__init__(render)
        self.position = pos
        self.translate(pos)
        self.draw_3d = True
        self.draw_vertexes = False

    def len_to_faces(self, index, camera_pos):
        x_new = (self.vertexes[self.faces[index][0]][0] + self.vertexes[self.faces[index][3]][0]) / 2
        y_new = (self.vertexes[self.faces[index][0]][1] + self.vertexes[self.faces[index][3]][1]) / 2
        z_new = (self.vertexes[self.faces[index][0]][2] + self.vertexes[self.faces[index][3]][2]) / 2

        return len_to_point(camera_pos[0], camera_pos[1], camera_pos[2], x_new, y_new, z_new)

    def len_to_cube(self, camera_pos):
        return len_to_point(camera_pos[0], camera_pos[1], camera_pos[2],
                            self.position[0], self.position[1], self.position[2])


'''
        grid_arr = np.empty((0, 4), int)
        # XY Grid
        for i in range(GRID_SIZE + 1):
            grid_arr = np.append(grid_arr, np.array([[i, 0, -SUP_GRID_XY_FAR, 1]]), axis=0)
            grid_arr = np.append(grid_arr, np.array([[i, GRID_SIZE, -SUP_GRID_XY_FAR, 1]]), axis=0)

        for i in range(GRID_SIZE + 1):
            grid_arr = np.append(grid_arr, np.array([[0, i, -SUP_GRID_XY_FAR, 1]]), axis=0)
            grid_arr = np.append(grid_arr, np.array([[GRID_SIZE, i, -SUP_GRID_XY_FAR, 1]]), axis=0)

        # XZ Grid
        for i in range(GRID_SIZE + 1):
            grid_arr = np.append(grid_arr, np.array([[i, -SUP_GRID_XZ_FAR, 0, 1]]), axis=0)
            grid_arr = np.append(grid_arr, np.array([[i, -SUP_GRID_XZ_FAR, GRID_SIZE, 1]]), axis=0)

        for i in range(GRID_SIZE + 1):
            grid_arr = np.append(grid_arr, np.array([[0, -SUP_GRID_XZ_FAR, i, 1]]), axis=0)
            grid_arr = np.append(grid_arr, np.array([[GRID_SIZE, -SUP_GRID_XZ_FAR, i, 1]]), axis=0)

        # YZ Grid
        for i in range(GRID_SIZE + 1):
            grid_arr = np.append(grid_arr, np.array([[-SUP_GRID_YZ_FAR, i, 0, 1]]), axis=0)
            grid_arr = np.append(grid_arr, np.array([[-SUP_GRID_YZ_FAR, i, GRID_SIZE, 1]]), axis=0)

        for i in range(GRID_SIZE + 1):
            grid_arr = np.append(grid_arr, np.array([[-SUP_GRID_YZ_FAR, 0, i, 1]]), axis=0)
            grid_arr = np.append(grid_arr, np.array([[-SUP_GRID_YZ_FAR, GRID_SIZE, i, 1]]), axis=0)

        faces_arr = np.empty((0, 2), int)
        for i in range((GRID_SIZE + 1) * 6):
            faces_arr = np.append(faces_arr, np.array([[i * 2, i * 2 + 1]]), axis=0)
'''
