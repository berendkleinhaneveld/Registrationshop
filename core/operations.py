"""
Operations

Vector operations. Put stuff in, get result out.
Input is never adjusted.

:Authors:
	Berend Klein Haneveld
"""
import math
import collections


def Dot(u, v):
	"""
	Returns dot product of two vectors.
	"""
	assert len(u) == len(v)
	return sum(map(lambda x, y: x * y, u, v))


def Subtract(u, v):
	"""
	Returns difference between two vectors.
	res = u - v
	"""
	assert len(u) == len(v)
	return map(lambda x, y: x - y, u, v)


def Multiply(u, s):
	"""
	Returns vector multiplied by scalar.
	"""
	def __multiply(x):
		return x * s
	return map(__multiply, u)


def Add(u, v):
	"""
	Returns addition of two vectors.
	"""
	assert len(u) == len(v)
	return map(lambda x, y: x + y, u, v)


def Length(u):
	"""
	Returns length of vector.
	"""
	return math.sqrt(sum(map(lambda x: x**2, u)))


def Normalize(u):
	"""
	Returns normalized version of vector.
	"""
	def __devide(x):
		return x / length
	length = Length(u)
	if length == 0:
		return [float('nan') for x in range(len(u))]
	return map(lambda x: __devide(x), u)


def Mean(vectors):
	"""
	Returns the mean vector of a collection of vectors.
	:type vectors: list of iterables
	"""
	assert isinstance(vectors[0], collections.Iterable)
	return Multiply(reduce(lambda x, y: Add(x, y), vectors), 1.0 / len(vectors))


def ClosestPoints(p1, p2, q1, q2, clamp=False):
	"""
	Get the 3D minimum distance between 2 lines
	input: two 3D lines p and q, defined by points p1, p2 and whether
		to clamp the output between the two given points.
	return: the two closest points on line p and q
	"""
	u = Subtract(p2, p1)
	v = Subtract(q2, q1)
	w = Subtract(p1, q1)
	a = Dot(u, u)  # always >= 0
	b = Dot(u, v)
	c = Dot(v, v)  # always >= 0
	d = Dot(u, w)
	e = Dot(v, w)
	D = a * c - b * b  # always >= 0
	sc = tc = 0.0

	# compute the line parameters of the two closest points
	if (D < 0.0000001):  # the lines are almost parallel
		sc = 0.0
		if b > c:  # use the largest denominator
			tc = d / b
		else:
			tc = e / c
	else:
		sc = (b * e - c * d) / D
		tc = (a * e - b * d) / D

	if clamp:
		sc = max(sc, 0)
		tc = max(sc, 0)
		sc = min(sc, 1)
		tc = min(tc, 1)

	return Add(Multiply(u, sc), p1), Add(Multiply(v, tc), q1)
