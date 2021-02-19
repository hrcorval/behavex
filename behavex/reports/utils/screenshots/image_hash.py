# -*- encoding: utf-8 -*
"""
BehaveX - BDD testing library based on Behave
"""
# pylint: disable=W0403, R0903
# __future__ and six have been added in order to maintain compatibility
from __future__ import absolute_import
from __future__ import print_function
from PIL import Image
import numpy


def binary_array_to_hex(arr):
    """convert from array to hex"""
    hex_ = 0
    sub = []
    for i, vect in enumerate(arr.flatten()):
        if vect:
            hex_ += 2**(i % 8)
        if (i % 8) == 7:
            sub.append(hex(hex_)[2:].rjust(2, '0'))
    return "".join(sub)


def binary_array_to_int(arr):
    """convert from binary array to int"""
    return sum([2**(i % 8) for i, v in enumerate(arr.flatten()) if v])


# Disabling pylint error until Numpy version gets updated to v1.9.X
# pylint: disable=E1101
class ImageHash(object):
    """
    Hash encapsulation. Can be used for dictionary keys and comparisons.
    """
    def __init__(self, binary_array):
        self.hash = binary_array

    def __str__(self):
        return binary_array_to_hex(self.hash)

    def __repr__(self):
        return repr(self.hash)

    def __sub__(self, other):
        assert self.hash.shape == other.hash.shape, ('ImageHashes must be of '
                                                     'the same shape!',
                                                     self.hash.shape,
                                                     other.hash.shape)
        return (self.hash != other.hash).sum()

    def __eq__(self, other):
        """Function especial eq"""
        return numpy.array_equal(self.hash, other.hash)

    def __ne__(self, other):
        return not numpy.array_equal(self.hash, other.hash)

    def __hash__(self):
        return binary_array_to_int(self.hash)


def dhash(image, hash_size=8):
    """
    Difference Hash computation.
    following http://www.hackerfactor.com/blog/index.php?/archives/
    529-Kind-of-Like-That.html
    @image must be a PIL instance.
    """
    image = image.convert("L").resize((hash_size + 1, hash_size),
                                      Image.ANTIALIAS)
    pixels = numpy.array(image.getdata(), dtype=numpy.float).reshape(
        (hash_size + 1, hash_size))
    # compute differences
    diff = pixels[1:, :] > pixels[:-1, :]
    return ImageHash(diff)


__dir__ = [ImageHash]

