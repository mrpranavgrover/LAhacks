import pandas as pd
import numpy as np
from pyjarowinkler import distance
import state_abbreviation
import street_abbreviation
from datetime import datetime as dt

# read the CSV file
data = pd.read_csv("Patient_Matching_Data_2.csv")
data["CustomID"] = pd.Series(data.index + 1, index = data.index)

originalData = data

def listToString(s):  
    
    # initialize an empty string 
    str1 = " "    
    
    # return string   
    return (str1.join(s))  

#street abbreviations
def replace_street_abbreviation(string):
 string2 = str(string).split()
 wo_lastword = string2[:len(string2)- 1]
 before_end = listToString(wo_lastword)
 last_word = string2[-1].lower().replace(".", "")
 if last_word in street_abbreviation.street_abbrev:
   return before_end.lower() + " " + street_abbreviation.street_abbrev[last_word]
 return string

#State abbreviations
def replace_state_abbreviations(string):
  #string.replace(fullname, abbreviation) 
  if string in state_abbreviation.abbrev_state:
    return state_abbreviation.abbrev_state[string]
  return string
   
#replaceMIinital 
def replace_MI(string1):
  if string1 == None:
    return ""
  return string1[:1]

# replace gender with abbreviations
def replace_gender_abbreviations(string1):
  if string1 is None:
    return ""
  string1 = str(string1).upper()
  if string1[:1] == "M":
    return "M"
  if string1[:1] == "F":
    return "F"
  if string1[:1] == "U":
    return "U"
  return string1

def replace_all_data(data):
  data["Sex"] = data["Sex"].map(replace_gender_abbreviations, na_action = 'ignore')
  data["Current Street 1"]= data["Current Street 1"].map(replace_street_abbreviation, na_action = 'ignore')
  data["Current State"] = data["Current State"].map(replace_state_abbreviations, na_action = 'ignore')
  data["MI"] = data["MI"].map(replace_MI, na_action = 'ignore')
#Calling replace_all_data
replace_all_data(data)  

# Find the groups
group_number = 0
groups = {
}

# Accepts two strings as arguments
# Returns the Jaro-Winkler distance between those two strings from 0 to 1
def compare_strings(string1, string2):
  return distance.get_jaro_distance(string1, string2, winkler=True, scaling=0.1)  

def compare_rows(row1, row2):
  if row1["CustomID"] >= row2["CustomID"]:
    return
  # We don't compare all the columns because some have misleading data
  columns = {"First Name", "Last Name", "MI", "Date of Birth", "Sex", "Current Street 1", "Current City", "Current State", "Current Zip Code", "Previous Street 1", "Previous City", "Previous State", "Previous Zip Code"}
  compared_items = 0
  total_similarity = 0
  for column in columns:
    value1 = str(row1[column])
    value2 = str(row2[column])
    # Eliminate blank rows
    if (not pd.isnull(data.loc[row1["CustomID"] - 1, column])) and (not pd.isnull(data.loc[row2["CustomID"] - 1, column])) and len(value1) != 0 and len(value2) != 0 and value1.lower() != "nan" and value2.lower() != "nan":
      # Find the similarity between two items
      similarity = compare_strings(value1, value2)
      if column == "Date of Birth" and similarity < 0.6:
        similarity = 0
      if column == "Current Street 1" and similarity < 0.7:
        similarity *= 0.5
      total_similarity += similarity
      compared_items += 1
  average_similarity = 0
  if compared_items != 0:
    average_similarity = total_similarity / compared_items
  
  THRESHOLD = 0.83
  if average_similarity > THRESHOLD or row1["GroupID"] == row2["GroupID"]:
    if average_similarity > THRESHOLD:
      groups[group_number].append(row2["CustomID"])
    print("Similarity between " + str(row1["CustomID"]) + " and " + str(row2["CustomID"]) + " is " + str(round(average_similarity * 100000)/1000) + "%. - " + str(compared_items) + " fields compared. " + ("Correct!" if row1["GroupID"] == row2["GroupID"] and average_similarity > THRESHOLD else "Wrong!"))
  
    # comment the stuff after this out if you don't want all the verbose stuffs
    """
    for column in columns:
      value1 = str(row1[column])
      value2 = str(row2[column])
      # Eliminate blank rows
      if (not pd.isnull(data.loc[row1["CustomID"] - 1, column])) and (not pd.isnull(data.loc[row2["CustomID"] - 1, column])) and len(value1) != 0 and len(value2) != 0 and value1.lower() != "nan" and value2.lower() != "nan":
        # Find the similarity between two itmes
        similarity = compare_strings(value1, value2)
        print("  " + column + ": Value 1: " + value1 + ", Value 2: " + value2 + " Similarity: " + str(round(similarity * 100000)/1000) + "\n")
    print("\n\n\n\n\n\n\n\n\n")
    """

def find_groups():
  global group_number
  index = 0
  
  for i in data.index:
    # Identify row we are comparing others to
    group_number += 1
    groups[group_number] = [index+1]
    row1 = data.iloc[index]
    print(group_number)
    # Compare other rows to our target row
    data.apply(lambda row2: compare_rows(row1, row2), axis=1)
    index = next_ungrouped()
    if index == -1:
      return

def is_grouped(value):
  for group in groups:
    for item in groups[group]: 
      if value == item:
        return True
  return False

def next_ungrouped():
  for i in data.index:
    if not is_grouped(i + 1):
      return i 
  return -1

find_groups()

def print_groups():
	for group in groups:
		print("Group: " + str(group))
		for person in groups[group]:
			print("  - "+data.iloc[person-1]["First Name"])
print(groups)
print_groups()
