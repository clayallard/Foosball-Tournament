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
    """
    Creates a tournament of an even number of players. After each match, the result of the games are recorded and each
    player's ranking will be adjusted. Then those ranks will be used to determine subsequent matches. This is known is
    skill-based match-making.
    """
    __rankings__ = dict()
    __player_seed__ = dict()
    __round_num__ = 0
    __rounds__ = []
    __played_singles__ = set()
    __cycle__ = 1
    __print__ = False
    __teams__ = None
    __updated__ = False

    class Match:
        """
        Holds data for the teams and scores of the match.
        """
        scores = [None, None]
        played = None

        def __init__(self, team1, team2, score1=None, score2=None):
            """
            Initialize matchup.
            """
            self.teams = [team1, team2]
            self.set_scores(score1, score2)

        def set_scores(self, score1, score2):
            """
            Sets the score, but only if both values are numeric. Otherwise, it does nothing.
            """
            if score1 is None or score2 is None:
                self.played = False
            elif type(score1) == int and type(score2):
                self.scores = [int(score1), int(score2)]
                self.played = True
            else:
                self.played = False

        def __naming__(self, lis):
            """
            Naming convention of teams is "P1 & P2"
            """
            if type(lis) != list:
                lis = [lis]
            s = str(lis[0])
            for p in range(1, len(lis)):
                s += " & " + str(lis[p])
            return s

        def __str__(self):
            return str(self.__naming__(self.teams[0])) + "\t" + str(self.scores[0]) + "\t" + str(self.scores[1]) + "\t" \
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
        if len(players) % 2 == 1:
            raise Exception("Must have an even number of players")
        for p in players:
            # in case of ties everyone has a random seed to break it.
            self.__player_seed__[p] = random.uniform(0, 1)
            # base ranking
            self.__rankings__[p] = 100 if type(players) == list else players[p]

        # Make sure everyone plays two doubles and one singles match every 3 rounds.
        doubles_main = round(len(players) / 6)
        singles_main = int((len(players) - 4 * doubles_main) / 2)
        # setting number of singles and doubles for each game
        self.__round_format__ = [[doubles_main, singles_main] for i in range(2)]
        self.__round_format__.append(
            [int(len(players) / 2 - doubles_main * 2), int(len(players) / 2 - singles_main * 2)])

    def matchups(self, r=None):
        """
        Returns all of the matchups of a given round. The parameter can be specified to collect any of the previous
        rounds.
        """
        if r is None:
            r = self.__round_num__ - 1
        return self.__rounds__[r]

    def __game_result__(self, match, scale=1, win_mult=1.15):
        """
        Initialize tournament with players and rankings. Can either pass in a list or a dictionary to initialize the
        players. If a list of players is inserted, then every player will be assumed to be the same rank. Otherwise, a
        dictionary can be passed in that will use the players' all time rankings instead.

        Parameters
        ----------
        match : The match that was played. It must be a completed match.
        scale : The amount of points per goal.
        win_mult : The bonus for winning the match.
        """
        if not match.played:
            raise Exception("Match incomplete")
        # Convert to list in order to make calculations easier.
        if type(match.teams[0]) == str: match.teams[0] = [match.teams[0]]
        if type(match.teams[1]) == str: match.teams[1] = [match.teams[1]]
        # Half points for doubles
        max_score = max(abs(match.scores[0]), abs(match.scores[1]))
        # To adjust for games that involve a lot of points.
        score_adjustment = float(math.pow(max_score / 3, 1 / 3)) if max_score != 0 else 1
        score1 = float(match.scores[0]) / len(match.teams[0]) / score_adjustment
        score2 = float(match.scores[1]) / len(match.teams[1]) / score_adjustment
        # Bonus for winning
        if score1 > score2: score1 *= win_mult
        if score1 < score2: score2 *= win_mult
        # The points to be distribute depends on the average of the two teams.
        # Points are weighted so that more points are earned the higher ranked the opponent is.
        avt1 = statistics.mean([self.__rankings__[t] for t in match.teams[0]])
        avt2 = statistics.mean([self.__rankings__[t] for t in match.teams[1]])
        diff = scale * (score1 * avt2 / avt1 - score2 * avt1 / avt2)

        # Redistribute the points based on the result.
        winner = {"T": match.teams[0], "S": score1, "A": avt1}
        loser = {"T": match.teams[1], "S": score2, "A": avt2}
        if diff < 0:
            temp = winner
            winner = loser
            loser = temp

        # Want to make sure points can't go below 10. Otherwise, players can be close to 0 points and gain too many
        # points per goal.
        diff = abs(diff)
        points_to_dist = statistics.mean([min(diff, self.__rankings__[t] - 10) for t in loser["T"]])
        for t in winner["T"]: self.__rankings__[t] += points_to_dist
        for t in loser["T"]: self.__rankings__[t] = max(10, self.__rankings__[t] - diff)

    def __list_noise__(self, lis, p=1.0):
        """
        Helper method for __matchup_list__. Make random swaps for the list of rankings so that matchups don't get too
        repetitive.

        :param lis: List of players
        :param p: geometric parameter for the probability to stop switching.
        :return: The shuffled list.
        """
        while random.uniform(0, 1) > p:
            index = random.randint(0, len(lis) - 2)
            lis[index:index + 2] = reversed(lis[index:index + 2])
        return lis

    def __matchup_list__(self):
        # amount of singles matches in the round
        sin = self.__round_format__[self.__round_num__ % 3][1]

        # for_testing_purposes = self.rankings(as_dict=False)
        ppl = self.rankings(as_dict=False)
        # Add noise to the list
        self.__list_noise__(ppl, 1 / len(ppl))
        # if self.__print__: print(ppl)
        # List of people who have yet to play singles in the 3 round cycle.
        can_single = [p for p in ppl if not p in self.__played_singles__]

        # create singles matches
        singles_ind = sorted(random.sample(range(0, int(len(can_single) / 2)), sin))
        # Keep track of the players playing singles.
        singles_players = set()
        singles_matches = [[can_single[2 * i], can_single[2 * i + 1]] for i in singles_ind]
        # Will store all the matchups for this round.
        matchups = []
        for p in singles_matches:
            for q in p:
                self.__played_singles__.add(q)
                singles_players.add(q)
            # Shuffle order of each player to not reveal player rankings.
            random.shuffle(p)
            matchups.append(self.Match(p[0], p[1]))

        # create doubles matchups
        # sort the subsetted list
        doubles_players = [p for p in ppl if p not in singles_players]
        # Group players by skill. Each pair is guaranteed to be playing against eachother.
        skill_pairs = [[doubles_players[2 * i], doubles_players[2 * i + 1]] for i in
                       range(int(len(doubles_players) / 2))]
        # if self.__print__: print("pairs: " + str(skill_pairs))
        # Randomize the skill pairs. One player from each pair will be randomly chosen to be on the same team.
        for p in skill_pairs: random.shuffle(p)
        random.shuffle(skill_pairs)
        doubles_matches = [self.Match([skill_pairs[2 * i][0], skill_pairs[2 * i + 1][0]],
                                      [skill_pairs[2 * i][1], skill_pairs[2 * i + 1][1]]) for i in
                           range(int(len(skill_pairs) / 2))]
        for d in doubles_matches: matchups.append(d)
        random.shuffle(matchups)
        self.__rounds__.append(matchups)

    def __round_complete__(self):
        """
        Returns true if all matchups are completed in the round.
        """
        if self.__round_num__ == 0:
            return True
        for m in self.__rounds__[self.__round_num__ - 1]:
            if not m.played: return False
        return True

    def update_ranks(self):
        """
        Reports the game results
        """
        if self.__updated__ or self.__round_num__ == 0:
            return
        for m in self.__rounds__[self.__round_num__ - 1]:
            self.__game_result__(m)
        self.__updated__ = True

    def new_round(self):
        """
        If the round is complete, sets up the next round.
        """
        if not self.__round_complete__():
            return
        self.update_ranks()
        if self.__round_num__ % 3 == 0:
            self.__played_singles__ = set()
            random.shuffle(self.__round_format__)
        self.__matchup_list__()
        self.__updated__ = False
        self.__round_num__ += 1

    def round_number(self):
        """
        The round number
        """
        return self.__round_num__

    def rankings(self, as_dict=False):
        """
        The rankings of all the players in order. Either with or without the real rankings.
        :param as_dict: Returns dictionary of rankings if True, and just a list of the ranks if False.
        """
        ranks = dict(
            sorted(self.__rankings__.items(), key=lambda item: (item[1], self.__player_seed__[item[0]]), reverse=True))
        if as_dict:
            return ranks
        return list(ranks.keys())

    def all_matches(self):
        """
        Returns list of all the matches from the tournament so far.
        """
        data = []
        for r in self.__rounds__:
            for m in r:
                data.append([m.teams, m.scores])
        return data

    def teams(self):
        """
        If the tournament ends, these are the teams that would be the most fair. Have the highest ranked player with
        the lowest ranked player and so on.
        """
        teams = []
        ordered = self.rankings(False)
        for i in range(int(len(ordered) / 2)):
            # bracket.append(ordr[i])
            teams.append([ordered[i], ordered[len(ordered) - i - 1]])
        return sorted(teams, key=lambda t: sum([self.__rankings__[i] for i in t]), reverse=True)
