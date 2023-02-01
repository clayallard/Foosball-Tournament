#!/usr/bin/env python
import argparse
import os
import pickle
from pathlib import Path

import random
# import numpy as np
from itertools import combinations
# from bracket import bracket
from tkinter import *
from tkinter import ttk
# import pandas as pd
# from tabulate import tabulate
# from IPython.display import clear_output
import statistics
import math

# make sure we're working in the directory this file lives in,
# for imports and for simplicity with relative paths
os.chdir(Path(__file__).parent.resolve())

class Tournament:
    __rankings__ = dict()
    __player_seed__ = dict()
    __round_num__ = 0
    __rounds__=[]
    __played_singles__=set()
    __cycle__=1
    __print__=False
    __teams__=None
    __updated__=False

    class Match:
        scores=[None, None]
        played=None

        def __init__(self, team1, team2, score1=None, score2=None):
            self.teams = [team1, team2]
            self.set_scores(score1, score2)

        def set_scores(self, score1, score2):
            if score1 is None or score2 is None:
                self.played = False
            elif type(score1)==int and type(score2):
                self.scores = [int(score1), int(score2)]
                self.played = True
            else:
                self.played = False

        def __naming__(self, lis):
            if type(lis)!=list:
                lis = [lis]
            s = str(lis[0])
            for p in range(1,len(lis)):
                s += " & " + str(lis[p])
            return s

        def __str__(self):
            return str(self.__naming__(self.teams[0])) + "\t"+ str(self.scores[0]) + "\t"+ str(self.scores[1]) + "\t" \
                   + str(self.__naming__(self.teams[1]))

    def __init__(self, players):
        """
        Initialize tournament with players and rankings. Can either pass in a list or a dictionary to initialize the
        players. If a list of players is inserted, then every player will be assumed to be the same rank. Otherwise, a
        dictionary can be passed in that will use the players' all time rankings instead.

        Parameters
        ----------
        players : can be either a list of players (player ID) or a dictionary with the player as the key and the ranking
        as the value.
        """
        if len(players)%2==1:
            raise Exception("Must have an even number of players")
        for p in players:
            self.__player_seed__[p]=random.uniform(0,1)
            self.__rankings__[p]=100 if type(players)==list else players[p]

        doubles_main = round(len(players) / 6)
        singles_main = int((len(players) - 4 * doubles_main) / 2)
        # setting number of singles and doubles for each game
        self.__round_format__ = [[doubles_main, singles_main] for i in range(2)]
        self.__round_format__.append(
            [int(len(players) / 2 - doubles_main * 2), int(len(players) / 2 - singles_main * 2)])
        # random.shuffle(self.__round_format__)

    def matchups(self, r=None):
        if r is None:
            r = self.__round_num__-1
        return self.__rounds__[r]

    def __game_result__(self, match, scale=1, win_mult=1.25):
        if not match.played:
            raise Exception("Match incomplete")
        if type(match.teams[0]) == str: match.teams[0] = [match.teams[0]]
        if type(match.teams[1]) == str: match.teams[1] = [match.teams[1]]
        # half points for doubles
        max_score=max(abs(match.scores[0]),abs(match.scores[1]))
        score_adjustment = float(math.pow(max_score/3,1/2)) if max_score!=0 else 1
        score1 = float(match.scores[0]) / len(match.teams[0]) / score_adjustment
        score2 = float(match.scores[1]) / len(match.teams[1]) / score_adjustment
        # bonus for winning
        if score1 > score2: score1 *= win_mult
        if score1 < score2: score2 *= win_mult
        avt1 = statistics.mean([self.__rankings__[t] for t in match.teams[0]])
        avt2 = statistics.mean([self.__rankings__[t] for t in match.teams[1]])
        diff = scale * (score1 * avt2 / avt1 - score2 * avt1 / avt2)

        winner = {"T": match.teams[0], "S": score1, "A": avt1}
        loser = {"T": match.teams[1], "S": score2, "A": avt2}
        if diff < 0:
            temp = winner
            winner = loser
            loser = temp

        diff = abs(diff)
        points_to_dist = statistics.mean([min(diff, self.__rankings__[t] - 10) for t in loser["T"]])
        for t in winner["T"]: self.__rankings__[t] += points_to_dist
        for t in loser["T"]: self.__rankings__[t] = max(10, self.__rankings__[t] - diff)

        #make a swap with probability 1-p. Keep swapping until we get outcome p.
    def __list_noise__(self, lis,p=1.0):
        while random.uniform(0,1) > p:
            index=random.randint(0,len(lis)-2)
            lis[index:index+2] = reversed(lis[index:index+2])
        return lis

    def __matchup_list__(self):
        # amount of singles matches in the round
        sin = self.__round_format__[self.__round_num__%3][1]

        peeps = self.rankings(as_dict=False)
        ppl = self.rankings(as_dict=False)
        self.__list_noise__(ppl, 1 / len(ppl))
        if self.__print__: print(ppl)
        can_single = [p for p in ppl if not p in self.__played_singles__]

        # create singles matches
        singles_ind = sorted(random.sample(range(0, int(len(can_single)/2)), sin))
        singles_players=set()
        singles_matches = [[can_single[2 * i], can_single[2 * i + 1]] for i in singles_ind]
        matchups=[]
        for p in singles_matches:
            for q in p:
                self.__played_singles__.add(q)
                singles_players.add(q)
            random.shuffle(p)
            matchups.append(self.Match(p[0], p[1]))

        # # create singles matches (old version)
        # singles_ind = sorted(random.sample(range(0, int(len(can_single))), 2 * sin))
        # # print(singles_ind)
        # singles_players = []
        # doubles_players = [p for p in self.__played_singles__]
        # for i in range(len(can_single)):
        #     if i in singles_ind:
        #         singles_players.append(can_single[i])
        #         self.__played_singles__.add(can_single[i])
        #     else:
        #         doubles_players.append(can_single[i])
        # singles_players = [can_single[i] for i in singles_ind]
        # singles_matches = [[singles_players[2 * i], singles_players[2 * i + 1]] for i in
        #                    range(int(len(singles_players) / 2))]
        # for p in singles_matches: random.shuffle(p)
        # matchups = [self.Match(m[0], m[1]) for m in singles_matches]

        # create doubles matchups

        # sort the subsetted list
        doubles_players = [p for p in ppl if p not in singles_players]
        skill_pairs = [[doubles_players[2 * i], doubles_players[2 * i + 1]] for i in
                       range(int(len(doubles_players) / 2))]
        if self.__print__: print("pairs: " + str(skill_pairs))
        for p in skill_pairs: random.shuffle(p)
        random.shuffle(skill_pairs)
        doubles_matches = [self.Match([skill_pairs[2 * i][0], skill_pairs[2 * i + 1][0]],
                            [skill_pairs[2 * i][1], skill_pairs[2 * i + 1][1]]) for i in
                           range(int(len(skill_pairs) / 2))]
        # print(doubles_matches)
        for d in doubles_matches: matchups.append(d)
        random.shuffle(matchups)
        self.__rounds__.append(matchups)

    def __round_complete__(self):
        if self.__round_num__ == 0:
            return True
        for m in self.__rounds__[self.__round_num__-1]:
            if not m.played: return False
        return True

    def update_ranks(self):
        if self.__updated__ or self.__round_num__ == 0:
            return
        for m in self.__rounds__[self.__round_num__-1]:
            self.__game_result__(m)
        self.__updated__=True

    def new_round(self):
        if not self.__round_complete__():
            return
        self.update_ranks()
        if self.__round_num__%3==0:
            self.__played_singles__=set()
            random.shuffle(self.__round_format__)
        self.__matchup_list__()
        self.__updated__=False
        self.__round_num__+=1

    def round_number(self):
        return self.__round_num__

    def rankings(self, as_dict= False):
        ranks = dict(sorted(self.__rankings__.items(), key=lambda item: (item[1], self.__player_seed__[item[0]]), reverse=True))
        if as_dict:
            return ranks
        return list(ranks.keys())

    def all_matches(self):
        data=[]
        for r in self.__rounds__:
            for m in r:
                data.append([m.teams,m.scores])
        return data

    def teams(self):
        teams = []
        ordered = self.rankings(False)
        for i in range(int(len(ordered) / 2)):
            # bracket.append(ordr[i])
            teams.append([ordered[i], ordered[len(ordered) - i - 1]])
        return sorted(teams, key=lambda t: sum([self.__rankings__[i] for i in t]), reverse=True)


# def main():
#
#     # t = Tournament(["Clay","Derek","David","Sidhant","Nil","Jeremy","Nehal","Ana","Aaditya","Catherine","Jasper","Sana","Mahdi","Kusai"])
#     # t.new_round()
#     # print(t.__rounds__[0][0].teams)
#     # print(t.__rounds__[0][1].teams)
#     # for i in range(8):
#     #     m=t.matchups()
#     #     # print(m)
#     #     for n in m:
#     #         n.set_scores(3,0)
#     #         print(n)
#     #     t.new_round()
#     #     print(t.rankings(True))
#     # print(t.teams())
#     # print(t.all_matches())
#
# if __name__== "__main__":
#     main()
