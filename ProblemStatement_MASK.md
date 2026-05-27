A society named MASK exists in KGP which wants to schedule its interview round. Here are the constraints.

### Structure of the society
1. MASK has three levels of hierarchy as far as interviews are concerned. Freshers, associates, and executives.
2. The selections happen for freshers and associates. Associates take interviews for those eligible to be freshers, and executives take interviews for associates candidates.
3. MASK has 5 teams, MN, Quiz, DNA, WebD, and AMV. The names of the teams are hardly relevant for the problem.
4. An interview candidate can apply to any subset of the teams. Each member of the society has their own set of teams they are a part of. The panel for the candidate consists of two interviewers. The triplet of (candidate, interviewer1, interviewer2), makes for an interview. Each interview is assigned a (time)slot. All constraints are to be satified and penalty is to be minimised. This is the interview scheduling problem in context of MASK.
5. The interviews happen in places booked by MASK and such, have a maximum capacity.

### Definitions of constraints:
1. Hard Constraints (Hard Penalty): The constraints which when violated make the solution (schedule) infeasible are called hard constraints. These take highest priority in the solution.
2. Soft Constraints (Soft Penalty): The constraints whose minimisation to any extent improves a solution according to the need are called soft constraints.

### The Constraints
It should be noted that the constraints are being framed as generally as possible to be applied on any structure even if not MASK. For example, it will not be implied that each candidate is interviewed by 2 interviewers, and is generalised for any number of interviewers. The implementation may, however, have specifics.

1. Each team in the set of teams applied by the candidate must be present in atleast one of the interviewers' set of teams. i.e. Union of set of teams of interviewers must be a superset (or equal) of the set of teams the candidate has applied to. HARD CONSTRAINT.
    
    This will be referred to as satisfice of teams.
2. At any (time)slot, no interviewer can occupy more than one interview parallely. HARD CONSTRAINT.
    
    This will be referred to as double booking penaly.
3. At any (time)slot, the number of interviews taking place must not exceed the maximum allowed interviews by the venue. HARD CONSTRAINT.
    
    This will be referred to as venue penalty.
4. An interviewer cannot have an interview in a slot where he declares his inavalability. HARD CONSTRAINT.
    
    This will be referred to as inavailability penalty.
5. It is preferred for the interviews to finish in the least time possible and as earl
y as possible. SOFT PENALTY.
    
   This will be referred to as "Makespan" penalty.
6. It is preferred that each interviewer shares a "fair" amount of workload. For now, we say that the maximum number of interviews being conducted by a member should be minimised.
    
    This will be referred to as "Workload" penalty.
7. It is preferred that all interviewers share atleast one team with the candidate. SOFT PENALTY.
    
    This will be referred to as "Relevance" penalty.
8. It is preferred that all interviews for a certain interviewer be done in a continuous strech. i.e. the gaps between the interviews for an interviewer should be minimised.
    
    This will be referred to as "Fragmentation" penalty
9. Interviewers may have a tendency to conduct interviews with the same co-interviewers. So the number of unique-sets of interviewers can be minimised. SOFT PENALTY. 

    This is not a penalty we will look to much but is presented as it was given in a literature I was reading. This is called the "Unique Panels" penalty. Kinda not-obvious from name.

20. 
    More constraints to be added further.