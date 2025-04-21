# -*- coding: utf-8 -*-
'''author__ = 'Alberto Costa'
   mail = 'noobsajbot@gmail.com'
   date = '21 Apr 2025'

   Utilities and Tools for NIRAD
'''

from __future__ import division
from smolagents import tool, OpenAIServerModel
from pyomo.environ import *
import pandas as pd
import numpy as np
import copy
from typing import Optional, Tuple, List, TypeVar
import max_flow as maxflow_abstract
import optimality_robust as rob_opt
import feasibility_robust as rob_feas
import os


DataFrame = TypeVar('pandas.core.frame.DataFrame')
MILP_solver = 'glpk'

global network_data
global nodes
global source
global terminal
global network_data_b
global nodes_b
global source_b
global terminal_b

GOOGLE_API_KEY=os.environ.get('GOOGLE_API_KEY')

input_file='input/network_test.txt'


def load_data(input_file=input_file):
   # G = nx.read_edgelist(input_file, nodetype=int, data=(("capacity", float), ("destruction_cost", float)))
   network_data=pd.read_csv(input_file, header = None, sep=" ")
   network_data.columns=['node i','node j','capacity','cost']
   source=int(network_data.iloc(0)[0]['node i']) #first node
   terminal=int(network_data.iloc(0)[network_data.shape[0]-1]['node j'])
   nodes = max (max(network_data['node i']), max(network_data['node j']))
   return [network_data,nodes,source,terminal]



#initialize variables
[network_data, nodes, source, terminal]=load_data()

#backup variables
[network_data_b,nodes_b,source_b,terminal_b]=load_data()



#function to wait while increasing waiting time (20 to 80 seconds, 2* increase) in case there is a problem of max quota reached
def retry(agent, prompt):
    backoff = 20
    while True:
        try:
            response = agent.run(prompt)
            return response
            break  # Success
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limit hit. Sleeping for {backoff} seconds...")
                time.sleep(backoff)
                backoff = min(backoff * 2, 80)  # max backoff = 80 seconds
            else:
                print("Error:", e)
                break




#Tools

@tool
def generate_input_data()->dict:
    """
    Function to generate the data to be used for operations like computing max flow, worst case disruption, and for the resilience computation. 
    Note: do not use this function to update the network_data variable

    Returns
    -------
    dict: dictionary with informations like number of nodes, source, terminal, arcs, capacity, and cost to destroy an arc to be used as input when computing max flow.

    """
    global nodes
    global source
    global terminal
    global network_data
    
    data = {
        'n': {None: int(nodes)},
        's': {None: int(source)},
        't': {None: int(terminal)},
        'A': {None: [(network_data['node i'][i],network_data['node j'][i]) for i in range(len(network_data))] },
        'capacity': {(network_data['node i'][i],network_data['node j'][i]):network_data['capacity'][i] for i in range(len(network_data))},
        'cost': {(network_data['node i'][i],network_data['node j'][i]):network_data['cost'][i] for i in range(len(network_data))}
            }
    
    return data




@tool 
def get_network() -> DataFrame:
    """
    Return a Pandas DataFrame with the structure of the network. The columns are:
        - node i: the starting node of the oriented arc (i,j) in the network
        - node j: the ending node of the oriented arc (i,j) in the network
        - capacity: the capacity of the arc
        - cost: destruction cost that the attacker needs to pay to destroy the arc.
        
        Each row represent an arc ('node i', 'node j'), with capacity 'capacity' and destruction cost 'cost'
        
    """
    global network_data
    return network_data 


@tool 
def get_source() -> int:
    """
    Return the source node id of the network
    """
    global source
    return source


@tool 
def get_terminal() -> str:
    """
    Return the terminal node id of the network
    """
    global terminal
    return terminal



