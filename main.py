import random
import numpy as np
from deap import base, creator, tools, algorithms
import collections

# Taking the approach of a Genetic Algorithm (GA) for this since I did a tutorial of solving VRP with GA.
# The indidivual is a list of tuples of the format (Interviewer1, Interviewer2, Slot) which will be called a gene. This is because the list of candidates is constant.

# Everything about the GA will be explained as the code goes.

# Here's a preliminary data from MASK 2024. This is quite inaccurate because it listed only freshers who were selected, but the associates involve existing members and selected members.
assocs_t = {'Priyanshu Verma': {'DNA'}, 'Satadru Sen': {'Music'}, 'Ajayendra Kumar Bansod': {'WebD'}, 'Pratyush Parth': {'Music', 'MN'}, 'Arghadeep Ghosh': {'DNA', 'MN'}, 'Krishna Chaitanya Terlapu': {'DNA'}, 'Aditya Sharma': {'Q'}, 'Mourya Grandhi': {'WebD'}, 'Pranali Patil ': {'DNA'}, 'Pratyay Ganguly': {'WebD'}, 'Argha Sarkar': {'AMV'}, 'Swadhin Kumar Behera': {'DNA'}, 'Aaryan Singh': {'WebD'}, 'Souradeep Das': {'Q', 'MN'}, 'Shubham Bairagi': {'DNA', 'AMV'}, 'Anamika': {'DNA'}, 'Animesh Raj': {'WebD'}, 'Arnab Jena': {'WebD', 'MN'}, 'Aron Chacko Alan': {'AMV', 'Q'}, 'Binaya Kumar Naik': {'WebD', 'MN'}, 'Dalli Manideep': {'WebD', 'Q', 'MN'}, 'Devangan Mukherjee': {'Q'}, 'Jeffrey Samuel': {'WebD'}, 'Laxmi Kant Jorwal': {'DNA'}, 'Moyili Sneha Satwika': {'DNA'}, 'Nayandeep Deb': {'WebD', 'Q', 'MN'}, 'Ponnapati Thanush Reddy': {'DNA', 'Q'}, 'Rashmi Dinkar Patil': {'DNA', 'MN'}, 'Rishabh Dehariya': {'MN'}, 'Rishith Prabhat': {'MN'}, 'Rohan Prakash Sahu': {'MN'}, 'Shehryaar Shah Khan': {'Q'}, 'Swaraj Dian': {'DNA', 'Q'}, 'Tridibesh Sarkar': {'DNA'}, 'Trishna Das': {'DNA'}, 'Varun Ponnekanti': {'MN'}, 'Vasa Harish': {'DNA'}, 'Viswasarathi N M': {'DNA'}}
freshers_t = {'Anuj Mangaj': {'AMV'}, 'Nivedhitha Somasundaram': {'AMV', 'Q'}, 'Sarthak Jhanwar': {'Q'}, 'Uday Kalyan S': {'WebD'}, 'Bakka Veera Brahma Reddy': {'AMV'}, 'Parandhaman Gokul': {'DNA'}, 'Arnav Gawade': {'Q'}, 'Garv Kumar': {'MN'}, 'Gokul Vemuri': {'Q'}, 'Seeram Rama Prajval': {'Q'}, 'Afrin Munshi': {'MN'}, 'Ayush Thawkar': {'MN'}, 'Tadi Joshua Raj ': {'WebD'}, 'Arul Rana': {'MN', 'Q'}, 'Angshuman Acharya': {'DNA', 'Q'}, 'Rudresh Mohapatra': {'DNA'}, 'Akshara Muralikrishnan': {'MN', 'Q'}, 'Himanshu Kumar': {'DNA'}, 'Bhumi Garg ': {'Music'}, 'Pratibha Shakya ': {'DNA'}}

#This framework of building interviewers and cadidates will allow us to convert the MASK problem to general later
INTERVIEWERS = [{'id': name, 'skills': list(teams)} for name, teams in assocs_t.items()]
CANDIDATES = [{'id': name, 'applied': list(teams)} for name, teams in freshers_t.items()]

INT_ID_MAP = {i: iv['id'] for i, iv in enumerate(INTERVIEWERS)}
INT_SKILL_MAP = {iv['id']: set(iv['skills']) for iv in INTERVIEWERS}
NUM_INTERVIEWERS = len(INTERVIEWERS)
NUM_CANDIDATES = len(CANDIDATES)

#The problem specific constraints, taken from 2024 data. We had booking of 3 days, each day we had 4 hours, and in each hour we can conduct approx 3 interviews so it would be 12. But a bit of approximation here and there.
DAYS = 2
SLOTS_PER_DAY = 10
TOTAL_SLOTS = DAYS * SLOTS_PER_DAY
MAX_PARALLEL_INTERVIEWS = 5

