'''
Created on 03.11.2018

@author: marek
'''


class Avg():
    '''
    Rekursive Mittelwertbildung, gedacht f�r lang laufende Tasks (z.B. Simulation, oder Echtzeit)
    Varionten:
    1. Exponentielle "Gl�ttung" analog  elektrisches RC-Glied.
    2. Gleichgewichtet
    3. Mit "Anlauf", indem die ersten Werte gleichgewichtet gemittelt werden, dann exponentiell
        -hat den Vorteil, dass nicht abgewartet werden muss, bis die exponentielle Gl�ttung sich 
        "einschwingt" (~10Gl�ttungskonsten?) sondern 
     
     Usage: 
    Calculates recurslvely avarage values, intentionaly for long running tasks,
    for "smooting" (diskretised analogon to electric RC  1-order ..xxx like RC- 1-order
    Also a variant to equaly waited avaraging, without need to buffer all the values.
    Also a "smooth" start up of the exponentiol (RC) avaraging, with eqaly avaraginglike 
    classdocs
    '''
    
    avg = 0
    avgConst = 0
    avgConstMax = 1e20
    dif = 0
    k = 0
    
    def addLaunch(self, value):
        if self.avgConst < self.avgConstMax:
            self.addEq(value)
        else:
            self.add=self.addExp
        
    def addEq(self, value):
        self.avgConst += 1
        self.k = 1 / self.avgConst
        self.addExp(value)
        
    def addExp(self, value):
        self.dif = self.k * value
        self.avg = (1 - self.k) * self.avg + self.dif
        
    def __init__(self, avgConstMax=None):
        '''
        Constructor
        '''
        if avgConstMax==None:
            self.avgConst = 0
            self.avgConstMax = 1e20
            self.add=self.addEq
        else:
            self.avgConst = 0
            self.avgConstMax = avgConstMax
            self.add=self.addLaunch


if __name__ == "__main__":
    pass   
