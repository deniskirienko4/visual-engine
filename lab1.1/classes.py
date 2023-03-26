from typing import Union


@property
def restricted(obj: str):
    raise AttributeError(f'{obj.__class__} does not have this attribite')


class Matrix:
    def __init__(self, data: Union[list[list[float]], 'Vector', 'Point']):
        if isinstance(data, Point) or isinstance(data, Vector):
            data = [data.values]
        self.data = data
        self.rows = len(data)
        self.columns = len(data[0])
        for i in range(self.rows-1):
            if len(self.data[i]) != len(self.data[i+1]):
                raise Exception("not rectangular matrix")

    def zero_matrix(rows: int, columns: int):
        data = [[0 for j in range(columns)] for i in range(rows)]
        return Matrix(data)

    def identity_matrix(size: int):
        result = Matrix.zero_matrix(size, size)
        for i in range(size):
            for j in range(size):
                if i == j:
                    result.data[i][j] = 1
        return result

    def __add__(self, obj: 'Matrix'):
        if isinstance(obj, Matrix):
            result = Matrix.zero_matrix(self.rows, self.columns)
            if self.rows == obj.rows and self.columns == obj.columns:
                result.data = [[self.data[row][column] + obj.data[row][column]
                                for column in range(self.columns)]
                               for row in range(self.rows)]
                return result
            raise Exception("different sizes")
        raise TypeError("wrong usage of addition")

    def __product(self, obj1: Union['Matrix', float, int],
                  obj2: Union['Matrix', float, int]):
        if isinstance(obj1, Matrix) and isinstance(obj2, Matrix):
            if obj1.columns == obj2.rows:
                result = [[sum(a * b for a, b in zip(A_row, B_col))
                           for B_col in zip(*obj2.data)]
                          for A_row in obj1.data]
                return Matrix(result)
            raise Exception("wrong sizes")

        elif isinstance(obj1, (float, int)) and isinstance(obj2, Matrix):
            result = Matrix.zero_matrix(obj2.rows, obj2.columns)
            for i in range(obj2.rows):
                for j in range(obj2.columns):
                    result.data[i][j] *= obj1
            return result

        elif isinstance(obj1, Matrix) and isinstance(obj2, (float, int)):
            result = Matrix.zero_matrix(obj1.rows, obj1.columns)
            for i in range(obj1.rows):
                for j in range(obj1.columns):
                    result.data[i][j] = obj1.data[i][j] * obj2
            return result
        raise Exception("not a matrix or a scalar")

    def copy(self):
        result = Matrix.zero_matrix(self.rows, self.columns)
        for i in range(self.rows):
            for j in range(self.columns):
                result[i][j] = self[i][j]
        return result

    def __mul__(self, obj: 'Matrix'):
        if (isinstance(self, (Matrix, int, float))
                and isinstance(obj, (Matrix, int, float))):
            return self.__product(self, obj)
        raise TypeError("wrong usage of multiply")

    def __rmul__(self, obj: 'Matrix'):
        if (isinstance(self, (Matrix, int, float))
                and isinstance(obj, (Matrix, int, float))):
            return self.__product(self, obj)
        raise TypeError("wrong usage of multiply")

    def __sub__(self, obj: 'Matrix'):
        if isinstance(obj, Matrix):
            return self + (obj*(-1))
        raise TypeError("wrong usage of subtraction")

    def __getitem__(self, key: int):
        return self.data[key]

    def __setitem__(self, key: int, item):
        self.data[key] = item
        return self

    def __repr__(self):
        return f'{self.data}'

    def transpose(self):
        if isinstance(self, Matrix):
            data = [[self[j][i] for j in range(self.rows)]
                    for i in range(self.columns)]
            self = Matrix(data)
            return self
        if isinstance(self, list):
            return [[self[j][i] for j in range(len(self))]
                    for i in range(len(self[0]))]

    def __minor(self, i: int, j: int):
        return [row[:j] + row[j+1:] for row in (self[:i]+self[i+1:])]

    def determinant(self):
        if isinstance(self, Matrix):
            matrix = self.data
        else:
            matrix = self

        if len(matrix) == len(matrix[0]):
            if len(matrix) == 2:
                return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]

            determinant = 0
            for c in range(len(matrix)):
                determinant += ((-1)**c)*matrix[0][c] *\
                    Matrix.determinant(Matrix.__minor(matrix, 0, c))
            return determinant
        raise Exception("not quadratic matrix")

    def inverse(self):
        determinant = Matrix.determinant(self)
        if determinant != 0:
            if self.rows == 2:
                return Matrix([[self[1][1]/determinant, -1*self[0][1]/determinant],
                               [-1*self[1][0]/determinant, self[0][0]/determinant]])

            cofactors = []
            for r in range(self.rows):
                cofactorRow = []
                for c in range(self.rows):
                    __minor = Matrix.__minor(self, r, c)
                    cofactorRow.append(((-1)**(r+c)) *
                                       Matrix.determinant(__minor))
                cofactors.append(cofactorRow)
            cofactors = Matrix.transpose(cofactors)
            for r in range(len(cofactors)):
                for c in range(len(cofactors)):
                    cofactors[r][c] = cofactors[r][c]/determinant
            result = Matrix(cofactors)
            return result
        raise Exception("degenerate matrix")

    def gram(self):
        if self.rows == self.columns:
            result = Matrix.zero_matrix(self.rows, self.rows)
            for i in range(self.rows):
                for j in range(self.rows):
                    sum = 0
                    for k in range(self.columns):
                        sum += self[i][k]*self[j][k]
                    result[i][j] = sum
            return result
        raise Exception("not a quadratic matrix")

    def __truediv__(self, obj: Union[int, float]):
        if isinstance(obj, (int, float)):
            return self * (1/obj)
        raise Exception("not a scalar")

    def __rtruediv__(self, obj):
        raise Exception("not commutative")


