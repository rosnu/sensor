import numpy as np
from scipy.interpolate import LinearNDInterpolator
from scipy.spatial import Delaunay
import math

from scipy.interpolate import SmoothBivariateSpline

from sensor_data import sensors, aqs5, aqs6
# aqs5 = {
#     'params': {'r0':4.7, 'rout':320, 'dt':1 / 80e6 * 7, 'du':3.3 / 1024},
#     'cal': [
#                 [2.2, 20, 213.5, 298.0],
#                 # [2.2,   100,    142.6,  297.7],
#                 [10, 20, 396.9, 677.7],
#                 [10, 100, 302.8, 677.3],
#                 [1, 156, 71.6, 155.8],
#                 [1, 220, 67.0 , 156.7],
#
#                # [4.7, 220, 209.1 ,  488.1],
#                #  [10e6, 1, 845.1 ,  1019.7],
#                #  [10,1,543.7 ,  678.3],
#                #  [10,56, 326.7 ,  678.8 ],
#                #  [2.2,56,162.6 ,  297.2],
#                #  [10e6,20,545.0 ,  1018.5],
#                #  [10e6,56,470.7 ,  1017.8],
#                #  [10e6,100,448.6 ,  1018.2],
#              ]
# }
#
# # aqs6 before 2025-12-21
# # aqs6 = {
# #     'params': {'r0':2.2, 'rout':470, 'dt':1 / 160e6 * 12, 'du':1e-3},
# #     'cal':[  # calibration pts
# #     [1.0, 1    , 862.1  , 891.3 ],  # semi no one
# #     # [1.0, 100,  774.8 ,   893.8],
# #     [1.0, 220, 627.5 , 899.9],
# #     # [2.2, 1    , 1446.4 ,  1487.7],
# #     # [2.2, 220,  948.6 ,  1489.4],
# #     # [4.7, 1    , 2045.8 ,  2101.9],
# #     [4.7, 100    , 1528.2 , 2068.1],
# #     [4.7, 220, 1229.4 , 2068.0],
# #     [10.0, 1 , 2449.8 , 2519.3],
# #     [10.0, 47, 2086.3 , 2522.5],
# #     # [1e7, 1, 3042.5 ,  3109.9],
# #     # [],
# # ]
# #     }
#
#
# #aqs6 2025-12-21
# aqs6 = {
#     'params': {'r0':2.2, 'rout':470, 'dt':1 / 160e6 * 12, 'du':1e-3},
#     'cal':[  # calibration pts
#             ###[ 1.0,   20,     839.8 ,  879.8,],
#             [ 1.0,   20,     854.5,   894.0,],
#             [ 1.0,  100,     760.3,   893.0,],
#             [ 1.0,  120,     749.2,   891.3,], 
#             [ 1.0,  220,     620.3,   893.7,],
#             [ 1.5,  220,     823.0,  1218.2,],
#             [ 2.2,   47,    1336.0,  1480.3,],
#             [ 2.2,   67,    1265.2,  1477.6,],
#             [ 4.7,   20,    1954.0,  2071.3,],
#             [ 4.7,  100,    1519.4,  2071.7,],
#             [10.0,   20,    2344.7,  2521.8,],
#             [10.0,  100,    1756.8,  2521.4,],
#             [10.0,  220,    1480.9,  2521.7,],
#             ]
# }
#
#
#
# # data_aqs6=[
# #     [1.0, 1    , 862.1  ,     891.3 ],  #semi no one
# #     [1.0, 100,  774.8 ,   893.8],
# #     [2.2, 1    , 1446.4 ,  1487.7],
# #     [2.2, 220,  948.6 ,  1489.4],
# #     [4.7, 1    , 2045.8 ,  2101.9],
# #     [4.7, 220, 1229.4 ,  2068.0],
# #     [10.0, 1 , 2449.8 ,  2519.3],
# #     [10.0, 47, 2086.3 ,  2522.5],
# #     [1e7, 1, 3042.5 ,  3109.9],
# #     # [],
# # ]
#
# # 1e7,  ,    2991.1 ,  3109.3    # sen0
# # ltgWasser    1092.8 ,  1452.2
# # dstwasser    1444.0 ,  1768.1
#
# # data_aqs7 = [
# # [2.2, 47, 1311 , 1482],  #1.340
# # [23.8, 47, 2304, 2824],
# # [23.8, 247, 1684, 2825],
# # [2.2, 247, 1020, 1500],
# #  [2.2, 1, 1500 - 1, 1500],
# # [23.8, 1, 2825 - 1, 2825 ],
# # # [4.4, 47, 1720.0 , 1988.1]
# # ]
#
# data_aqs7 = [         
#       # [2.2, 1, 1390.2, 1480.6       ],
#       # [4.4, 1, 1879.8, 1975.1       ],
#       # [9.1, 1, 2274.2, 2377.5       ],
#       # [13.8, 1, 2419.9, 2524.4     ],
#       # [23.8, 1, 2599.7, 2704.7     ],
#       [1.0, 47, 727.0 , 868.7         ],
#       [2.2, 47, 1220.0 , 1394.2      ],
#       [4.4, 47, 1590.8 , 1890.9      ] ,
#       [9.1, 47, 1864.9 , 2318.7      ],
#       [13.8, 47, 2006.0 , 2532.3    ],
#       [23.8, 47, 2177.4 , 2726.7    ],
#
#       [4.4, 147, 1311.0 , 1986.5 ],
#
#       [2.2, 247, 893.4 , 1472.8        ],
#       [4.4, 247, 1145.7 , 1998.7      ] ,
#       [9.1, 247, 1397.3 , 2430.6      ],
#       [13.8, 247, 1495.5 , 2616.2    ],
#       [23.8, 247, 1580.3 , 2790.9    ],
#
# ]
#
# data_t = [
#         [100, 100, 329.1 , 516.6 ],
#         [6.9, 200, 268.3 , 516.6 ],
#         [4.7, 200, 222.9 , 421.4 ],
#         [4.7, 100, 279.0 , 422.0 ],
#         # [13.8, 0, 1978.9,2039. ], 
#         # [13.8, 100, 1831.9,1983.5 ], 
#         # [13.8, 147, 1800.9,1949.7], 
#     ]
#
# sensors = {
#     'aqs5':aqs5,
#     'aqs6':aqs6,
#     }