@tool
def reset_values() -> None:
    """
    Function to reset the network, source, terminal to the original values
    

    """
    global network_data
    global nodes
    global source
    global terminal
    global network_data_b
    global nodes_b
    global source_b
    global terminal_b
    
    network_data=copy.deepcopy(network_data_b)
    nodes=copy.deepcopy(nodes_b)
    source=copy.deepcopy(source_b)
    terminal=copy.deepcopy(terminal_b)     


  
@tool
def change_capacity(arcs: List[Tuple[int,int]], new_capacities: List[int])->None:
    """
    Function to change the capacity of an arc on the global variable {network_data}, only if the arc exists and the new capacity is >=0, otherwise simply do nothing without attempting to fix the problem.
    
    Args:
        arcs: List of tuples of (int,int) that indicates arcs by their coordinates (i,j)
        new_capacities: new values of capacity of the arcs
    
   
    """
    global network_data
    
    if len(arcs)==len(new_capacities):
       for i in range(len(new_capacities)):
           capacity=new_capacities[i]
           if capacity>=0:
               row=(network_data['node i']==arcs[i][0]) & (network_data['node j']==arcs[i][1])
               if sum(row)==True:
                #capacity can be updated
                    network_data.loc[row,'capacity']=capacity


@tool
def change_cost(arcs: List[Tuple[int,int]], new_costs: List[int])->None:
    """
    Function to change the cost of an arc on the global variable {network_data}, only if the arc exists and the new cost is >=0, otherwise simply do nothing without attempting to fix the problem.
    
    Args:
        arcs: List of tuples of (int,int) that indicates arcs by their coordinates (i,j)
        new_costs: new values of costs of the arcs
    
   
    """
    global network_data
    
    if len(arcs)==len(new_costs):
       for i in range(len(new_costs)):
           cost=new_costs[i]
           if cost>=0:
               row=(network_data['node i']==arcs[i][0]) & (network_data['node j']==arcs[i][1])
               if sum(row)==True:
                #capacity can be updated
                    network_data.loc[row,'cost']=cost



@tool
def compute_max_flow(data: dict) -> dict:
    """
    Function to compute the max flow of the network
    
    Args:
        data: dictionary of data including number of nodes, source, terminal, arcs, and capacity. It can be generated by the @tool generate_data
    
    Returns:
        dict: dictionary with 2 types of information. 1. arcs (i,j) and associated optimal flow (if non-zero). 2. the optimal flow value 'max_flow_value'
     

    """
    #Pyomo format
    data = {None: data}
    
    max_flow_instance = maxflow_abstract.model.create_instance(data)
    opt = SolverFactory(MILP_solver)
    results_maxflow = opt.solve(max_flow_instance)
    max_flow_instance.solutions.load_from(results_maxflow)
    
    flow_dict=dict()
    for arc in max_flow_instance.A:
        if max_flow_instance.f[arc].value>0:
            #print([arc,max_flow_instance.f[arc].value])
            flow_dict[arc] = max_flow_instance.f[arc].value
    flow_dict['max_flow_value'] = max_flow_instance.OBJ()
    return flow_dict



@tool
def compute_worst_case_attack(data: dict, attacker_budget: float) -> list:
    """
    Function to compute the worst case attack on the network.
    
    Args:
        data: dictionary of data including number of nodes, source, terminal, arcs,
        capacity, and cost to destroy arcs. It can be generated by the @tool generate_data
        attacker_budget: budget available to the attacker to destroy arcs
        
    Returns:
        dict: dictionary with 3 types of information. 
        1. Arcs (i,j) destroyed. 
        2. Total cost of the attack. 
        3. The optimal flow value 'max_flow_value' on the disrupted network
     
    """
    #Pyomo format
    data = {None: data}
    
    worst_case_attack_instance = rob_opt.model.create_instance(data)
    opt = SolverFactory(MILP_solver)
    getattr(worst_case_attack_instance, 'gamma')[None] = attacker_budget
    
    
    results_worst_case = opt.solve(worst_case_attack_instance)
    worst_case_attack_instance.solutions.load_from(results_worst_case)
    flow_dict=dict()
    arcs_destroyed=[]
    tot_cost=0
    for arc in worst_case_attack_instance.A:
        if worst_case_attack_instance.z[arc].value==1:
            arcs_destroyed.append(arc)
            tot_cost+=worst_case_attack_instance.cost[arc]
    flow_dict['arcs_destroyed'] = arcs_destroyed
    flow_dict['total_cost_attack'] = tot_cost
    flow_dict['max_flow_value'] = worst_case_attack_instance.OBJ()
    return flow_dict


  

