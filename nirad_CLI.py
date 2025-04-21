# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 15:08:08 2025

@author: costaal
S.H.I.E.L.D.
"""

import nirad_utils as shu
from smolagents import CodeAgent
import pandas as pd
from colorama import Fore, Back, Style

list_tools=[shu.compute_worst_case_attack, shu.compute_resilience, shu.compute_max_flow, shu.get_network, shu.generate_input_data, shu.change_capacity, shu.change_cost, shu.reset_values]

agent = CodeAgent(tools=list_tools, model=shu.model, additional_authorized_imports=['pandas','io'], max_steps=15, verbosity_level=-1)  #-1 to suppress reasoning steps




#type exit to exit
def main():
    
    prompt=f'{shu.prompt_NIRAD_v2}\n {shu.few_shot_examples_v2}'
    while True:
          print(Fore.GREEN + Style.BRIGHT+"N.I.R.A.D.> Enter your query:"+ Style.RESET_ALL, end="")
     
          user_query = input(Fore.YELLOW +Style.BRIGHT+" "+Style.RESET_ALL)
          if user_query.lower() == "exit":
    
              break
          prompt=f'{prompt}\n User Query: {user_query}' 
          r=shu.retry(agent,prompt)
         
          print(Fore.RED + Style.BRIGHT+"(Answer) "+Style.RESET_ALL+str(r)+"\n")
          prompt=f'{prompt}\n Answer: {r}' 

 
    
     
if __name__ == '__main__': 
    main()  
     