import pyspark
from pyspark import SparkContext
import cv2
import numpy as np 
import scipy as sp
import struct
from helper_functions import *
from constants import *

from operator import add

def sub_matrix(t):
    # t looks like (((ID, "Y"), (h, w)), Y)
    # key is ((ID, "Y/Cr/Cb"), (h, w)),
    # val is Y/Cr/Cb
    sub_blocks = []
    key = t[0]
    channel = t[1]
    channel_height, channel_width = channel.shape
    no_rows_blocks = channel_height / b_size
    no_cols_blocks = channel_width / b_size

    for col in range(no_cols_blocks):
        for row in range(no_rows_blocks):
            row_start = row * b_size
            row_end = (row + 1) * b_size
            col_start = col * b_size
            col_end = (col + 1) * b_size
            cur_block = channel[row_start : row_end, col_start : col_end]
            value = (((row, col), (channel_height, channel_width)), cur_block)
            sub_blocks.append((key, value))
    return sub_blocks

def create_big(t):
    # # key is ((ID, "Y/Cr/Cb"), (h, w))
    # val is (((row, col), (channel_height, channel_width)), plus_128(x[1][1]))
    # val is ((row, col), (x[1][0], plus_128(x[1][1]))
    key = t[0]
    val = t[1]
    row = val[0][0][0]
    col = val[0][0][1]
    channel_height = val[0][1][0]
    channel_width = val[0][1][1]
    # h = key[1][0]
    # w = key[1][1]
    matrix = val[1]
    # maybe its divide by b_size
    big = np.zeros((channel_height, channel_width), np.float32) 
    row_start = row * b_size
    row_end = (row + 1) * b_size
    col_start = col * b_size
    col_end = (col + 1) * b_size
    big[row_start:row_end, col_start:col_end] = matrix
    return (key, big)

def create_bigger(t):
    # # key is ((ID, "Y/Cr/Cb"), (h, w))
    # val is big
    key = t[0]
    val = t[1]
    h = key[1][0]
    w = key[1][1]
    matrix = t[1]
    big = np.zeros((h, w, 3), np.uint8)
    if (key[0][1] ==  "Y"):
        big[:,:,0] = resize_image(matrix, w, h)    
    elif (key[0][1] == "Cr"):
        big[:,:,1] = resize_image(matrix, w, h)
    else:
        big[:,:,2] = resize_image(matrix, w, h)
    return (key[0][0], big)

def final_picture(t):
    # key is ID
    # val is 3D picture
    return t[0], cv2.cvtColor(t[1], ycrbr2bgr)


def key_val(img):
    h, w = np.array(img[1].shape[:2])
    ID = img[0]
    Y, Cr, Cb = convert_to_YCrCb(img[1])
    return ((((ID, "Y"), (h, w)), Y), 
            (((ID, "Cr"), (h, w)), Cr), 
            (((ID, "Cb"), (h, w)), Cb))

def plus_128(pixel):
    pixel += 128
    pixel[pixel > 255] = 255
    pixel[pixel < 0] = 0
    return pixel


def generate_Y_cb_cr_matrices(rdd):
    rdd = rdd.flatMap(lambda x: key_val(x))
    return rdd

def generate_sub_blocks(rdd):
    rdd = rdd.flatMap(lambda x: sub_matrix(x))
    return rdd

def apply_transformations(rdd):
    # key is ((ID, "Y/Cr/Cb"), (h, w))
    # val is (((row, col), (channel_height, channel_width)), cur_block)
    dct = rdd.map(lambda x: (x[0], (x[1][0], dct_block(x[1][1].astype(np.float32) - 128))))
    # val is ((row, col), dct_block(x[1][1].astype(np.float32) - 128))
    q = dct.map(lambda x: (x[0], (x[1][0], quantize_block(x[1][1], x[0][0][1] == "Y", QF))))
    # val is ((row, col), quantize_block(x[1][1], x[0][0][1] == "Y", QF)
    inv_q = q.map(lambda x: (x[0], (x[1][0], quantize_block(x[1][1], x[0][0][1]== "Y", QF, inverse = True))))
    # val is ((row, col), quantize_block(x[1][1], x[0][0][1]== "Y", QF, inverse = True)
    inv_dct = inv_q.map(lambda x: (x[0], (x[1][0], dct_block(x[1][1], inverse = True))))
    # val is ((row, col), dct_block(x[1][1], inverse = True)
    rdd = inv_dct.map(lambda x: (x[0], (x[1][0], plus_128(x[1][1]))))
    # val is ((row, col), plus_128(x[1][1]))
    return rdd

def combine_sub_blocks(rdd):
    """
    Given an rdd of subblocks from many different images, combine them together to reform the images.
    Should your rdd should contain values that are np arrays of size (height, width).
    """
    # rdd has entries with 
    # key is ((ID, "Y/Cr/Cb"), (h, w))
    # val is (((row, col), (channel_height, channel_width)), plus_128(x[1][1]))
    # val is ((row, col), (x[1][0], plus_128(x[1][1]))
    rdd = rdd.map(create_big)
    rdd = rdd.reduceByKey(np.add)
    rdd = rdd.map(create_bigger)
    rdd = rdd.reduceByKey(np.add)
    return rdd

def run(images):
    """
    Returns an RDD where all the images will be proccessed once the RDD is aggregated.
    The format returned in the RDD should be (image_id, image_matrix) where image_matrix 
    is an np array of size (height, width, 3).
    """
    sc = SparkContext()
    rdd = sc.parallelize(images, 16) \
        .map(truncate).repartition(16)
    rdd = generate_Y_cb_cr_matrices(rdd)
    rdd = generate_sub_blocks(rdd)
    rdd = apply_transformations(rdd)
    rdd = combine_sub_blocks(rdd)

    rdd = rdd.map(final_picture)
    
    return  rdd

