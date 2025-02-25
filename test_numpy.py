"""
import numpy as np

a = np.arange(int(1e6)).reshape((1000,1000))
for _ in range(int(1e5)):
    a @ a
"""
import numpy as np

# Creating very large arrays
arr1 = np.random.rand(10000, 10000)
arr2 = np.random.rand(10000, 10000)

# Performing lots of math that should utilize multiple cores
result = np.dot(np.linalg.inv(arr1), arr2)

print("Finished")

