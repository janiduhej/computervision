#!/usr/bin/env python

'''
Simple example of stereo image matching and point cloud generation.

Resulting .ply file cam be easily viewed using MeshLab ( http://meshlab.sourceforge.net/ )
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt

ply_header = '''ply
format ascii 1.0
element vertex %(vert_num)d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
'''

def write_ply(fn, verts, colors):
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'w') as f:
        f.write(ply_header % dict(vert_num=len(verts)))
        np.savetxt(f, verts, '%f %f %f %d %d %d')


if __name__ == '__main__':
    print ('loading images...')
    imgL = cv2.imread('./squirrel_images_and_data/image_0.jpg',0)
    imgR = cv2.imread('./squirrel_images_and_data/image_1.jpg',0)
    imgL = cv2.GaussianBlur( imgL,(5,5),1)  # downscale images for faster processing
    imgR = cv2.GaussianBlur( imgR, (5,5),1 )


    # disparity range is tuned for 'squirrel' image pair
    window_size = 3
    min_disp = 25
    num_disp = 112-min_disp
    stereo = cv2.StereoBM_create(numDisparities=0, blockSize=21)

    print ('computing disparity...')
    disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0

    print ('generating 3d point cloud...')
    h, w = imgL.shape[:2]
    f = 0.8*w                          # guess for focal length
    Q = np.float32([[1, 0, 0, -0.5*w],
                    [0,-1, 0,  0.5*h], # turn points 180 deg around x-axis,
                    [0, 0, 0,     -f], # so that y-axis looks up
                    [0, 0, 1,      0]])
    points = cv2.reprojectImageTo3D(disp, Q)
    colors = cv2.cvtColor(imgL, cv2.COLOR_BGR2RGB)
    mask = disp > disp.min()
    out_points = points[mask]
    out_colors = colors[mask]
    out_fn = 'out.ply'
    write_ply('out.ply', out_points, out_colors)
    print ('%s saved' % 'out.ply')
    plt.subplot(121), plt.imshow(cv2.cvtColor(imgL, cv2.COLOR_BGR2RGB))
    plt.subplot(122), plt.imshow(cv2.cvtColor(imgR, cv2.COLOR_BGR2RGB))
    plt.show()
    cv2.imshow('left', imgL)
    cv2.imshow('right', imgR)

    cv2.imshow('disparity', (disp-min_disp)/num_disp)
    cv2.waitKey()
    cv2.destroyAllWindows()