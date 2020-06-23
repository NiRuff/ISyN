import visit_calc as vis_calc
import nosepoke_calc as np_calc

from os.path import dirname

import tkinter as tk
from tkinter import Tk, Button
from tkinter.filedialog import askopenfilename
import pandas as pd
from pathlib import Path

import datetime

# datetime widget
master = tk.Tk()

curr_datetime = datetime.datetime.now()

# we don't want a full GUI, so keep the root window from appearing
Tk().withdraw()

# show an "Open" dialog box and return the path to the selected file
nosepoke_file = askopenfilename(title="Select Nosepoke.txt", filetypes=[("Nosepoke file", "*.txt")])
visit_file = askopenfilename(title="Select Visit.txt", filetypes=[("Visit file", "*.txt")])
group_assignment_file = askopenfilename(title="Select Group Assignment file")

# create dataframe for nosepoke and for visit file
df_nosepoke = pd.read_csv(nosepoke_file, sep="\t")
df_visit = pd.read_csv(visit_file, sep="\t")
print(df_visit.columns)


# get all phases out of Visit file:
# if a phase occurs more than one time, it will be catched here and renamed in phase_x_1 and phase_x_2
phases = df_visit.Module[(df_visit.Module != df_visit.Module.shift()) & (df_visit.Animal == df_visit.Animal.iloc[0])].values

# add suffix to phases - if element appears > 1 time in whole list,
# append suffix giving the number of times this phase appeared in slice of list
p = list(phases)
phases_temp = list()
for i in range(len(p)):
    if p.count(p[i]) > 1:
        phases_temp.append(p[i] + "_" + str(p[:i+1].count(p[i])))
    else:
        phases_temp.append(p[i])

with open(group_assignment_file) as f:
    label = f.readline()
    content = f.readlines()
group_dict = dict()
for line in content:
    entries = line.strip().split("\t")
    group_dict.update({entries[0]: entries[1:]})

# read out sucrose label
if label.split("\t")[0] != "Label":
    print("Did you enter label in your group assignment file?")
sucrose_label = label.split("\t")[1]

print(sucrose_label)

# create analysis directory and a subdirectory for every phase
analysis_dir = dirname(nosepoke_file) + "_IntelliPy_Analysis_" + curr_datetime.strftime('%Y_%m_%d')
Path(analysis_dir).mkdir(parents=True, exist_ok=True)

for curr_phase in phases_temp:
    Path(analysis_dir + "/" + curr_phase).mkdir(parents=True, exist_ok=True)

# iterate over all phases, create phase-dataframe and apply functionality
# ! phases are defined in Visit.txt - slice by ModuleName in Visit.txt and take
# its min and max VisitId to define for nosepoke file
# the StartTimecode and EndTimecode have to be adjusted like this:
# Timecode = Timecode - StartDate
# So that the Timecode is relative to the phase start

# get first date overall and subtract from first date per phase later
# combine first date and time
first_datetime = df_visit.loc[0, ["StartDate"]].values.item() + " " + df_visit.loc[0, ["StartTime"]].values.item()
first_datetime_total = datetime.datetime.strptime(first_datetime, '%Y-%m-%d %H:%M:%S.%f')

# subtract milliseconds of first entry
millisecond_correction = df_visit.loc[0, ["StartTimecode"]].values.item()
tdelta = datetime.timedelta(seconds=millisecond_correction)

experiment_start = first_datetime_total - tdelta

master.title("Experiment Phases")

entries = list()
startdates = list()

# get startdates of all phases even if a phases occurs multiple times
# by slicing the dataframe by the old_phase
for i in range(len(phases)):
    if i > 0:
        old_phase = phases[i-1]
        entries.append(tk.Entry(master, width=60))
        tk.Label(master, text=phases_temp[i]).grid(row=i)
        slice_start = df_visit.loc[df_visit.Module == old_phase, "Module"].index[0]
        slice_df_visit = df_visit.iloc[slice_start:]
        startdates.append(slice_df_visit[slice_df_visit.Module == phases[i]]["StartDate"].iloc[0])
    else:
        entries.append(tk.Entry(master, width=60))
        tk.Label(master, text=phases_temp[i]).grid(row=i)
        startdates.append(df_visit[df_visit.Module == phases[i]]["StartDate"].iloc[0])
print(startdates)

i = 0
for entry in entries:
    if i == 0:
        entry.insert(10, experiment_start)
    else:
        entry.insert(10, startdates[i] + " 00:00:00.000")
    entry.grid(row=i, column=1)
    i += 1