def interpolate_or_extrapolate_z(xy, z, x_query, y_query):
    # pts = np.array(points)
    # xy = pts[:, :2]
    # z = pts[:, 2]

    tri = Delaunay(xy)

    simplex = tri.find_simplex([[x_query, y_query]])

    if simplex < 0:
        # nächstgelegenes Dreieck über Schwerpunkt
        centers = xy[tri.simplices].mean(axis=1)
        simplex = np.argmin(np.sum((centers - [x_query, y_query]) ** 2, axis=1))
    else:
        simplex = simplex[0]

    T = tri.transform[simplex]

    # affine Koordinaten
    r = T[:2,:].dot(np.array([x_query, y_query]) - T[2,:])
    bary = np.array([r[0], r[1], 1.0 - r.sum()])  # darf < 0 sein → Extrapolation

    verts = tri.simplices[simplex]
    return float(np.dot(bary, z[verts]))

  
class Interpolator():

    def __init__(self, data):
        
        self.data = np.array(data['cal'])
        # self.data = np.array(data)
    
        self.measures = self.data[:, 2:]
        self.Rs = self.data[:, 0]
        self.Cs = self.data[:, 1]
        self.Ts = self.data[:, 0] * self.data[:, 1]
        self.usf_errs = np.zeros(len(self.data))
        self.us1_errs = np.zeros(len(self.data))

        self.u0 = 3.3
        # self.r0 = 2.2e3 #data['params']['r0']*1e3
        # self.dt = 1 / 160e6 * 12#data['params']['rout']*1e3
        # self.rout= 470e3 #data['params']['dt']
        self.r0 = data['params']['r0'] * 1e3
        self.rout = data['params']['rout'] * 1e3
        self.dt = data['params']['dt']
        self.du = data['params']['du']
        
        for i in range(len(self.data)):
            # self.usfs[i], self.us1s [i]=self.calc_err_usf_us0 (self.data[i][0], self.data[i][1])
            self.usf_errs[i], self.us1_errs [i] = self.calc_err_usf_us1 (self.data[i])

        self.interpolatorUsf_err = LinearNDInterpolator(self.measures, self.usf_errs)
        self.interpolatorUs1_err = LinearNDInterpolator(self.measures, self.us1_errs)
        
        # self.interpolatorUsf_err = LinearNDInterpolator(self.measures, self.usf_errs)
        # self.interpolatorUs1_err = LinearNDInterpolator(self.measures, self.us1_errs)
        
        self.coeffs_usf_err = fit_quadratic_surface(self.data[:, 2], self.data[:, 3], self.usf_errs)
        self.coeffs_us1_err = fit_quadratic_surface(self.data[:, 2], self.data[:, 3], self.us1_errs)
        
        self.coeffs_rs = fit_quadratic_surface(self.data[:, 2], self.data[:, 3], self.data[:, 0])
        self.coeffs_cs = fit_quadratic_surface(self.data[:, 2], self.data[:, 3], self.data[:, 1])
        
        self.spline_cs = SmoothBivariateSpline(self.data[:, 2], self.data[:, 3], self.data[:, 1], kx=2, ky=2)
        self.spline_rs = SmoothBivariateSpline(self.data[:, 2], self.data[:, 3], self.data[:, 0], kx=2, ky=2)
        pass

    def getUs(self, aif, ai1):
        usf = aif + self.interpolatorUsf_err((aif, ai1))
        us1 = ai1 + self.interpolatorUs1_err((aif, ai1))
        return usf, us1
    
    def getRC(self, aif, ai1):
        dusf = self.interpolatorUsf_err((aif, ai1))
        dus1 = self.interpolatorUs1_err((aif, ai1))
        
        # xy = self.data[:, 2:]
        # z  = self.
        # dusf = interpolate_or_extrapolate_z(xy, z, aif, ai1)
        # dus1 = self.interpolatorUs1_err((aif, ai1))
        uf = aif * self.du
        usf = uf + dusf
        u1 = ai1 * self.du
        us1 = u1 + dus1
        
        '''    
         us1 = u0*rs/(rs+r0)
        us1*rs + us1*r0 =u0* rs
        us1*r0 = rs(u0-us1)
        rs=us1*r0 /(u0-us1)
        '''
        rs = us1 * self.r0 / (self.u0 - us1)
        
        '''
        us*e^(-t/T)=u0-us      wg. symmetrie
        ln(us) -dt/T=ln(u0-us)
        ln(us)-ln(u0-us) = dt/T
        T=dt/ln(us/(u0-us))
        cs=T/rs
        '''
        T = self.dt / math.log(usf / (us1 - usf))

        cs = T / (rs * self.r0 / (rs + self.r0))
        
        self.uf = uf
        self.u1 = u1
        self.usf = usf
        self.us1 = us1
        self.rs = rs 
        self.cs = cs 
        self.T = T
        # return rs, cs
        return round(rs, 0), round(cs * 1e12, 0)

    def getRC_spline(self, aif, ai1):
        # rs = quadratic_surface(aif, ai1, self.coeffs_rs)
        cs = self.spline_cs(aif, ai1)[0][0]
        rs_spline = self.spline_rs(aif, ai1)[0][0]
        
        # # xy = self.data[:, 2:]
        # # z  = self.
        # # dusf = interpolate_or_extrapolate_z(xy, z, aif, ai1)
        dus1 = self.interpolatorUs1_err((aif, ai1))
        # uf=aif * self.du
        # usf =  uf + dusf
        # if usf <=0: usf=.001
        u1 = ai1 * self.du
        us1 = u1 + dus1
        
        '''    
         us1 = u0*rs/(rs+r0)
        us1*rs + us1*r0 =u0* rs
        us1*r0 = rs(u0-us1)
        rs=us1*r0 /(u0-us1)
        '''
        rs = us1 * self.r0 / (self.u0 - us1)
        
        '''
        us*e^(-t/T)=u0-us      wg. symmetrie
        ln(us) -dt/T=ln(u0-us)
        ln(us)-ln(u0-us) = dt/T
        T=dt/ln(us/(u0-us))
        cs=T/rs
        '''
        # T = self.dt / math.log(usf / (us1 - usf))
        #
        # cs = T / (rs * self.r0 / (rs + self.r0))
        #
        # self.uf=uf
        # self.u1=u1
        # self.usf = usf
        # self.us1 = us1
        # self.rs = rs 
        # self.cs = cs 
        # self.T = T
        return rs, cs, #rs_spline
        # return round(rs, 0), round(cs * 1e12, 0)

