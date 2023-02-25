import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy 

outputDir = "figures/set2.png"

title = "paretoFront"

inputDir = "results/paretoFront2.txt"

lims = [[0,260],[-260,0]]

paretoFront= pd.read_csv(inputDir, names=["X","Y"], sep="\t")

fig,ax = plt.subplots(1,1, figsize=(10,10))
ax.scatter(x = paretoFront["X"], y = paretoFront["Y"], c = "red", s = 100, alpha = 0.3)
ax.set_title(title)
#ax.axis("square")
ax.set_xlim(lims[0])
ax.set_ylim(lims[1])
ax.grid(True)
plt.savefig(outputDir)
plt.close()
