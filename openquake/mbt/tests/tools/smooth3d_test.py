import numpy as np
import unittest

from pyproj import Proj
from openquake.mbt.tools.smooth3d import Smoothing3D
from openquake.hazardlib.geo.mesh import Mesh
from openquake.hmtk.seismicity.catalogue import Catalogue

PLOTTING = False


class Smooth3DTestCase(unittest.TestCase):

    def setUp(self):
        self.spch = 2.5
        self.spcv = 2.5

        # Set the projection
        self.p = Proj(proj='lcc', lon_0=10.5, lat_2=45)

        # Find the grid limits
        xlo, ylo = tuple(t/1e3 for t in self.p(10.0, 45.0))
        xup, yup = tuple(t/1e3 for t in self.p(11.0, 46.0))

        # Creating a test mesh
        pnts = []
        dlt = 0.01
        for x in np.arange(xlo, xup+dlt, self.spch):
            for y in np.arange(ylo, yup+dlt, self.spch):
                for z in np.arange(0, 30+dlt, self.spcv):
                    pnts.append([x, y, z])
        pnts = np.array(pnts)
        plo, pla = self.p(pnts[:, 0]*1e3, pnts[:, 1]*1e3, inverse=True)
        pnts[:, 0] = plo
        pnts[:, 1] = pla
        self.mesh = Mesh(pnts[:, 0], pnts[:, 1], pnts[:, 2])

        # Create a catalogue
        keys = ['longitude', 'latitude', 'depth', 'year', 'magnitude']
        cata = np.array([[10.0, 45.0, 10.0, 2000, 5.0],
                         [10.5, 45.5, 10.0, 2000, 5.0],
                         [10.5, 45.6, 10.0, 2000, 5.0]])
        self.cat = Catalogue()
        self.cat.load_from_array(keys, cata)

        # Create a catalogue
        keys = ['longitude', 'latitude', 'depth', 'year', 'magnitude']
        cata = np.array([[10.5, 45.5, 10.0, 2000, 5.0]])
        self.cat1 = Catalogue()
        self.cat1.load_from_array(keys, cata)

    def testcase02(self):

        smooth = Smoothing3D(self.cat1, self.mesh, self.spch, self.spcv)
        values = smooth.gaussian(20, [5, 5, 5])

        if PLOTTING:
            vsc = 0.01
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D

            fig = plt.figure()
            iii = np.nonzero(values > 1e-15)[0]
            ax = fig.add_subplot(111, projection='3d')
            ax.plot(self.mesh.lons, self.mesh.lats, self.mesh.depths*vsc, 'ok',
                    alpha=0.2, ms=1.0)
            ax.plot(self.cat1.data['longitude'], self.cat1.data['latitude'],
                    self.cat1.data['depth']*vsc, 'or', alpha=0.7, ms=5.0)
            ax.scatter(self.mesh.lons[iii], self.mesh.lats[iii],
                       self.mesh.depths[iii]*vsc, c=values[iii],
                       alpha=0.5, s=4.0)
            ax.invert_zaxis()
            plt.show()

    def testcase01(self):
        smooth = Smoothing3D(self.cat, self.mesh, self.spch, self.spcv)
        values = smooth.gaussian(20, [5, 5, 2])

        if PLOTTING:
            vsc = 0.01
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            fig = plt.figure()
            iii = np.nonzero(values > 1e-15)[0]
            ax = fig.add_subplot(111, projection='3d')
            ax.plot(self.mesh.lons, self.mesh.lats, self.mesh.depths*vsc, 'ok',
                    alpha=0.2, ms=1.0)
            ax.plot(self.cat.data['longitude'], self.cat.data['latitude'],
                    self.cat.data['depth']*vsc, 'or', alpha=0.7, ms=5.0)
            ax.scatter(self.mesh.lons[iii], self.mesh.lats[iii],
                       self.mesh.depths[iii]*vsc, c=values[iii],
                       alpha=0.5, s=4.0)
            ax.invert_zaxis()
            plt.show()
