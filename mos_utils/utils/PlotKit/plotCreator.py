import matplotlib.pyplot as plt



class PlotFinanceGraphs:
    def __init__(self):
        pass


    def menyPlots(self,arg,l_values,ls_labes,xAxisName,yAxisName,title,figName):
        for i in range(len(l_values)):
            plt.plot(arg, l_values[i], label=ls_labes[i])

        plt.xlabel(xAxisName)
        plt.ylabel(yAxisName)
        plt.title(title)
        plt.legend()
        plt.savefig(figName+'png')

