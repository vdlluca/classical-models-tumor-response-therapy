import pandas as pd
import math
import itertools as it
import utils



# if a value in vector not numeric, replace it to "with_value"
# input: vector
# output: numeric vector
def clean_nonnumeric(vector, with_value=0):
    #predicate to check if string is an integer
    def is_number(string):
        try:
            return not math.isnan(float(string))
        except ValueError:
            return False

    return [
        i if is_number(i) else with_value
        for i in vector
    ]


# perform preprocessing as described in paper
# input: list of studies as dataframes
# output: combined preprocessed dataframe
def preprocess(studies):
    for study in studies:
        # sort records by time per patient
        study.sort_values(by=['PatientID', 'TreatmentDay'], inplace=True)

        # extract study and arm nr
        study['StudyNr'] = \
            study['StudyArm'].apply(lambda saTxt: int(saTxt[6]))
        study['Arm'] = \
            study['StudyArm'].apply(lambda saTxt: int(saTxt[-1]))
        study.drop('StudyArm', axis=1, inplace=True)

        # set nonnumeric values to 0
        study['TargetLesionLongDiam_mm'] = \
            clean_nonnumeric(study['TargetLesionLongDiam_mm'], with_value=0)
        study['TargetLesionLongDiam_mm'].astype('float')

        # calculate tumor volume using formula
        study['TumorVolume_mm3'] = \
            study['TargetLesionLongDiam_mm'].apply(lambda ld: ld ** 3 * 0.5)

    # normalize tumor volume to range of [0,1]
    min_tv = min(map(
        lambda study: study['TumorVolume_mm3'].min(),
        studies
    ))
    max_tv = max(map(
        lambda study: study['TumorVolume_mm3'].max(),
        studies
    ))
    for study in studies:
        study['TumorVolumeNorm'] = \
            study['TumorVolume_mm3'].apply(lambda tv: (tv - min_tv) / (max_tv - min_tv))

    return studies


if __name__ == '__main__':
    study1 = pd.read_excel('../Original Paper/studies/Study1.xlsx')
    study2 = pd.read_excel('../Original Paper/studies/Study2.xlsx')
    study3 = pd.read_excel('../Original Paper/studies/Study3.xlsx')
    study4 = pd.read_excel('../Original Paper/studies/Study4.xlsx')
    study5 = pd.read_excel('../Original Paper/studies/Study5.xlsx')
    studies = [study1, study2, study3, study4, study5]
    
    print('Patient ID overlap across studies:', check_patient_overlap(studies))
    preprocessed = preprocess(studies)
    print(preprocessed)
    print(get_at_least(preprocessed, 6))