class Vector(Matrix):
    def __init__(self, values: Union[list[list[float]], Matrix]):
        if isinstance(values, Matrix):
            values = values.data

        if isinstance(values[0], list):
            if len(values[0]) == 1:
                self.as_matrix = Matrix(values)
                self.values = values
                self.type = 'v'
            elif len(values) == 1:
                self.as_matrix = Matrix(values)
                self.values = values[0]
                self.type = 'h'
            else:
                raise Exception('wrong size for a vector')
        elif isinstance(values[0], (int, float)):
            self.as_matrix = Matrix([values])
            self.values = values
            self.type = 'h'

        self.size = len(values)

    def transpose(self):
        self = self.as_matrix
        data = [[self[j][i] for j in range(self.rows)]
                for i in range(self.columns)]
        self = Vector(data)
        return self

    def __getitem__(self, key: int):
        if self.type == 'h':
            return self.values[key]
        return self.values[key][0]

    def __scalar_product(self, obj: 'Vector'):
        if isinstance(obj, Vector):
            return self[0]*obj[0] + self[1]*obj[1] + self[2]*obj[2]
        raise TypeError("not a vector")

    def __vector_product(self, obj: 'Vector'):
        if self.size == 3 and obj.size == 3:
            return Vector([self[1]*obj[2] - self[2]*obj[1],
                           self[2]*obj[0] - self[0]*obj[2],
                           self[0]*obj[1] - self[1]*obj[0]])

    def __add__(self, obj: 'Vector'):
        if isinstance(self, Vector) and isinstance(obj, Vector):
            self, obj = self.as_matrix, obj.as_matrix
            result = Matrix.zero_matrix(self.rows, self.columns)
            if self.rows == obj.rows and self.columns == obj.columns:
                result.data = [[self.data[row][column] + obj.data[row][column]
                                for column in range(self.columns)]
                               for row in range(self.rows)]
                if len(result.data[0]) == 1:
                    return Vector(result)
                return Vector(result[0])
            raise Exception("different sizes")
        raise TypeError("wrong usage of addition")

    def __and__(self, obj: 'Vector'):
        return Vector.__scalar_product(self, obj)

    def __mul__(self, obj: Union[int, float, 'Vector']):
        if isinstance(obj, Vector):
            result = self.as_matrix * obj.as_matrix
            return Vector(result)
        elif isinstance(obj, (int, float)):
            result = self.as_matrix * obj
            return Vector(result)

    def __rmul__(self, obj: Union[int, float, 'Vector']):
        if isinstance(obj, Vector):
            result = self.as_matrix * obj.as_matrix
            return result
        elif isinstance(obj, (int, float)):
            result = self.as_matrix * obj
            return result

    def __pow__(self, obj: 'Vector'):
        return Vector.__vector_product(self, obj)

    def __sub__(self, obj: 'Vector'):
        return self + (obj*(-1))

    def __repr__(self):
        return f'{self.values}'

    def len(self):
        return (self & self)**0.5

    zero_matrix = restricted
    identity_matrix = restricted
    copy = restricted
    __setitem__ = restricted
    determinant = restricted
    inverse = restricted
    gram = restricted