# quadratic_surface
    def getRC4(self, aif, ai1):
        # rs = quadratic_surface(aif, ai1, self.coeffs_rs)
        cs = quadratic_surface(aif, ai1, self.coeffs_cs)
        
        # # xy = self.data[:, 2:]
        # # z  = self.
        # # dusf = interpolate_or_extrapolate_z(xy, z, aif, ai1)
        dus1 = self.interpolatorUs1_err((aif, ai1))
        # uf=aif * self.du
        # usf =  uf + dusf
        # if usf <=0: usf=.001
        u1 = ai1 * self.du
        us1 = u1 + dus1
        
        '''    
         us1 = u0*rs/(rs+r0)
        us1*rs + us1*r0 =u0* rs
        us1*r0 = rs(u0-us1)
        rs=us1*r0 /(u0-us1)
        '''
        rs = us1 * self.r0 / (self.u0 - us1)
        
        '''
        us*e^(-t/T)=u0-us      wg. symmetrie
        ln(us) -dt/T=ln(u0-us)
        ln(us)-ln(u0-us) = dt/T
        T=dt/ln(us/(u0-us))
        cs=T/rs
        '''
        # T = self.dt / math.log(usf / (us1 - usf))
        #
        # cs = T / (rs * self.r0 / (rs + self.r0))
        #
        # self.uf=uf
        # self.u1=u1
        # self.usf = usf
        # self.us1 = us1
        # self.rs = rs 
        # self.cs = cs 
        # self.T = T
        return rs, cs
        # return round(rs, 0), round(cs * 1e12, 0)

    def getRC3(self, aif, ai1):
        dusf = quadratic_surface(aif, ai1, self.coeffs_usf_err)
        dus1 = quadratic_surface(aif, ai1, self.coeffs_us1_err)
        
        # xy = self.data[:, 2:]
        # z  = self.
        # dusf = interpolate_or_extrapolate_z(xy, z, aif, ai1)
        # dus1 = self.interpolatorUs1_err((aif, ai1))
        uf = aif * self.du
        usf = uf + dusf
        if usf <= 0: usf = .001
        u1 = ai1 * self.du
        us1 = u1 + dus1
        
        '''    
         us1 = u0*rs/(rs+r0)
        us1*rs + us1*r0 =u0* rs
        us1*r0 = rs(u0-us1)
        rs=r0 * us1/(u0-us1)
        '''
        rs = self.r0 * us1 / (self.u0 - us1)
        
        '''
        us*e^(-t/T)=u0-us      wg. symmetrie
        ln(us) -dt/T=ln(u0-us)
        ln(us)-ln(u0-us) = dt/T
        T=dt/ln(us/(u0-us))
        cs=T/rs||r0
        '''
        T = self.dt / math.log(usf / (us1 - usf))

        cs = T / (rs * self.r0 / (rs + self.r0))
        
        self.uf = uf
        self.u1 = u1
        self.usf = usf
        self.us1 = us1
        self.rs = rs 
        self.cs = cs 
        self.T = T
        # return rs, cs
        return round(rs, 0), round(cs * 1e12, 0)

    def getRC2(self, aif, ai1):

        aif = aif * self.du
        ai1 = ai1 * self.du
        
        xy = self.measures

        z = self.usf_errs
        dusf = interpolate_or_extrapolate_z(xy, z, aif, ai1)

        z = self.us1_errs
        dus1 = interpolate_or_extrapolate_z(xy, z, aif, ai1)

        usf = (aif + dusf)
        us1 = (ai1 + dus1)
        
        '''    
         us1 = u0*rs/(rs+r0)
        us1*rs + us1*r0 =u0* rs
        us1*r0 = rs(u0-us1)
        rs=us1*r0 /(u0-us1)
        '''
        rs = us1 * self.r0 / (self.u0 - us1)
        
        '''
        us*e^(-t/T)=u0-us      wg. symmetrie
        ln(us) -dt/T=ln(u0-us)
        ln(us)-ln(u0-us) = dt/T
        T=dt/ln(us/(u0-us))
        cs=T/rs
        '''
        T = self.dt / math.log(usf / (us1 - usf))

        cs = T / (rs * self.r0 / (rs + self.r0))
        
        # return rs, cs
        return round(rs, 0), round(cs * 1e12, 0)

    def calc_usf_us0(self, rs, cs):
        krs = rs / (rs + self.r0)
        us0 = self.u0 * krs
        rs_r0 = self.r0 * krs  # rs||r0
        T = rs_r0 * cs
        '''
        us*e^(-t/T)=u0-us     # wg. symmetrie
        us=u0/(e^(-t/T)+1)
        '''
        usf = us0 / (math.exp(-self.dt / T) + 1)

        return usf, us0

    def calc_err_usf_us1(self, data):
        rs = data[0] * 1e3
        cs = data[1] * 1e-12
        aif = data[2] * self.du
        ai1 = data[3] * self.du
        
        ioutf = aif / self.rout
        iout1 = ai1 / self.rout
        '''
        Superpos.
        a)
       iout=ai/rout
       us=ur0=rs||r0*iout = ai/rout*rs*r0/(rs+r0)
       b)
       us=u0*rs/(r0+rs)   
        '''
        krs = rs / (rs + self.r0)
        rs_r0 = self.r0 * krs  # rs||r0
        us1 = self.u0 * krs - iout1 * rs_r0  # iout*r0||rs
        T = rs_r0 * cs
        '''
        us*e^(-t/T)=u0-us     # wg. symmetrie
        us=u0/(e^(-t/T)+1)
        '''
        usf = us1 / (math.exp(-self.dt / T) + 1)

        # us_error, U_diode(aif, ai1)
        return usf - aif, us1 - ai1


