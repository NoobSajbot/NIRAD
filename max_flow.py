'''author__ = 'Alberto Costa'
   mail = 'noobsajbot@gmail.com'
   date = '21 Apr 2025'

model representing the max flow
'''


from __future__ import division
from pyomo.environ import *

model = AbstractModel()

model.n = Param (within=NonNegativeIntegers) #nodes number
model.s = Param (within=NonNegativeIntegers) #source node id
model.t = Param (within=NonNegativeIntegers) #terminal node id

model.V = RangeSet(1,model.n) #vertices
model.A = Set(within=model.V * model.V) #arcs

model.capacity = Param(model.A) #capacity of arcs
model.z = Param(model.A, default=0, mutable=True) #destruction cost

model.f = Var(model.A, domain=NonNegativeReals) #flow on each arc


def obj_expression(model):
    return sum(model.f[i,j] for (i,j) in model.A if j==value(model.t))


model.OBJ = Objective(rule=obj_expression, sense=maximize)


def constraint_capacity_bound_rule(model,i,j):
    return model.f[i,j] <= model.capacity[i,j]

model.constraint_capacity_bound = Constraint(model.A, rule=constraint_capacity_bound_rule)


def constraint_flow_conservation_rule(model,i):
    if (i != value(model.s) and i!= value(model.t)):
        return sum(model.f[k,j] for (k,j) in model.A  if k == i) == sum(model.f[k,j] for (k,j) in model.A if j == i)
    else:
        no_constraint = pyomo.environ.Constraint.Skip
        return no_constraint
    

model.constraint_flow_conservation = Constraint(model.V, rule=constraint_flow_conservation_rule)