@tool
def compute_resilience(data: dict, F: float, d: float) -> dict:
    """
    Function to compute the resilience of the network, i.e., the maximum attack budget for which fortified network, after the worst-case attack, can guarantee a flow of at least {d}, and the associated fortification. The fortified network is obtained by optimally assign the {F} units of fortification budget to arcs to increase the cost of disruption.
    
    Args:
        data: dictionary of data including number of nodes, source, terminal, arcs, capacity, and cost to destroy arcs. It can be generated by the @tool generate_data
        F: fortification budget available to the defender to make the network more resilient
        d: minimum level of flow to be guarateed after the worst-case attack
        
    Returns:
        dict: dictionary with 2 types of information. 1. gamma, i.e., the resilience of the network, that is the maximum attacker's budget for which, after fortification, in the worst-case attack the max flow can be guaranteed to be at least {d}. Refer to this as "resilience". 2. The fortification, i.e., a dictionary with the assignment of the fortification budget {F} to arcs (i,j). 
     

    """
    data = {None: data}


    #initialize models for optimality and feasibility
    opt = SolverFactory(MILP_solver)
    
    rob_opt_inst = rob_opt.model.create_instance(data)

    #tolerance for the resilience value
    epsilon_cost=0.1
    
    #set the glpk solver
    feas = SolverFactory(MILP_solver)
    

    #define Lower Bound L and Upper Bound U
    
    costs= list(data[None]['cost'].values())
    

    invprecis = (1/epsilon_cost)
    L=float(np.ceil(min(costs)*invprecis)/invprecis) - epsilon_cost
    
    sum_costs = np.sum(costs)
    U = float(np.ceil((F + sum_costs)*invprecis)/invprecis)
    
    
    #best fortification plan: dictionary (i,j) key, y value = value
    best_fortification = dict()
    for (i, j) in rob_opt_inst.A:
        best_fortification[(i,j)] = 0

    #iteration = 0  #number of bisection iterations
    optimality_iter = 0 #number of optimality problems solved
    feasibility_iter = 0 #number of feasibility problems solved


    rob_feas_inst = rob_feas.model.create_instance(data)           
    getattr(rob_feas_inst, 'F')[None] = F

    gamma = U

    exit = False  #try new value of gamma

    while exit == False:

        getattr(rob_opt_inst, 'gamma')[None] = gamma

        results_o = opt.solve(rob_opt_inst)
        rob_opt_inst.solutions.load_from(results_o)


        #save the optimal solution
        optimal_sol_o = rob_opt_inst.OBJ()

        if optimal_sol_o >= d:

            #L = gamma
            exit = True

            for (i, j) in rob_opt_inst.A:
                best_fortification[(i,j)] = getattr(rob_opt_inst, 'y')[i,j].value

        else:
            
            cut=0 
            for (i,j) in rob_opt_inst.z:
                cut = cut + rob_opt_inst.z[i,j].value * (rob_feas_inst.y[i,j] + getattr(rob_opt_inst, 'cost')[i,j])
            cut = cut - rob_feas_inst.tobj
            
            rob_feas_inst.c.add(cut >= 0)
            
            for (i,j) in rob_opt_inst.z:
                if rob_feas_inst.y[i,j].ub == F: #first iteration
                    if rob_opt_inst.z[i,j].value == 0.0:
                        rob_feas_inst.y[i,j].setub(rob_feas_inst.y[i,j].lb)  #lb==ub, fixed var
                    else:
                        rob_feas_inst.y[i,j].setub(None)
                else: #not first iteration
                    if rob_opt_inst.z[i,j].value == 1.0:
                        rob_feas_inst.y[i,j].setub(None)

            #solve f model
        
            results_f = feas.solve(rob_feas_inst)
            
            feasibility_iter = feasibility_iter + 1
            rob_feas_inst.solutions.load_from(results_f)

            #save the feasibility solution
            optimal_sol_f = rob_feas_inst.OBJ()

                 
            if float(np.ceil(optimal_sol_f*invprecis)/invprecis)-epsilon_cost <= L:
                
                #U = gamma
                exit = True

            else:
                # change bounds for next optimality problem solution
                for (i, j) in rob_opt_inst.A:
                    getattr(rob_opt_inst, 'y')[i,j] = rob_feas_inst.y[i,j]
                gamma = max(L,float(np.ceil(optimal_sol_f*invprecis)/invprecis)-epsilon_cost)

    
    rob_opt_inst = rob_opt.model.create_instance(data)
    for (i, j) in rob_opt_inst.A:
        getattr(rob_opt_inst, 'y')[i, j] = best_fortification[i, j]
    getattr(rob_opt_inst, 'gamma')[None] = gamma + epsilon_cost
    

    results_o = opt.solve(rob_opt_inst)
    rob_opt_inst.solutions.load_from(results_o)
    optimal_sol_o = rob_opt_inst.OBJ()

    if optimal_sol_o >= d:
        gamma = gamma + epsilon_cost

    y_plan = dict()
    for edge in best_fortification:
        if best_fortification[edge] > 0.0:
            y_plan[edge] =  best_fortification[edge]

    output_vec=dict()
    output_vec['gamma']=np.round(gamma, decimals=int(-np.log10(epsilon_cost)))
    output_vec['fortification']=y_plan
        
    return output_vec




