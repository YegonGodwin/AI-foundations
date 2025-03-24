import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv('datab.csv')
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']
explode = (0.05, 0, 0, 0.3,0)

plt.pie(data.user_id, explode=explode, colors=colors, labels = data.iloc[:, 1])
plt.title("Pie chart Depicting shares of each individual")
plt.show()