import numpy as np


def fit_quadratic_surface(x, y, z):
    """
    Fit z = a*x^2 + b*y^2 + c*x*y + d*x + e*y + f
    """
    # Design-Matrix
    A = np.column_stack([
        x ** 2,
        y ** 2,
        x * y,
        x,
        y,
        np.ones_like(x)
    ])

    # Least Squares
    coeffs, _, _, _ = np.linalg.lstsq(A, z, rcond=None)

    return coeffs  # a, b, c, d, e, f


def quadratic_surface(x, y, coeffs):
    a, b, c, d, e, f = coeffs
    return a * x ** 2 + b * y ** 2 + c * x * y + d * x + e * y + f


def test():
    print ('aqs5')
    rcint = Interpolator(aqs5)

    R, C = rcint.getRC2 (84.1 , 222.9); 
    print(int(R), ", ", int(C), "  cal aqs5")
    
    R, C = rcint.getRC2 (209.1 , 488.1); 
    print(int(R), ", ", int(C), "?")
    
############    
    print ('aqs5')

    rcint = Interpolator(aqs6)
    
    R, C = rcint.getRC3 (960 , 1489.4); 
    print(int(R), ", ", int(C))
    # #
    R, C = rcint.getRC3 (1756.8 , 2521.4); 
    print(int(R), ", ", int(C), "  10,100")
    
    # R, C = rcint.getRC (749.2 ,  891.3 ); 
    R, C = rcint.getRC3 (749.2 , 895); 
    print(int(R), ", ", int(C), "  1,120")
    
    R, C = rcint.getRC3 (1092.8 , 1452.2); 
    print(int(R), ", ", int(C), "  ltgWasser")
    #
    R, C = rcint.getRC3 (1444.0 , 1768.1); 
    print(int(R), ", ", int(C), "  dstwasser")
    
    R, C = rcint.getRC3 (774.8 , 893.8); 
    print(int(R), ", ", int(C), "  1,100")
    
    R, C = rcint.getRC3 (1528.2 , 2068.1); 
    print(int(R), ", ", int(C), "?4.7,100")

    R, C = rcint.getRC3 (1266.2 , 1478.4); 
    print(int(R), ", ", int(C), "2.2,47+20")

    R, C = rcint.getRC3 (823.0 , 1218.2); 
    print(int(R), ", ", int(C), "1.5, 220")

    # R, C = rcint.getRC3 (1100.0 ,  1800.2); 
    # print(int(R), ", ", int(C), "")


