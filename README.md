# KGPSociety_Interview_Scheduling
An interview scheduling solution made using metaheuristics for societies of KGP, firstly made for MASK.

# Problem Statement
## Problem statement which started this

This problem was thought of after inefficient allocations in interviews for the batch 2024-25, but since the problem was not solved, we faced similar issues along with some new issues all except re-scheduling capable of being solved with a simple optimisation and constraint satisfaction program.

The problem statement was then solved by me in a little sandbox which was iteratively solved and standardised and made formal.

Here's the formal problem statment which describes a general framework along with specifics of MASK highlighted so that suitable changes can be made easily.

[Formal Problem Statement](/ProblemStatement_MASK.md)

# Running
## Setup
1. Make sure **python** and **git** are installed
2. If you're using virtual environments, it is recommended to use `uv`, otherwise create a venv in the cloned directory adding packages `deap>=1.4.4` and `numpy>=2.4.6`
3. Clone the repo and change directory to the cloned folder.
4. If using `uv`, run 
    ```bash
    uv sync
    ```
    Note that it is not needed to run `uv init` as it usually thought

    Otherwise, setup virtual environment as described in 2

    Else, do `pip install deap numpy` if you're fine with global.
## Setting up problem
Read the [problem statement](/ProblemStatement_MASK.md) before editing any files.

You would have to change/create 3 files,

1. Interviewers CSV
2. Candidates CSV
3. Availability CSV

### Interviewers and Candidates
Rules for making the CSVs is same for both Interviewers and Candidates. Just the IRL meaning is different.

1. The python file reading the csv is set to **ignore any empty line or lines starting with `##`**.
2. First line is ignored and hence header row is compulsory.
3. The first field is name.
4. If the name is supposed to have comma, keep the name in double quotes (`""`), this is automatically done when you download as csv from Google Sheets or export an xlsx as csv in Excel.
5. Anything after name is used for getting the teams (applied for candidates, qualified for interviewers)
6. The teams may be any of the following formats (each row is an example of a valid row format)

    |name| teams| | | 
    | --- | --- | --- | ---|
    |Ananda | A,B,C | |
    | Bhaskara | D, E, F|
    | Chandragupta | G | H | I
    | Dushyanta | J,K | L, M| N

    For Ananda, all teams are put with commas without space, whereas for Bhaskara, there were spaces
    
    For Chandragupta, one team was put in each cell (not only in the teams column)

    For Dushanta, it is a combination of all 3.

**After changing or making files, update the INTERVIEWERS_CSV and CANDIDATES_CSV paths in `main.py`**

### Availability

**Rules 1, 2, 3, 4 are same as interviewers and candidates**

5. Same name must be used as interviewers csv.
6. All cells in the row after name are used to check for _<ins>inavailability</ins>_. 

    If any cell has anything other than N or n, it is taken that the interviewer is available

#### Example

|name| 1| 2| 3| 
| --- | --- | --- | ---|
|Ananda | | | |
| Bhaskara | Y|Y |N |
| Chandragupta | |N | |
| Dushyanta |Y |Y |A |

1,2,3 are for our help and can be replaced by slot name or slot timings. Here it is slot number.

<ins>Ananda and Dushyanta are available all 3 slots</ins>. Empty is taken as available, so is Y or A.

Bhaskara is not available in 3rd slot, Chandragupta in 2nd slot.

**After changing or making files, update the AVAILABILITY_CSV path in `main.py`**

Have to change behavior that any name of the interviewer if not available in availability csv, it is assumed they are always free.