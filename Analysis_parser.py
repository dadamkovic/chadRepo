###############################################
# NOTE: The SonarQube doesn't give resolution #
###############################################
from pandas import read_json, DataFrame
from json import load
from math import isnan

## analysisParse
#  @brief Makes a CSV file from the JSON
#
#  @param json_string   The json as string
#  NOTE: Doesn't select columns nor handle data in any way. If the json is read as a string in the program,
#  this function should be updated.
def analysisParse(json_string):
    df = read_json(json_string, orient='index')
    df.to_csv('analysis.csv')

## analysisParseFile
#  @brief Makes a CSV file from SonarQube JSON file
#
#  @param json_file     The json as a .json file
#  @param csv_filename  Filename for the CSV to be created
def analysisParseFile(json_file, csv_filename='analysis.csv'):

    # Open json file and load it
    with open(json_file) as f:
        df = load(f)
    
    # Get the issues from the json and make it into pandas dataframe
    df = DataFrame(df['issues'])

    # Parse issue start- and end line from textRange
    start_lines = []
    end_lines = []
    resolutions = []
    for i in df['textRange'].tolist():
        if type(i) is dict:
            start_lines.append(i['startLine'])
            end_lines.append(i['endLine'])
        else:
            start_lines.append("")
            end_lines.append("")
        resolutions.append("null")

    # Select the columns and rename the ones with different names compared to what's asked
    df = df[['project', 'creationDate', 'hash', 'type', 'rule', 'component', 'severity', 'status', 'message', 'effort', 'debt', 'author']]
    df = df.rename(columns={'project':'projectName', 'hash':'creationCommitHash', 'rule':'squid'})

    # Insert parsed startLine, endLine and resolutions
    df.insert(7, "startLine", start_lines, True)
    df.insert(8, "endLine", end_lines, True)
    df.insert(9, "resolution", resolutions, True)

    # Save csv
    df.to_csv(csv_filename)

if __name__ == "__main__":
    analysisParseFile("proto_and_sample_data/data/proto_and_sample_data_data_commons-cli.sonar_data.json", "test.csv")