import numpy as np
import matplotlib.pyplot as plt

x = np.arange(20)
y = np.full(20, 0)
plt.xticks(range(len(x)), x)
plt.xlabel("Iterations")
plt.ylabel("D")
plt.plot(x,y)
plt.show()