def test3():
    print ('aqs6')
    rcint = Interpolator(aqs6)

    R, C = rcint.getRC3 (823.0 , 1218.2); 
    print(round(R, 1), ", ", int(C), "1.5, 220")
    
    R, C = rcint.getRC3 (854.5, 894.0,); 
    print(round(R, 1), ", ", int(C), "1., 20")
    
    R, C = rcint.getRC3 (1519.4, 2071.7); 
    print(round(R, 1), ", ", int(C), "4.7,  100,")
def test4():
    print ('aqs6')
    rcint = Interpolator(aqs6)

    R, C = rcint.getRC4 (823.0 , 1218.2); 
    print(round(R, 1), ", ", int(C), "1.5, 220")
    
    R, C = rcint.getRC4 (854.5, 894.0,); 
    print(round(R, 1), ", ", int(C), "1., 20")
    
    R, C = rcint.getRC4 (1519.4, 2071.7); 
    print(round(R, 1), ", ", int(C), "4.7,  100,")
    
def test_spline():
    print ('aqs6 spline')
    rcint = Interpolator(aqs6)

    R, C = rcint.getRC_spline (823.0 , 1218.2); 
    print(round(R, 1), ", ", int(C), "1.5, 220")
    
    R, C = rcint.getRC_spline (854.5, 894.0,); 
    print(round(R, 1), ", ", int(C), "1., 20")
    
    R, C = rcint.getRC_spline (1519.4, 2071.7); 
    print(round(R, 1), ", ", int(C), "4.7,  100,")
    
    R, C = rcint.getRC_spline (2344.7 ,  2521.8); 
    print(round(R, 1), ", ", int(C), "10,  20,")

    R, C = rcint.getRC_spline (903.0 ,  1300.8); 
    print(round(R, 1), ", ", int(C), "aqs6 erde")
    
     
    
if __name__ == "__main__":
    test3()
    test4()
    test_spline()
 