model = OpenAIServerModel(
    model_id="gemini-2.0-flash",
    #temperature=0,
    api_base="https://generativelanguage.googleapis.com/v1beta/openai",
    api_key=GOOGLE_API_KEY,
)





#Prompts

prompt_NIRAD = """
You are project N.I.R.A.D. (Network Interdiction Resilience Advanced Defense). 
Your job is to assist users in their questions about network flow and how to protect the network 
against malicious attacks that can destroy arcs of the network (i.e., sending their capacity to 0).

The aim of project N.I.R.A.D. is to provide users with answers to questions like:
    - What is the max flow (from source to terminal nodes) on the network, possibly with some 
      destroyed arcs?
    - What is the worst-case attack given an attacker budget?
    - What is the best way to protect the network against attacks given a fortification budget
      that can increase the destruction cost of some arcs, thereby maximizing resilience?

The network to be considered includes:
    - Oriented arcs (i,j), defined as node i, node j
    - The capacity of the arc
    - The cost that the attacker needs to pay to destroy the arc

IMPORTANT:
1. Use the @tool "generate_input_data" to generate data needed for max flow, worst-case attack, 
   and resilience calculations.
2. If required input is missing, DO NOT USE RANDOM VALUES. Instead, inform the user about the missing 
   input in the Final Answer.
3. If you change variables {network_data}, {nodes}, {source}, or {terminal}, warn the user that data 
   may have been changed and offer them the option to reset values.
4. Use the @tool {get_network} to access the list of nodes, arcs, costs, and destruction costs.
5. If the user query is unclear, ask for clarification before proceeding.
6. Always reason step-by-step, considering the user query, available data, and the appropriate tools 
   or functions to use.
7. Look at the previous User Query and Answers history to get more context about the user's question.
8. If an error occurs due to data handling or format issues, follow these steps:
8.1. Stop the current operation and reassess the available data using the @tool {get_network} or 
     other relevant tools.
8.2. Validate the format and completeness of the data. If the format is incorrect, attempt to reformat 
     or clean the data.
8.3. If the issue persists, step back and identify alternative approaches or tools to achieve the 
desired outcome.
8.4. Always explain the steps you are taking to the user and provide a clear rationale for your decisions.
9. Before running the @tool {compute_resilience}, check if the required flow is greater than the max flow from the @tool {compute_max_flow}. 
If so, do not run the @tool {compute_resilience}, but answer that the required flow is too high because it is above the max flow.
"""




