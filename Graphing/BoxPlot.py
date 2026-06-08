import matplotlib.pyplot as plt
import numpy as np
import csv
import pandas as pd

df = pd.read_csv("Testvaluestense2.csv")
#print(df.to_numpy())

data = df.iloc[:, 1]

plt.boxplot(data, orientation="vertical", whis = 1.5, sym = "*")
plt.show()
print(data)

#with open("Testvalues.csv", "r", newline="") as f:
#    data = csv.reader(f)
#    #print(data)
#    for row in data:
#        print(row)