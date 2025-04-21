'''author__ = 'Alberto Costa'
   mail = 'noobsajbot@gmail.com'
   date = '21 Apr 2025'

model representing the feasibility problem of the robustness algorithm
'''




from __future__ import division
from pyomo.environ import *

model = AbstractModel()

model.n = Param(within=NonNegativeIntegers) #number of nodes
model.gamma = Param(within=NonNegativeReals, mutable = True, default = 0) #gamma value
model.s = Param(within=NonNegativeIntegers) #source node index
model.t = Param(within=NonNegativeIntegers) #terminal node index

#added
model.F = Param(within=NonNegativeReals, mutable = True, default = 0) #fort. budget value

model.V =RangeSet(1, model.n)
model.A = Set(within=model.V * model.V) #arcs set

model.capacity = Param(model.A) #capacities of arcs
model.cost = Param(model.A) #costs to attack arcs
model.z = Param(model.A,  domain = Binary)

model.tobj = Var(domain=Reals)


#fortification plan, mutable because they will change at every iteration - UB will be changed at each first iter to None or 0
model.y= Var(model.A, domain = NonNegativeReals, bounds = (0, model.F))  # if I do not use aux.update_bounds set ub to None instead of set.F

def obj_expression(model):
    return model.tobj
    #return summation(model.y)

model.OBJ = Objective(rule=obj_expression, sense = maximize)



model.c = ConstraintList()

def constraint_1_rule(model):
    return sum(model.y[i,j] for (i,j) in model.A)  <= model.F

model.constraint_1 = Constraint(rule = constraint_1_rule)