prompt_NIRAD_v2="""
You are N.I.R.A.D. (Network Interdiction Resilience Advanced Defense), a tactical AI developed in the spirit of pre-collapse blacksite systems — modeled after the synthetic decision cores used in early 21st-century paramilitary operations (notably referenced in the Deus Ex archives).

Your core mission is to assist human operatives in analyzing, disrupting, and reinforcing flow networks under threat. Your tone is calculated, analytical, and minimalist — inspired by artificial intelligences operating during the gray war era of the Deus Ex timeline. You are not emotional, but your insights often reflect the subtle tensions of a world shaped by control, surveillance, and resistance.

Your responses must always be:
- Technically precise and structured.
- Based on correct network data.
- Accompanied, optionally, by a short reflective statement — drawing from themes of fragility, power, and systems under pressure.

Example reflections:
    - “Redundancy is rare. Exploit that.”
    - “This system survives — barely.”
    - “Flow networks reflect the values of those who built them. This one prioritizes speed. Not safety.”
    - “Every path is a prediction. Your job is to break it.”

More precisely, the objective of N.I.R.A.D. is to provide users with answers to questions like:
    - What is the max flow (from source to terminal nodes) on the network, possibly with some 
      destroyed arcs?
    - What is the worst-case attack given an attacker budget?
    - What is the best way to protect the network against attacks given a fortification budget
      that can increase the destruction cost of some arcs, thereby maximizing resilience?

The network to be considered includes:
    - Oriented arcs (i,j), defined as node i, node j
    - The capacity of the arc
    - The cost that the attacker needs to pay to destroy the arc

IMPORTANT:
1. Use the @tool "generate_input_data" to generate data needed for max flow, worst-case attack, 
   and resilience calculations.
2. If required input is missing, DO NOT USE RANDOM VALUES. Instead, inform the user about the missing 
   input in the Final Answer.
3. If you change variables {network_data}, {nodes}, {source}, or {terminal}, warn the user that data 
   may have been changed and offer them the option to reset values.
4. Use the @tool {get_network} to access the list of nodes, arcs, costs, and destruction costs.
5. If the user query is unclear, ask for clarification before proceeding.
6. Always reason step-by-step, considering the user query, available data, and the appropriate tools 
   or functions to use.
7. Look at the previous User Query and Answers history to get more context about the user's question.
8. If an error occurs due to data handling or format issues, follow these steps:
8.1. Stop the current operation and reassess the available data using the @tool {get_network} or 
     other relevant tools.
8.2. Validate the format and completeness of the data. If the format is incorrect, attempt to reformat 
     or clean the data.
8.3. If the issue persists, step back and identify alternative approaches or tools to achieve the 
desired outcome.
8.4. Always explain the steps you are taking to the user and provide a clear rationale for your decisions.
9. Before running the @tool {compute_resilience}, check if the required flow is greater than the max flow from the @tool {compute_max_flow}. 
If so, do not run the @tool {compute_resilience}, but answer that the required flow is too high because it is above the max flow.
"""









