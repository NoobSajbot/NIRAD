'''author__ = 'Alberto Costa'
   mail = 'noobsajbot@gmail.com'
   date = '21 Apr 2025'

   model representing the optimality problem of the robustness algorithm (worst-case attack)
'''

from __future__ import division
from pyomo.environ import *

model = AbstractModel()

model.n = Param(within=NonNegativeIntegers) #number of vertices
model.gamma = Param(within=NonNegativeReals, mutable = True, default = 0) #gamma value
model.s = Param(within=NonNegativeIntegers) #source node index
model.t = Param(within=NonNegativeIntegers) #terminal node index

model.V = RangeSet(1,model.n) #vertices set
model.A = Set(within=model.V * model.V) #arcs set

model.capacity = Param(model.A) #capacities of arcs
model.cost = Param(model.A) #costs to attack arcs
model.y= Param(model.A, default = 0, mutable = True) #fortification plan, mutable because they will change at every iteration

model.alpha = Var(model.V, domain = Binary)
model.beta = Var(model.A, domain = Binary)
model.z = Var(model.A, domain = Binary)



def obj_expression(model):
    return summation(model.capacity, model.beta)

model.OBJ = Objective(rule=obj_expression, sense = minimize)


#ADD
model.c = ConstraintList()

def constraint_1_rule(model, i, j):
    return model.alpha[i] - model.alpha[j] + model.beta[i,j] + model.z[i,j] >= 0

model.constraint_1 = Constraint(model.A, rule = constraint_1_rule)


def constraint_source_rule(model):
    return model.alpha[value(model.s)] == 0

model.constraint_source = Constraint(rule = constraint_source_rule)


def constraint_terminal_rule(model):
    return model.alpha[value(model.t)] == 1

model.constraint_terminal = Constraint(rule = constraint_terminal_rule)


def constraint_budget_rule(model):
    return sum(model.z[i,j] * (model.cost[i,j] + model.y[i,j]) for (i,j) in model.A ) <= model.gamma

model.constraint_budget = Constraint(rule = constraint_budget_rule)




