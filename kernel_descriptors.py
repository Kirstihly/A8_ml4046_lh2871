"""
Contains kernel descriptors and tamura kernel descriptors
"""
import numpy as np
import cv2
from scipy.ndimage import gaussian_gradient_magnitude

def gaussian_kernel(x,y, gamma=5):
    """
    Computes spatial difference between x,y with gaussian kernel
    x: array of values
    y: array of values
    gamma: float hyperparam in kernel
    
    return:
    val: float numerical value of the kernel value
    """
    return np.exp(-gamma * np.square(np.linalg.norm((abs(x-y)))))

def coarseness(img, D=16):
    """
    Computes the tamura coarsness value
    
    Feature map approximated with random ortho gaussian matrix
    """
    m, n = img.shape
    z = img.flatten()
    mag, theta = gradient(img)
    mag = mag.flatten()
    
    orientation = ang_map(z,D)
    position = rbf_map(z, D/2)
    
    coarseness = np.kron()
    

def gradient(img, eps=1e-5):
    """
    Computes gradient of image after gaussian smoothing, similar to SIFT filters
    
    Follows example from https://gist.github.com/hackintoshrao/cc0e10f58079ede6866111d6ed75b420
    https://github.com/flyfj/RGBDMaze/blob/master/KernelDescriptor/kdes/gradkdes_dense.m
    
    img: 2d array of an image
    
    Return:
    mag: array of magnitude
    theta: array of orientation
    """
    sobelx = cv2.Sobel(img,-1,1,0,ksize=3)
    sobely = cv2.Sobel(img,-1,0,1,ksize=3) 
    mag = np.sqrt(sobelx ** 2 + sobely ** 2)
    t = np.arctan(sobely / np.maximum(sobelx,1e-5))
    
    #normalize
    mag = mag / np.sqrt(np.sum(mag ** 2))
    theta = []
    for i in range(t.shape[0]):
        theta.append(np.array([(np.sin(t[i][j]), np.cos(t[i][j])) for j in range(t.shape[1])]))
    
    return mag, theta

def orf_matrix(size):
    """
    Generates SQ where S diagonal matrix with entries sampled from chi-dist with d-degree freedom and
    Orthogonal random gaussian matrix Q with each entry sampled independently from N(0,1)
    
    size: tuple (D,d)
    
    Return:
    SQ: ndarray where:
        S: ndarray diagonal sampled from chi d-degree
        Q: ndarray random gaussian
    """
    D,d = size
    S = np.diag(np.random.chisquare(d, size=d))[:D]
    G = np.random.normal(size=(d,d))
    Q, R = np.linalg.qr(G)
    return np.matmul(S,Q)
    
def rbf_map(x, D):
    """
    RBF random feature map approximated by random gaussian matrix
    phi(x) = sqrt(1/D)[sin(w1T x),..., sin(wDT x), cos(w1T x),..., cos(wDT x)]T
    
    x: array
    D: int desired dimension
    Return:
    phi_x: array of mapped feature
    """
    d = len(x)
    W = orf_matrix((D,d))
    #compute sin and cos
    phi_x = np.zeros(2*D)
    for i in range(D):
        phi_x[i] = np.sin(np.matmul(W[i], x))
        phi_x[D+i] = np.cos(np.matmul(W[i], x))
    return np.sqrt(1.0/D) * phi_x

def ang_map(x, D):
    """
    Angular kernel feature map with random Gaussian
    
    x: array
    D: int mapped dimension
    
    Return:
    phi_x: array of mapped feature
    """
    d = len(x)
    G = np.random.normal(size=(D,d))
    return 1.0/np.sqrt(D) * np.sign(np.matmul(G,x))
    