# Deap configuration
# The fitness is a weighted sum of the penalties listed in the problem statement.
# 1. Hard Penalty. All hard-penalties have same high weight in this context. Hard penalty = Satisfice (of candidate) penalty + Double booking (interviewer) penalty + Venue (overbooking) penalty
# 2. Makespan penalty
# 3. Workload penalty
# 4. Relevance penalty
# 5. Fragmentation penalty
# 6. Unique Panel penalty.

# GA Weights
GA_WEIGHTS = (-10000.0, -50.0, -20.0, -5.0, -5.0, -1.0)
creator.create("FitnessMin", base.Fitness, weights=GA_WEIGHTS)
creator.create("Individual", list, fitness=creator.FitnessMin)

# A GA is applied onto a the problem by the implementation of the following:
#   Gene and Individual Representation: 
#       1. Creating an Indidivual. An indidual is composed of genes which defines the individual.
#       2. Tweaking an individual. The way indidividuals are changed. (refer to Metaheristics Essentials)
#           2.1. Mutation. Parent undergoes a change with a small probability and gives child.
#           2.2. Crossover. This means two (or more) indidivuals combine to create two (or more) individuals sharing genes if their parents.
#       3. Fitness assessment. Finding the fitness (evaluate) of an individual.

# These are implemented for our problem by functions:
#   create_gene, create_individual, custom_mutate, evaluate. We will use builtin Two Point Crossover given by DEAP for the crossover.

# This repo has been made after a lot of coding to get the solution so I will be including key frames of development in the commits. Many improvements will go and then I will then continue the development.

def create_gene():
    #Since the individual is a list of (Interviewer1, Interviewer2, Slot), the gene is a tuple of (Interviewer1, Interviewer2, Slot)
    i1,i2 = sorted(random.sample(range(INTERVIEWERS), 2))
    slot = random.randint(0, TOTAL_SLOTS-1)
    return [i1,i2,slot]

def create_individual():
    return [create_gene() for _ in range(NUM_CANDIDATES)]

def custom_mutate(ind, indpb):
    for i in range(len(ind)):
        if random.random() < indpb:
            if random.random() < 0.5:
                ind[i][2] = random.randint(0, TOTAL_SLOTS - 1)
            else:
                ind[i][0], ind[i][1] = sorted(random.sample(range(NUM_INTERVIEWERS), 2))
    return ind,

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", custom_mutate, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

def evaluate(ind):
    #Literal penalties
    hard_penalty=0
    candidate_satisfice_penalty=0
    double_booking_penalty=0
    venue_penalty=0
    makespan_penalty=0
    workload_penalty=0
    relevance_penalty=0
    fragmentation_penalty=0
    unique_panel_penalty=0

    #Helpers to define the penalties
    max_slot_used=min_slot_used=0
    max_workload=0 #workload_penalty is actually literally that the maxiumum worload be minimised so workload_penalty = max_workload

    #Objects made during the process of evaluation.
    slot_usage=collections.defaultdict(int)
    interviewer_schedule=collections.defaultdict(int)
    used_pairs=set()
    
    for c_idx,gene in enumerate(indidivual):
        i1, i2, slot = gene
        cand = CANDIDATES[c_idx]
        req_skills = set(cand['applied'])
        
        #Get Interviewers' skills
        s1 = INT_SKILL_MAP[INT_ID_MAP[i1]]
        s2 = INT_SKILL_MAP[INT_ID_MAP[i2]]

        if not req_skills.issubset(s1.union(s2)):
            candidate_satisfice_penalty += 1
        
        if not s1.intersection(req_skills):
            relevance_penalty += 1
        if not s2.intersection(req_skills):
            relevance_penalty += 1
        
        slot_usage[slot] += 1
        interviewer_schedule[i1].append(slot)
        interviewer_schedule[i2].append(slot)
        used_pairs.add((i1,i2))

        if slot > max_slot_used:
            max_slot_used  = slot
        if slot < min_slot_used:
            min_slot_used = slot

    for i_idx, slots in interviewer_schedule.items():
        unique_slots = sorted(list(set(slots)))
        if len(slots)!= len(unique_slots):
            double_booking_penalty += len(slots) - len(unique_slots)
        
        workload = len(unique_slots)
        if workload > max_workload:
            max_workload = count
        
        if len(unique_slots) > 1:
            for k in range(len(unique_slots)-1):
                gap = unique_slots[k+1] - unique_slots[k] -1
                if gap > 0:
                    fragmentation_penalty += gap
    
    for slot, count in slot_usage.items():
        if count > MAX_PARALLEL_INTERVIEWS:
            venue_penalty += (count - MAX_PARALLEL_INTERVIEWS)
    unique_panel_penalty += len(used_pairs)

    #Using the helpers
    hard_penalty = candidate_satisfice_penalty + double_booking_penalty + venue_penalty
    makespan_penalty = max_slot_used-min_slot_used
    workload_penalty = max_workload
    return (hard_penalty, makespan_penalty, workload_penalty, relevance_penalty, fragmentation_penalty, unique_panel_penalty)

def main():
    print("Hello from kgpsociety-interview-scheduling!")


if __name__ == "__main__":
    main()
