import random
import numpy as np
from deap import base, creator, tools, algorithms
import collections
import os,pickle, warnings
import csv

# Taking the approach of a Genetic Algorithm (GA) for this since I did a tutorial of solving VRP with GA.
# The individual is a list of tuples of the format (Interviewer1, Interviewer2, Slot) which will be called a gene. This is because the list of candidates is constant.

# Everything about the GA will be explained as the code goes.

# Reading the interview problem from a CSV. Though this is incrediby centric to the MASK problem.
def read_interview_problem(problem_csv_filepath):
    res = dict()
    with open(problem_csv_filepath, "r", newline="") as problem_csv:
        problem_reader = csv.reader(problem_csv)
        next(problem_reader)#Skipping the header always. IMPORTANT. MUST HAVE HEADER.
        for row in problem_reader:
            if row==[] or "##" in row[0]: #Adding commenting feature
                continue
            if len(row) == 1:
                raise Warning("Only 1 field (presumed to be name) present!")
            name = row[0]
            teams = row[1:]
            #Some input handling
            if teams!=[]:
                for ind,val in enumerate(teams[:]):
                    if "," in val: #If the teams were put in one cell this happens
                        del teams[ind]
                        teams.extend(val.split(","))
                teams = [team for team in teams if team.strip()!='']
                for ind,val in enumerate(teams[:]):
                    Val = val.upper().strip()
                    if Val in ["MN"]: teams[ind] = "MN"
                    if Val in ["Q", "QUIZ"]: teams[ind] = "Q"
                    if Val in ["AMV", "ANIME MUSIC VIDEO"]: teams[ind] = "AMV"
                    if Val in ["WEBD", "W", "WEB"]: teams[ind] = "WebD"
                    if Val in ["DNA", "D&A", "DESIGN AND ARTS", "DESIGN & ARTS"]: teams[ind] = "DNA"
                    if Val in ["MUSIC", "M"]: teams[ind] = "Music"

            res[name] = set(teams)
    
    return res

INTERVIEWERS_CSV = "MASK_Scheduling_Interviewers.csv"
CANDIDATES_CSV = "MASK_Scheduling_Candidates.csv"

interviewers_t = read_interview_problem(INTERVIEWERS_CSV)
candidates_t = read_interview_problem(CANDIDATES_CSV)

#This framework of building interviewers and cadidates will allow us to convert the MASK problem to general later
INTERVIEWERS = [{'id': name, 'skills': list(teams)} for name, teams in interviewers_t.items()]
CANDIDATES = [{'id': name, 'applied': list(teams)} for name, teams in candidates_t.items()]

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

toolbox = base.Toolbox()

# GA Weights
GA_WEIGHTS = (-10000.0, -50.0, -20.0, -5.0, -5.0, -1.0)
creator.create("FitnessMin", base.Fitness, weights=GA_WEIGHTS)
creator.create("Individual", list, fitness=creator.FitnessMin)

# A GA is applied onto a the problem by the implementation of the following:
#   Gene and Individual Representation: 
#       1. Creating an individual. An indidual is composed of genes which defines the individual.
#       2. Tweaking an individual. The way individuals are changed. (refer to Metaheristics Essentials)
#           2.1. Mutation. Parent undergoes a change with a small probability and gives child.
#           2.2. Crossover. This means two (or more) individuals combine to create two (or more) individuals sharing genes if their parents.
#       3. Fitness assessment. Finding the fitness (evaluate) of an individual.

# These are implemented for our problem by functions:
#   create_gene, create_individual, custom_mutate, evaluate. We will use builtin Two Point Crossover given by DEAP for the crossover.

# This repo has been made after a lot of coding to get the solution so I will be including key frames of development in the commits. Many improvements will go and then I will then continue the development.

def create_gene():
    #Since the individual is a list of (Interviewer1, Interviewer2, Slot), the gene is a tuple of (Interviewer1, Interviewer2, Slot)
    i1,i2 = sorted(random.sample(range(NUM_INTERVIEWERS), 2))
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

toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
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
    interviewer_schedule=collections.defaultdict(list)
    used_pairs=set()
    
    for c_idx,gene in enumerate(ind):
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
            max_workload = workload
        
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
toolbox.register("evaluate", evaluate)

# Saving and Loading.
#   For GAs, and in general population-based metaheuristics is the ability to optimise taking an nth generation as the initial-population instead of a random population, which lets us run the program for a few generations, see the result, and then run for more if we believe improvement is possible. This is rarely implemented so this was my first use of the concept.

CHECKPOINT_FILE = "MASK_sch_curr_best_pop.dat"

def save_checkpoint(population, filename):
    try:
        with open(filename, "wb") as f:
            pickle.dump(population, f)
        print(f"[Checkpoint] Successfully saved population to {filename}")
    except Exception as e:
        print(f"[Checkpoint] Warning: File existed but failed to load {e}. Starting fresh.")
    return None

def load_checkpoint(filename):
    if not os.path.exists(filename):
        return None
    try:
        if os.path.getsize(filename) > 0:
            with open(filename, "rb") as f:
                pop = pickle.load(f)
                print(f"[Checkpoint] Loaded population of size {len(pop)} from {filename}")
                return pop
    except Exception as e:
        print(f"[Checkpoint] Warning: File existed but failed to load ({e}). Starting fresh.")
    return None

