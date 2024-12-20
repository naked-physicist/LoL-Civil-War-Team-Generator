# LoL-Civil-War-Team-Generator
Team composition generator for League of Legends (LoL) with friends

It works as the MMR (Match Making Rating) system used in LoL, but in a much simpler way

You can divide 1-5 positions into Main/Secondary/Tertiary position categories according to your adeptness

You should input AT LEAST one lane for the Main position

Copy and paste the python code and execute it with your own IDE (current version is being developed with Jupyter notebook)



--Rank points--

iron = 1,
bronze = 2,
silver = 3,
gold = 4,
platinum = 5,
emerald = 6,
diamond = 7,
master = 8,
grand master = 9,
challenger = 10

(Ensure that the rank inputs are the most recent solo rank tier)

High-skill server bonus = +1.0

(for Korea/China servers according to recent LoL Worlds results)

Order capability bonus = +0.5

(for object control/lane distribution/team fight order capabilities)

Penalties for secondary/tertiary positions = -0.5/-1.0 respectively

Synergy bonus for average team score = \sqrt{average team score}



--Metrics for team evaluation--

1. Total-points difference metric (T-metric):
Difference between the sums of each team's points = |Blue team total points - Red team total points|

2. Lane-points difference metric (L-metric):
Root-mean-square of each lane's difference in points = \sqrt{ ((top-points difference)^2 + ... + (sup-points difference)^2)/5 }

Ideally, these two metrics should be zero for balanced team making



--Composition system--

The players who have the least number of available positions are assigned to their lane first

And then remaining positions are filled with the players who can go more lanes.



--Team composition results--

Results are shown with the two metrics

Sorting priority is given to T-metric and then L-metric

Red and Blue teams are randomly assigned



### To do list:
Main version
- [x] Save/Open buttons for player list (for frequently involved players)
- [x] Previous/Next page buttons for recommended team compositions
- [x] Calculating L-metric without the 'order capable' bonus point
- [ ] *.exe file for users who don't have python.

Advanced version
- [ ] Rank points derived from Gaussian distribution
- [ ] Weights for 'order capable' bonus point for different ranks/positions
- [ ] Champion pool points - Large(more than 5 champs)/Medium(3-4)/Small(1-2) for each lane
- [ ] Connection to Riot API and Discord

