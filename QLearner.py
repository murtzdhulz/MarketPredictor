"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand

class QLearner(object):

    def __init__(self, \
        num_states=100, \
        num_actions = 4, \
        alpha = 0.2, \
        gamma = 0.9, \
        rar = 0.5, \
        radr = 0.99, \
        dyna = 0, \
        verbose = False):

        self.verbose = verbose
        self.num_actions = num_actions
        self.s = 0
        self.a = 0
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.Q_table = np.random.uniform(-1,1,size=(num_states,num_actions))

        self.dyna = dyna
        self.Tc = np.ndarray([num_states,num_actions,num_states])
        self.Tc.fill(0.000001)
        self.T = np.zeros([num_states,num_actions,num_states])
        self.R = np.zeros([num_states,num_actions])
        self.seen_states = []

    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action
        """
        self.s = s

        rand_Gen = np.random.random()

        if rand_Gen <= self.rar:
            action = rand.randint(0, self.num_actions-1)
        else:
            action = np.asarray(self.Q_table[self.s,:]).argmax()

        self.rar *= self.radr
        if self.verbose: print "s =", s,"a =",action

        self.a = action
        #print 'RAR:',self.rar
        return action

    def query(self,s_prime,r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """
        self.seen_states.append((self.s,self.a))
        #print len(self.seen_states)

        self.Q_table[self.s,self.a] = ((1-self.alpha)*self.Q_table[self.s,self.a]) + (self.alpha*(r + self.gamma*max(self.Q_table[s_prime,cur_action] for cur_action in range(0,self.num_actions))))

        rand_Gen = np.random.random()

        if rand_Gen <= self.rar:
            action = rand.randint(0, self.num_actions-1)
        else:
            action = np.asarray(self.Q_table[s_prime,:]).argmax()

        self.rar *= self.radr

        if self.verbose: print "s =", s_prime,"a =",action,"r =",r

        self.s = s_prime
        self.a = action

        #DYNA PART
        alphar = 0.2
        self.Tc[self.s,self.a,s_prime] += 1
        self.T[self.s,self.a,s_prime] = self.Tc[self.s,self.a,s_prime]/sum(self.Tc[self.s, self.a, :])
        self.R[self.s,self.a] = (1 - alphar) * self.R[self.s,self.a] + alphar * r

        if len(self.seen_states) > 100:
            for i in range(0, self.dyna):
                cur_s, cur_a = self.seen_states[np.random.randint(0,len(self.seen_states))]
                #print 'Dyna - ',cur_s,cur_a
                r = self.R[cur_s,cur_a]
                prob_dist_list = []
                for s_loop in range(0,self.Q_table.shape[0]):
                    prob_dist_list.append(self.T[cur_s,cur_a,s_loop])

                prob_dist_list = np.array(prob_dist_list)

                #print 'The problematic value',sum(self.T[cur_s,cur_a, :])

                prob_dist_list = prob_dist_list/sum(self.T[cur_s,cur_a, :])

                #print prob_dist_list
                cumulative_dist = np.cumsum(prob_dist_list)
                rand_float = np.random.random()
                cur_s_prime = 0
                for states in range(0,len(cumulative_dist)):
                    if rand_float < cumulative_dist[states]:
                        cur_s_prime = states
                        break

                self.Q_table[cur_s,cur_a] = ((1-self.alpha)*self.Q_table[cur_s,self.a]) + (self.alpha*(r + self.gamma*max(self.Q_table[cur_s_prime,cur_action] for cur_action in range(0,self.num_actions))))
                self.rar *= self.radr

        return action

if __name__=="__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