def main():
    POP_SIZE = 400
    NGEN = 150

    pop = load_checkpoint(CHECKPOINT_FILE)
    old_best_fitness_vector = None
    if pop is None:
        print("[Start] No valid checkpoint found. Initializing random population.")
        pop = toolbox.population(n=POP_SIZE)
        # For a fresh run, any result is "better" than nothing
        # We can treat old_best_fitness_vector as None or extremely bad
    else:
        # Evaluate the loaded population immediately (because I don't care if fitness was present in the pickle dump)
        fitnesses = list(map(toolbox.evaluate, pop))
        for ind, fitness in zip(pop, fitnesses):
            ind.fitness.values=fitness
        
        current_best = tools.selBest(pop, 1)[0]
        old_best_fitness_vector = current_best.fitness.values
        print(f"[Start] Best fitness in the loaded file: {old_best_fitness_vector}")
    
    hof = tools.HallOfFame(1)

    # Turns out DEAP gives all individuals an attribute fitness which behaves exactly as applying the WEIGHTS and direction (minimization/maximization of fitness) onto the vector of individual fitnesses
    # If fitness1 > fitness2 then the individual 1 is always better. Even if the problem was minimization, which is our case, it doesn't mean that fitness1 > fitness2 means that after multiplying with weights the value obtained is more for 1. Since the goal is minimisation, lower value would give fitness1 > fitness2.
    # The previous one was comparing vectors which was going in the lexicographic sorting.
    stats = tools.Statistics(lambda ind: ind.fitness)
    stats.register("min", lambda fitnesses: np.max(fitnesses).values)

    print("Starting Evolution...")
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.4, ngen=NGEN,
                                    stats=stats, halloffame=hof, verbose=True)

    best_ind = hof[0]
    scores = evaluate(best_ind)
    new_best_fitness_vector = best_ind.fitness.values

    should_save = False
    if old_best_fitness_vector is None:
        print("\n[Result] First run completed.")
        should_save = True
    else:
        if best_ind.fitness > current_best.fitness:
            print(f"\n[Result] Improvement found! \nOld: {old_best_fitness_vector} \nNew: {new_best_fitness_vector}")
            should_save = True
        elif best_ind.fitness == current_best.fitness:
            print("\n[Result] No improvement (fitness equal). Saving anyway to preserve genetic diversity evolution in population.")
            should_save = True
        else:
            print(f"\n[Result] New generation is worse, (Old: {old_best_fitness_vector} vs New: {new_best_fitness_vector}). NOT updating file.")
            should_save = False
    
    if should_save:
        save_checkpoint(pop, CHECKPOINT_FILE)

    print("\n" + "="*50)
    print("FINAL SCHEDULE METRICS")
    # 1. Hard Penalty. All hard-penalties have same high weight in this context. Hard penalty = Satisfice (of candidate) penalty + Double booking (interviewer) penalty + Venue (overbooking) penalty
# 2. Makespan penalty
# 3. Workload penalty
# 4. Relevance penalty
# 5. Fragmentation penalty
# 6. Unique Panel penalty.

    print("="*70)
    print(f"1. Hard Penalty:                                              {scores[0]} (Target: 0)")
    print(f"2. Makespan Penalty:                                          {scores[1]}")
    print(f"3. Max Workload:                                              {scores[2]}")
    print(f"4. No of interviewers irrelevant to candidate (Relevance):    {scores[3]}")
    print(f"5. Sum of Gaps between interviews of an interviewer:          {scores[4]}")
    print(f"6. No. of Unique Panels:                                      {scores[5]}")
    print("-"*70)
    
    # OUTPUT FORMATTING
    if scores[0] > 0:
        print("WARNING: Hard constraints violated.")
    
    schedule_map = collections.defaultdict(list)
    interviewer_load = collections.defaultdict(int)

    for c_idx, gene in enumerate(best_ind):
        i1, i2, slot = gene
        c_name = CANDIDATES[c_idx]['id']
        i1_name = INT_ID_MAP[i1]
        i2_name = INT_ID_MAP[i2]
        
        # Check relevance for display
        cand_req = set(CANDIDATES[c_idx]['applied'])
        s1 = INT_SKILL_MAP[i1_name]
        s2 = INT_SKILL_MAP[i2_name]
        
        # Tagging strictly relevant interviewers
        i1_tag = "*" if not s1.intersection(cand_req) else ""
        i2_tag = "*" if not s2.intersection(cand_req) else ""
        
        schedule_map[slot].append(f"({c_name}, {i1_name}{i1_tag}, {i2_name}{i2_tag})")
        interviewer_load[i1_name] += 1
        interviewer_load[i2_name] += 1

    sorted_slots = sorted(schedule_map.keys())
    for slot in sorted_slots:
        day = (slot // SLOTS_PER_DAY) + 1
        time_slot = (slot % SLOTS_PER_DAY) + 1
        print(f"\nSlot {slot} (Day {day}, Slot {time_slot}):")
        for entry in schedule_map[slot]:
            print(f"  {entry}")
            
    print("\nNOTE: '*' indicates the interviewer shares no applied skill with the candidate.")
    
    print("\n" + "="*50)
    print("INTERVIEWER WORKLOAD")
    print("="*50)
    sorted_load = sorted(interviewer_load.items(), key=lambda x: x[1], reverse=True)
    for name, load in sorted_load:
        print(f"{name}: {load}")
    
if __name__ == "__main__":
    main()
