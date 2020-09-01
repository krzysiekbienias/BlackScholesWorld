import matplotlib.pyplot as plt
import os



class PlotFinanceGraphs:
    def __init__(self):
        self.storePng='/Users/krzysiekbienias/Documents/GitHub/BlackScholesWorld/HelperFiles'


    def manyPlots(self,arg,l_values,ls_labes,figName,xAxisName=None,yAxisName=None,title=None,):
        os.chdir(self.storePng)
        for i in range(len(l_values)):
            plt.plot(arg, l_values[i], label=ls_labes[i])

        plt.xlabel(xAxisName)
        plt.ylabel(yAxisName)
        plt.title(title)
        plt.legend()
        plt.savefig(figName)

