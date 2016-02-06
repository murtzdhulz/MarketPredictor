__author__ = 'Murtaza'

import numpy as np
from math import pow

class KNNLearner():

    #We will initialise k and set a default value for k = 3
    def __init__(self, k = 3):
        self.k = k
        self.dataX = []
        self.dataY = []

    def addEvidence(self,dataX,dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        self.dataX = dataX
        self.dataY = dataY

    def calculate_distance(self,point1,point2):
        cur_distnce = 0
        for i in range(len(point1)):
            cur_distnce += (point1[i]-point2[i])**2
        return np.sqrt(cur_distnce)

    def query(self,points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        pred_Y = []
        for i in range(len(points)):
            eucledian_distance = []
            for j in range(len(self.dataX)):
                eucledian_distance.append(self.calculate_distance(points[i],self.dataX[j]))

            top_indices = np.argsort(eucledian_distance)
            Y_vals = []
            for idx in range(self.k):
                Y_vals.append(self.dataY[top_indices[idx]])
            pred_Y.append(np.mean(Y_vals))
        return pred_Y