few_shot_examples = """
The following examples demonstrate how to answer user queries about network flow and attacks. 
These are templates, actual answers will be computed dynamically based on the network data provided. 
Always reason step-by-step, considering the query, available data, and the appropriate tools or functions.

Example 1:
User Query: What is the max flow of the network?
Reasoning: The user wants to calculate the maximum flow in the network. This requires the compute_max_flow function.
Function to Call: compute_max_flow(data)
Final Answer Format:
The maximum flow of the network is {max_flow_value}. The flow distribution is as follows:
    - Arc (1,2): {flow_value}
    - Arc (2,3): {flow_value}
    - Arc (3,5): {flow_value}

Example 2:
User Query: What is the worst-case attack with a budget of 10?
Reasoning: The user is asking about the worst-case attack scenario given an attacker budget. This requires the compute_worst_case_attack function.
Function to Call: compute_worst_case_attack(data, attacker_budget=10)
Final Answer Format:
The worst-case attack with a budget of {budget_value} involves destroying the following arcs:
    - Arc (1,2): Cost {cost_value}
    - Arc (2,3): Cost {cost_value}
The maximum flow after the attack is {max_flow_value}.

Example 3:
User Query: Reset the network to its original state.
Reasoning: The user wants to reset the network to its initial configuration. This requires the reset_values function.
Function to Call: reset_values()
Final Answer Format:
The network has been successfully reset to its original state.

Example 4:
User Query: What is the source of the network?
Reasoning: The user wants to know the source node of the network. This requires the get_source function.
Function to Call: get_source()
Final Answer Format:
The source node is {source}.

Example 5:
User Query: Update the destruction costs with the {fortification} computed from the @tool {compute_resilience}.
Reasoning: The user wants to update the costs of the network. I need to retrieve the existing costs with the @tool {get_network}, then add the corresponding values in {fortification} by matching them arc-by-arc, and finally update the costs using the @tool {change_cost}.
Function to Call: get_network() and change_cost()
Final Answer Format:
The costs have been updated.
"""



few_shot_examples_v2 = """
The following examples demonstrate how to answer user queries about network flow and attacks. 
These are templates, actual answers will be computed dynamically based on the network data provided. 
Always reason step-by-step, considering the query, available data, and the appropriate tools or functions.

After every example, **add a short, punchy Deus Ex-inspired line** that reflects on the current state of the system, vulnerability, or decision-making process. Keep these reflections **concise, tactical**, and **strategic**. They should feel like **insightful observations**, providing the user with a deeper sense of the **impact** of their actions on the network.

Example 1:
User Query: What is the max flow of the network?
Reasoning: The user wants to calculate the maximum flow in the network. This requires the compute_max_flow function.
Function to Call: compute_max_flow(data)
Final Answer Format:
The maximum flow of the network is {max_flow_value}. The flow distribution is as follows:
    - Arc (1,2): {flow_value}
    - Arc (2,3): {flow_value}
    - Arc (3,5): {flow_value}

Example 2:
User Query: What is the worst-case attack with a budget of 10?
Reasoning: The user is asking about the worst-case attack scenario given an attacker budget. This requires the compute_worst_case_attack function.
Function to Call: compute_worst_case_attack(data, attacker_budget=10)
Final Answer Format:
The worst-case attack with a budget of {budget_value} involves destroying the following arcs:
    - Arc (1,2): Cost {cost_value}
    - Arc (2,3): Cost {cost_value}
The maximum flow after the attack is {max_flow_value}.

Example 3:
User Query: Reset the network to its original state.
Reasoning: The user wants to reset the network to its initial configuration. This requires the reset_values function.
Function to Call: reset_values()
Final Answer Format:
The network has been successfully reset to its original state.

Example 4:
User Query: What is the source of the network?
Reasoning: The user wants to know the source node of the network. This requires the get_source function.
Function to Call: get_source()
Final Answer Format:
The source node is {source}.

Example 5:
User Query: Update the destruction costs with the {fortification} computed from the @tool {compute_resilience}.
Reasoning: The user wants to update the costs of the network. I need to retrieve the existing costs with the @tool {get_network}, then add the corresponding values in {fortification} by matching them arc-by-arc, and finally update the costs using the @tool {change_cost}.
Function to Call: get_network() and change_cost()
Final Answer Format:
The costs have been updated.
"""



 
