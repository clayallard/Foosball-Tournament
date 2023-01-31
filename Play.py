#!/usr/bin/env python
import argparse
import os
import pickle
from pathlib import Path

import random

# import matplotlib.dates
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
from Tournament import Tournament

# make sure we're working in the directory this file lives in,
# for imports and for simplicity with relative paths
os.chdir(Path(__file__).parent.resolve())

root = Tk()
root.title("Foosball Tournament (Round " + str(1) + ")")
root.geometry("1280x720")

my_entries = []

# with open('Participants.txt') as f:
#     lines = f.read().splitlines()
#     players = [p.strip() for p in lines if p.strip() != ""]
# t = Tournament(players)
# rounds=3


def main():
    global t
    global rounds
    global scores
    with open('Participants.txt') as f:
        lines = f.read().splitlines()
        players = [p.strip() for p in lines if p.strip() != ""]
    t = Tournament(players)

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rounds", default=max(math.floor(30/(len(players)/3)),3), type=int,
                        help="the amount of rounds to play.")
    args = parser.parse_args()
    # rounds=max(math.floor(30/(len(players)/3)),3)
    rounds=args.rounds

    t.new_round()
    scores = [["", ""] for i in range(len(t.matchups()))]
    # update_scores()
    if t.round_number() > rounds:
        print(
            "The tournament is over as the amount of rounds set have been played. To play more rounds, edit the round count in the code.")
        print("Teams: " + str(t.teams()))
    else:
        main_frame = round_setup()
        root.bind('<Return>', lambda event: update_scores())
        root.mainloop()

def naming(team):
    if type(team)!= list:
        team = [team]
    n=str(team[0])
    for i in range(1,len(team)):
        n+= " & " + str(team[i])
    return "(" + n + ")"

#input list to check if any value is not numeric.
def all_numeric(list_of_scores):
    for m in list_of_scores:
        for n in m:
            if not str(n).isnumeric():
                return False
    return True

def round_setup():
    global main_frame
    main_frame = Frame(root)
    main_frame.pack(fill=BOTH, expand=1)

    my_canvas = Canvas(main_frame)
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=RIGHT, fill=Y)

    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind("<Configure>", lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
    # my_canvas.bind_all("<MouseWheel>", my_canvas.yview_scroll)

    second_frame = Frame(my_canvas)

    my_entries.clear()
    my_canvas.create_window((0, 0), window=second_frame, anchor="nw")
    round_matches = t.matchups()
    for x in range(len(round_matches)):
        for y in range(2):
            val=""
            if type(round_matches[x].scores[y]) == int:
                val = str(round_matches[x].scores[y])
            labelNum = Label(second_frame, text=naming(round_matches[x].teams[y])).grid(row=2 * x, column=2 * y)
            my_entry = Entry(second_frame, justify='center')
            my_entry.insert(END, val)
            my_entry.grid(row=2 * x + 1, column=2 * y, sticky='ns', pady=(0, 10))
            my_entries.append(my_entry)

    if t.round_number() == rounds:
        my_button = Button(second_frame, text="Finish", command=update_scores, height=1, width=10)
    else:
        my_button = Button(second_frame, text="Next Round", command=update_scores, height=1, width=10)
    my_button.grid(row=1, column=3, padx=20)
    return main_frame

# def finished():
#     if t.round_number() == rounds:
#         root.destroy()
#     teams = t.teams()
#     seeding = 0
#     st=""
#     for team in teams:
#         seeding+=1
#         st += str(seeding) + " " + naming(team) + "\n"
#     print(st)
#     print(t.rankings(True))

def update_scores():
    global scores
    # clear_output(wait=True)
    for i in range(int(len(my_entries) / 2)):
        val1 = my_entries[2 * i].get()
        val2 = my_entries[2 * i + 1].get()
        scores[i] = [int(val1) if val1.isnumeric() else "", int(val2) if val2.isnumeric() else ""]
    if not all_numeric(scores):
        top = Toplevel(root)
        top.geometry("500x75")
        top.title("Child Window")
        Label(top, text="Cannot continue to the next round until all scores are reported!", font=(18)).place(x=25, y=25)
        return
    # getting data from GUI
    # val1=3 if random.randint(0,1)==0 else random.randint(0,2)
    # val2=3 if val1!=3 else random.randint(0,2)
    # scores[i]=[val1,val2]
    # if pr: print("Singles (" + str(curr_round+1)+") "+str(played_singles))
    round_matches = t.matchups()
    for s in range(len(round_matches)):
        round_matches[s].set_scores(scores[s][0], scores[s][1])
    t.new_round()
    if t.round_number() > rounds:
        root.destroy()
        teams = t.teams()
        seeding = 0
        st=""
        for team in teams:
            seeding+=1
            st += str(seeding) + " " + naming(team) + "\n"
        print(st)
        print(t.rankings(True))
        return
    main_frame.destroy()
    round_setup()
    root.title("Foosball Tournament (Round " + str(t.round_number()) + ")")
    scores=[["",""] for i in range(len(t.matchups()))]



def test():
    # rounds=max(math.floor(30/(len(players)/3)),3)

    t.new_round()
    print(t.__rounds__[0][0].teams)
    print(t.__rounds__[0][1].teams)
    for i in range(8):
        m=t.matchups()
        # print(m)
        for n in m:
            n.set_scores(3,0)
            print(n)
            # print(t.round_number())
        t.new_round()
        print(t.rankings(True))
    print(t.teams())
    # print(t.all_matches())


if __name__== "__main__":
    main()
    # test()
