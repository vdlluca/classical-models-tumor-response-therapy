import math
from enum import Enum
import numpy as np



# get all records of patients with 'i' or more data points
# params: joint dataframe of all studies, like the output of 'preprocess'
# return: dataframe with data points of patients with 'i' or more data points
def get_at_least(studies, i):
    return studies.groupby('PatientID') \
                  .filter(lambda group: group['PatientID'].count() >= i)


# pairwise check if patient ID is reused across studies
# params: list of studies as dataframes
# return: False if the patient ID's are disjoint, True otherwise
def check_patient_overlap(studies):
    for study1, study2 in it.combinations(studies, 2):
        # pairwise inner join to check if empty
        if study1.join(study2, on='PatientID', rsuffix='_2', how='inner').size > 0:
            return True
    return False


# converts the time (days) to weeks
# e.g if the day 227 => week 33
# params: time vector in days
# return: time vector in weeks
def convert_to_weeks(time):
    return [math.ceil(i/7) for i in time]


# Trend enum
class Trend(Enum):
    UP = 1
    FLUCTUATE = 2
    DOWN = 3

    def color(self):
        if self == Trend.UP:
            return '#d73027'
        elif self == Trend.FLUCTUATE:
            return '#313695'
        elif self == Trend.DOWN:
            return '#1a9850'

    def __lt__(self,other):
        return self.value < other.value


# detect if the trend of LD data is going, up, down or fluctuates
# based on paper section "Patient categorization according to RECIST and trajectory type"
# params: data point vector
# return: trend enum
def detect_trend(vector):
    # get difference vector
    v = np.array(vector)
    diff_v = v[1:] - v[:-1]

    # get sum of positive and negative differences
    pos = np.sum(
        np.clip(diff_v, a_min=0, a_max=None)
    )
    neg = - np.sum(
        np.clip(diff_v, a_min=None, a_max=0)
    )
    
    # UP if strictly positive or sum of positive to sum of negative rate is > 2
    if (neg == 0) or (pos / neg > 2):
        return Trend.UP
    # DOWN if strictly negative or sum of negative to sum of positive rate is > 2
    elif (pos == 0) or (neg / pos > 2):
        return Trend.DOWN
    # FLUCTUATE else
    else:
        return Trend.FLUCTUATE