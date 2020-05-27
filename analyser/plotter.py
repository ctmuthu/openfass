import matplotlib.pyplot as plt

def plot(dt,value):
    plt.plot(dt,value)
    plt.show()

def multiplot(cpuDT, cpuSec, memDT, memUsage, reqDT, reqCount, res200DT, res200Count, res502DT, res502Count, resDT, resTime):
    #print(cpuDT, cpuSec, memDT, memUsage, reqDT, reqCount, res200DT, res200Count, res502DT, res502Count, resDT, resTime)
    
    plt.figure()

    plt.subplot(321)
    plt.plot(cpuDT, cpuSec)
    plt.ylabel('CPU Total Seconds')
    plt.grid(True)

    plt.subplot(322)
    plt.plot(memDT, memUsage)
    plt.ylabel('Pod memory usage')
    plt.grid(True)

    plt.subplot(323)
    plt.plot(reqDT, reqCount)
    plt.ylabel('HTTP requests')
    plt.grid(True)

    plt.subplot(324)
    plt.plot(res200DT, res200Count)
    plt.ylabel('Successful Response 200')
    plt.grid(True)

    plt.subplot(325)
    plt.plot(res502DT, res502Count)
    plt.ylabel('Failed requests 502')
    plt.grid(True)

    plt.subplot(326)
    plt.plot(resDT, resTime)
    plt.ylabel('Response time')
    plt.grid(True)

    plt.savefig('./analyser/graph.png')
    plt.show()