def BilinearForm(matrix: Matrix, vec1: Vector, vec2: Vector):
    if matrix.rows == matrix.columns and matrix.rows == vec1.size and \
            matrix.rows == vec2.size:
        sum = 0
        for i in range(matrix.rows):
            for j in range(matrix.rows):
                sum += matrix[i][j]*vec1[i]*vec2[j]
        return sum
    raise Exception("wrong sizes")


class Point(Vector):
    def __add__(self, vector: Vector):
        if isinstance(vector, Vector):
            if self.size == vector.size:
                return Point([self.values[i]+vector.values[i]
                              for i in range(self.size)])
            raise Exception("wrong sizes")
        raise Exception("wrong usage of addition")

    def __radd__(self, vector: Vector):
        if isinstance(vector, Vector):
            if self.size == vector.size:
                return Point([self.values[i]+vector.values[i]
                              for i in range(self.size)])
            raise Exception("wrong sizes")
        raise Exception("wrong usage of addition")

    def __sub__(self, vector: Vector):
        if isinstance(vector, Vector):
            if self.size == vector.size:
                return Point([self.values[i]-vector.values[i]
                              for i in range(self.size)])
            raise Exception("wrong sizes")
        raise Exception("wrong usage of addition")

    __mul__ = restricted
    __rmul__ = restricted
    __and__ = restricted
    __pow__ = restricted
    transpose = restricted
    len = restricted


class VectorSpace:
    def __init__(self, basis: list[Vector]):
        self.basis = Matrix([vec.values for vec in basis])
        self.size = len(basis)

    def scalar_product(self, vec1: 'Vector', vec2: 'Vector'):
        if vec1.type == 'v' and vec2.type == 'v':
            return (vec1.transpose().as_matrix*Matrix.gram(self.basis)*vec2.as_matrix)[0][0]
        elif vec1.type == 'h' and vec2.type == 'h':
            return (vec1.as_matrix*Matrix.gram(self.basis)*vec2.transpose().as_matrix)[0][0]
        elif vec1.type == 'v' and vec2.type == 'h':
            return (vec1.transpose().as_matrix*Matrix.gram(self.basis)*vec2.transpose().as_matrix)[0][0]
        elif vec1.type == 'h' and vec2.type == 'v':
            return (vec1.as_matrix*Matrix.gram(self.basis)*vec2.as_matrix)[0][0]

    def as_vector(self, point: Point):
        if point.size == self.size:
            result = Matrix.zero_matrix(1, point.size)
            det = self.basis.determinant()
            for column in range(point.size):
                temp_matrix = self.basis.copy().transpose()
                for row in range(point.size):
                    temp_matrix[row][column] = point[row]
                result[0][column] = temp_matrix.determinant() / det
            return Vector(result)
        raise Exception("wrong sizes")


class CoorinateSystem:
    def __init__(self, initial_point: Point, vs: VectorSpace):
        self.initial_point = initial_point
        self.vs = vs
