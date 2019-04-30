import numpy as np

def findBoundary(image):
    ''' finds each pixel that has value 1 and is neighboring (without diagonals) a 0 pixel

    Returns:
        boundary: list of row,col coordinates which are boundary
        image.shape: dimensions of original image.
    '''
    boundary = []
    for row in range(image.shape[0]):
        for col in range(image.shape[1]):
            if image[row][col] == 1:
                try:
                    if image[row][col+1] == 0 or image[row][col-1] == 0 \
                    or image[row+1][col] == 0 or image[row-1][col] == 0:
                        boundary.append((row, col))
                except IndexError:
                    boundary.append((row,col))
    return boundary, image.shape

def createBoundaryMap(boundary, dims):
    ''' takes a boundary list and dimensions and turns this into an image of that size
    with the boundary as only pixels colored 1. 

    Returns:
        boundary_view: binary matrix with boundary values set to 1. 
    '''
    boundary_view = np.zeros(dims)
    for boundary_val in boundary:
        boundary_view[boundary_val[0]][boundary_val[1]] = 1
    return boundary_view