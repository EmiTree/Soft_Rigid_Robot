import matplotlib.pyplot as plt
import numpy as np
import csv
import pandas as pd

dfUtense = pd.read_csv("Testvaluestense2.csv")
dfUflop = pd.read_csv("Testvaluesflop5.csv")
dfUbendL = pd.read_csv("Testvaluesflop4.csv")
dfUbendFr = pd.read_csv("Testvaluesflop3.csv")

dfBendingL = pd.read_csv("Testvaluestense2.csv")
dfBendingFr = pd.read_csv("Testvaluestense2.csv")

dfNav = pd.read_csv("Testvaluestense2.csv")
dfDistU = pd.read_csv("Testvaluestense2.csv")
dfDistFl= pd.read_csv("Testvaluestense2.csv")
dfDistL = pd.read_csv("Testvaluestense2.csv")
dfDistFo = pd.read_csv("Testvaluestense2.csv")

#print(df.to_numpy())

dataUtense = dfUtense.iloc[:, 1] + 5.5
dataUflop = dfUflop.iloc[:, 1] + 5.5
dataUbendL = dfUbendL.iloc[:, 1] + 4.9
dataUbendFr = dfUbendFr.iloc[:, 1] + 4.9

dataBendingL = dfBendingL.iloc[:, 1] + 4.9
dataBendingFr = dfBendingFr.iloc[:, 1] + 4.9

dataNav = dfBendingL.iloc[:, 1] + 4.9
dataDistU = dfBendingFr.iloc[:, 1] + 4.9
dataDistFl = dfBendingFr.iloc[:, 1] + 4.9
dataDistL = dfBendingFr.iloc[:, 1] + 4.9
dataDistFo = dfBendingFr.iloc[:, 1] + 4.9


upright = [dataUtense, dataUflop, dataUbendL, dataUbendFr]
labels = ["tense", "flop", "bend left", "bend forward"]
colors = ["skyblue", "lightcyan", "lightcoral", "lightpink"]
fig, ax = plt.subplots(1)
output = plt.boxplot(upright, showmeans = True, labels=labels, whis = 1.5, sym = "*", showfliers = False, patch_artist=True)
ax.set_title("Leaning angle of upright soft arm positions")
plt.ylim(-2.5,2.5)
#chat: 
for i, (label, data) in enumerate(zip(labels, upright)):
    mean = np.mean(data)
    median = np.median(data)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)

    lower_cap = output["caps"][2*i].get_ydata()[0]
    upper_cap = output["caps"][2*i + 1].get_ydata()[0]

    print(f"\n{label}")
    print(f"Mean      : {mean:.2f}")
    print(f"Median    : {median:.2f}")
    print(f"25th pct  : {q1:.2f}")
    print(f"75th pct  : {q3:.2f}")
    print(f"Lower cap : {lower_cap:.2f}")
    print(f"Upper cap : {upper_cap:.2f}")
    ax.text(i + 1.05, mean,   f"μ={mean:.2f}", color="green")
    ax.text(i + 0.60, median, f"M={median:.2f}", color="red")
    ax.text(i + 1.05, q1,     f"Q1={q1:.2f}", fontsize=8)
    ax.text(i + 1.05, q3,     f"Q3={q3:.2f}", fontsize=8)
    ax.text(i + 1.05, lower_cap, f"L={lower_cap:.2f}", fontsize=8)
    ax.text(i + 1.05, upper_cap, f"U={upper_cap:.2f}", fontsize=8)
for patch, color in zip(output['boxes'], colors):
    patch.set_facecolor(color)
ax.set_ylabel("Leaning angle in degrees")
plt.show()
#print(data)




Bending = [dataBendingL, dataBendingFr]
labels = ["Bending Left", "Bending Forward"]
colors = ["lightblue", "lightcoral"]
fig, ax = plt.subplots(1)
output = plt.boxplot(Bending, showmeans = True, labels=labels, whis = 1.5, sym = "*", showfliers = False, patch_artist=True)
ax.set_title("Leaning angle of Bending soft arm positions")
plt.ylim(-2.5,2.5)
#chat: 
for i, (label, data) in enumerate(zip(labels, Bending)):
    mean = np.mean(data)
    median = np.median(data)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)

    lower_cap = output["caps"][2*i].get_ydata()[0]
    upper_cap = output["caps"][2*i + 1].get_ydata()[0]

    print(f"\n{label}")
    print(f"Mean      : {mean:.2f}")
    print(f"Median    : {median:.2f}")
    print(f"25th pct  : {q1:.2f}")
    print(f"75th pct  : {q3:.2f}")
    print(f"Lower cap : {lower_cap:.2f}")
    print(f"Upper cap : {upper_cap:.2f}")
    ax.text(i + 1.05, mean,   f"μ={mean:.2f}", color="green")
    ax.text(i + 0.60, median, f"M={median:.2f}", color="red")
    ax.text(i + 1.05, q1,     f"Q1={q1:.2f}", fontsize=8)
    ax.text(i + 1.05, q3,     f"Q3={q3:.2f}", fontsize=8)
    ax.text(i + 1.05, lower_cap, f"L={lower_cap:.2f}", fontsize=8)
    ax.text(i + 1.05, upper_cap, f"U={upper_cap:.2f}", fontsize=8)

ax.set_ylabel("Leaning angle in degrees")
for patch, color in zip(output['boxes'], colors):
    patch.set_facecolor(color)
plt.show()
print(data)

disturbances = [dataNav, dataDistU, dataDistFl, dataDistL, dataDistFo]
labels = ["Navigation", "Disturbance Upright", "Disturbance Floppy", "Disturbance Left", "Disturbance Forward"]
colors = ["lightblue", "lightcoral", "lightgreen", "lightyellow", "lightpink"]
fig, ax = plt.subplots(1)
output = plt.boxplot(disturbances, showmeans = True, labels=labels, whis = 1.5, sym = "*", showfliers = False, patch_artist=True)
ax.set_title("Leaning angle of disturbances")
plt.ylim(-2.5,2.5)
#chat: 
for i, (label, data) in enumerate(zip(labels, disturbances)):
    mean = np.mean(data)
    median = np.median(data)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)

    lower_cap = output["caps"][2*i].get_ydata()[0]
    upper_cap = output["caps"][2*i + 1].get_ydata()[0]

    print(f"\n{label}")
    print(f"Mean      : {mean:.2f}")
    print(f"Median    : {median:.2f}")
    print(f"25th pct  : {q1:.2f}")
    print(f"75th pct  : {q3:.2f}")
    print(f"Lower cap : {lower_cap:.2f}")
    print(f"Upper cap : {upper_cap:.2f}")
    ax.text(i + 1.05, mean,   f"μ={mean:.2f}", color="green")
    ax.text(i + 0.60, median, f"M={median:.2f}", color="red")
    ax.text(i + 1.05, q1,     f"Q1={q1:.2f}", fontsize=8)
    ax.text(i + 1.05, q3,     f"Q3={q3:.2f}", fontsize=8)
    ax.text(i + 1.05, lower_cap, f"L={lower_cap:.2f}", fontsize=8)
    ax.text(i + 1.05, upper_cap, f"U={upper_cap:.2f}", fontsize=8)

ax.set_ylabel("Leaning angle in degrees")
for patch, color in zip(output['boxes'], colors):
    patch.set_facecolor(color)
plt.show()
print(data)
#with open("Testvalues.csv", "r", newline="") as f:
#    data = csv.reader(f)
#    #print(data)
#    for row in data:
#        print(row)


#print(df.to_numpy())

