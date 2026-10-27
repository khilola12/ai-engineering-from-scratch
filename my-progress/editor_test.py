import os
import numpy as np
import sys
def scale(values:list[float],factor:float)->list[float]:
    return [v*factor for v in values]
result=scale([1.0,2.0 ,3.0],factor=2)
print( result )
total=np.sum(  result)