no_lick_ex = tk.IntVar()
tk.Checkbutton(master, text="exclude Nosepokes without lick", variable=no_lick_ex).grid(row=1, column=2, sticky=tk.W)
no_lick_rem = tk.IntVar()
tk.Checkbutton(master, text="remove Nosepokes without lick", variable=no_lick_rem).grid(row=2, column=2, sticky=tk.W)
no_lick_only = tk.IntVar()
tk.Checkbutton(master, text="show Nosepokes without lick", variable=no_lick_only).grid(row=3, column=2, sticky=tk.W)
water_y_suc_n = tk.IntVar()
tk.Checkbutton(master, text="Water: Correct, Sucrose: Incorrect", variable=water_y_suc_n).grid(row=4, column=2, sticky=tk.W)
water_y_suc_y = tk.IntVar()
tk.Checkbutton(master, text="Water: Correct, Sucrose: Correct", variable=water_y_suc_y).grid(row=5, column=2, sticky=tk.W)

tk.Button(master,
          text='Submit',
          command=master.quit).grid(row=len(entries)+1,
                                    column=0,
                                    sticky=tk.W,
                                    pady=4)
#todo
# implement no_lick for sucrose
# write a manual with pictures

added_hour_intervalls = []

def addHourInterval():
    e = tk.Entry(master)
    e.grid(sticky=tk.W, column=1, row=len(entries)+3+len(added_hour_intervalls))
    added_hour_intervalls.append(e)


e1 = tk.Entry(master)
e1.grid(sticky=tk.W, column=2, row=len(entries)+3)
e1.insert(10, "00:00:00.000")
e2 = tk.Entry(master)
e2.grid(sticky=tk.W, column=3, row=len(entries)+3)
e2.insert(10, "00:00:00.000")

tk.Button(master,
          text='Add hour intervalls',
          command=addHourInterval).grid(row=len(entries)+1,
                                    column=1,
                                    sticky=tk.W,
                                    pady=4)

tk.Label(master, text='Hour intervalls').grid(row=len(entries)+2,
                                    column=1,
                                    sticky=tk.W,
                                    pady=4)

tk.Label(master, text='Daily timeframe').grid(row=len(entries)+2,
                                    column=2,
                                    sticky=tk.W,
                                    pady=4)


tk.mainloop()
#added_timeframes = (datetime.datetime.strptime(e1.get(),"%H:%M:%S.%f"), datetime.datetime.strptime(e2.get(), "%H:%M:%S.%f"))
if e2.get() == "00:00:00.000":
    added_timeframes = pd.DataFrame([e1.get(), "23:59:59.999"], columns=["times"])
else:
    added_timeframes = pd.DataFrame([e1.get(), e2.get()], columns = ["times"])
added_timeframes["times"] = pd.to_datetime(added_timeframes["times"], format='%H:%M:%S.%f').dt.time
tf_start = added_timeframes.iloc[0,0]
tf_end = added_timeframes.iloc[1,0]



phase_datetimes = list()
for entry in entries:
    phase_datetimes.append(datetime.datetime.strptime(entry.get(), '%Y-%m-%d %H:%M:%S.%f'))
print(phase_datetimes)

hour_intervals = []
for e in added_hour_intervalls:
    hour_intervals.append(e.get())

#apply timeframe:
df_visit["StartTimeEdit"] = pd.to_datetime(df_visit["StartTime"], format='%H:%M:%S.%f').dt.time
print(len(df_visit))
df_visit = df_visit[(df_visit["StartTimeEdit"] >= tf_start) & (df_visit["StartTimeEdit"] <= tf_end)]
print(len(df_visit))


# create columns for StartDateTime and EndDateTime
df_visit.loc[:, "StartDateTime"] = pd.to_datetime(df_visit["StartDate"] + " " + df_visit["StartTime"], format='%Y-%m-%d %H:%M:%S.%f')
df_visit.loc[:, "EndDateTime"] = pd.to_datetime(df_visit["EndDate"] + " " + df_visit["EndTime"], format='%Y-%m-%d %H:%M:%S.%f')

df_nosepoke.loc[:, "StartDateTime"] = pd.to_datetime(df_nosepoke["StartDate"] + " " + df_nosepoke["StartTime"], format='%Y-%m-%d %H:%M:%S.%f')
df_nosepoke.loc[:, "EndDateTime"] = pd.to_datetime(df_nosepoke["EndDate"] + " " + df_nosepoke["EndTime"], format='%Y-%m-%d %H:%M:%S.%f')

