# IntelliPy

## Features

The IntelliCage system helps researchers to conduct behavioral experiments and learning experiments with mice while ensuring minimal human intervention. The animals can be observed for long time periods - up to several weeks. This long-term data acquisition can provide new insights in mouse behavior, that might not be detectable in short-term observations.
However, analyzing those big amounts of data is challenging for many researchers. 
IntelliPy aims to simplify and automize many aspects of the analysis, such as acquiring data per group, creating learning curves or pivoting parameters in different timeframes. All plots are automatically created and the final tables for statistical tests are stored separately for the user.


## Usage
### Create a group assignment file:
A tab-separated text file (tsv) is necessary in order to tell IntelliPy, which Animal belongs to which group.
It additionally contiains information about the label given for sucrose - if Sucrose Preference experiments were performed.
You have to create this file for yourself in this manner:

1)  Give the word **Label** followed by a tab followed by the label you chose for sucrose in line one.
2)  Give the name of the first group followed by a tab and then all animals belonging to this group - also tab separated
3)  repeat step 2) for all remaining groups

*An example file is added as* **"Group_assignment.txt"**
