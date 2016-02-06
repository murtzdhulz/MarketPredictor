__author__ = 'Murtaza'

import numpy as np

class BagLearner():

    def __init__(self, learner, bags, kwargs, boost = False):
        self.boost = boost
        self.bags = bags
        self.dataX = []
        self.dataY = []

        self.learners = []
        for i in range(0,bags):
            self.learners.append(learner(**kwargs))

    def addEvidence(self,dataX,dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        length = len(dataX)
        for oneLearner in self.learners:
            new_dataX = []
            new_dataY = []
            for j in range(length):
                random_num = np.random.randint(0,length)
                new_dataX.append(dataX[random_num])
                new_dataY.append(dataY[random_num])
            oneLearner.addEvidence(new_dataX,new_dataY)

    def query(self,points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        pred_Y = []
        for oneLearner in self.learners:
            pred_Y.append(oneLearner.query(points))
        return np.mean(pred_Y,axis=0)