# insert column for "Module" in df_nosepoke
df_nosepoke["Module"] = pd.np.nan
for i in range(len(phase_datetimes)):
    if i == len(phase_datetimes)-1:
        df_nosepoke.loc[df_nosepoke["StartDateTime"] >= phase_datetimes[i], "Module"] = phases[i]
    elif i > 0:
        df_nosepoke.loc[(df_nosepoke["StartDateTime"] < phase_datetimes[i+1]) & (df_nosepoke["StartDateTime"] > phase_datetimes[i]), "Module"] = phases[i]
    else:
        df_nosepoke.loc[df_nosepoke["StartDateTime"] < phase_datetimes[i+1], "Module"] = phases[i]

if df_nosepoke["Module"].isnull().values.any():
    print("Warning, some rows did not get a module assignment")

# for sanity check
total_visit_rows = 0
total_nosepoke_rows = 0

i = 0
for j in range(len(phases)):
    # reduce by module
    curr_visit_df_module = df_visit.loc[df_visit["Module"] == phases[j]]
    curr_nosepoke_df_module = df_nosepoke.loc[df_nosepoke["Module"] == phases[j]]

    # further reduce by time - if module appears multiple times, check for start of next module so that
    # > now and < later can assure no duplicate counting of later modules values

    if i+1 < len(phase_datetimes):
        curr_visit_df = curr_visit_df_module.loc[(curr_visit_df_module["StartDateTime"] >= phase_datetimes[i]) & (curr_visit_df_module["StartDateTime"] < phase_datetimes[i+1])]
    else:
        curr_visit_df = curr_visit_df_module.loc[curr_visit_df_module["StartDateTime"] >= phase_datetimes[i]]

    # add visitOrder for curr_visit
    curr_visit_df.loc[:, "VisitOrder"] = curr_visit_df.groupby("Animal")["VisitOrder"].expanding().count().reset_index(0)["VisitOrder"]

    # reset timecode
    curr_visit_df.loc[:, ["StartTimecode"]] = (curr_visit_df["StartDateTime"] - phase_datetimes[i]).dt.total_seconds()
    curr_visit_df.loc[:, ["EndTimecode"]] = (curr_visit_df["EndDateTime"] - phase_datetimes[i]).dt.total_seconds()

    min_visit_id = curr_visit_df["VisitID"].min()
    max_visit_id = curr_visit_df["VisitID"].max()

    # create curr_nosepoke_df from visitIDs
    curr_nosepoke_df = df_nosepoke.loc[(df_nosepoke["VisitID"] >= min_visit_id) & (df_nosepoke["VisitID"] <= max_visit_id)]

    # reset timecode
    curr_nosepoke_df.loc[:, ["StartTimecode"]] = (curr_nosepoke_df["StartDateTime"] - phase_datetimes[i]).dt.total_seconds()
    curr_nosepoke_df.loc[:, ["EndTimecode"]] = (curr_nosepoke_df["EndDateTime"] - phase_datetimes[i]).dt.total_seconds()

    vis_calc.learning_rate(curr_visit_df.copy(), path=analysis_dir + "/" + phases_temp[j], phase=phases[j], group_dict=group_dict)
    vis_calc.pivot(curr_visit_df.copy(), path=analysis_dir + "/" + phases_temp[j], phase=phases[j], group_dict=group_dict,
                   hour_intervals=hour_intervals)

    if phases[i] == "SucrosePreference":
        np_calc.learning_rate_sucrose(curr_nosepoke_df.copy(), path=analysis_dir + "/" + phases_temp[j],
                                      group_dict=group_dict, water_y_suc_n=water_y_suc_n, water_y_suc_y=water_y_suc_y,
                                      sucrose_label=sucrose_label)
    else:
        np_calc.learning_rate_non_sucrose(curr_nosepoke_df.copy(), path=analysis_dir + "/" + phases_temp[j],
                                          phase=phases[j], group_dict=group_dict, no_lick_ex=no_lick_ex, no_lick_rem=no_lick_rem,
                                          no_lick_only=no_lick_only)

    total_visit_rows += len(curr_visit_df.index)
    total_nosepoke_rows += len(curr_nosepoke_df)
    i += 1

if total_visit_rows != len(df_visit.index):
    print("!Visit row number not matching!" + str(total_visit_rows) + "\t" + str(len(df_visit.index)))
if total_nosepoke_rows != len(df_nosepoke.index):
    print("!Nosepoke row number not matching!" + str(total_nosepoke_rows) + "\t" + str(len(df_nosepoke.index)))


master.destroy()

