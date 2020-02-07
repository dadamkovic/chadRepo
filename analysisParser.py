##################################################################
# NOTE: The SonarQube doesn't give resolution, endLine nor squid #
##################################################################
from pandas import read_json, DataFrame
from json import load

## analysisParse
#  @brief Makes a CSV file from the JSON
#  @param json_string The json as string
#  NOTE: Doesn't select columns nor handle data in any way. If the json is read as a string in the program,
#  this function should be updated.
def analysisParse(json_string):
    df = read_json(json_string, orient='index')
    df.to_csv('analysis.csv')

## analysisParseFile
#  @brief Makes a CSV file from SonarQube JSON file
#  @param json_file The json as a .json file
def analysisParseFile(json_file):

    # Open json file and load it
    with open(json_file) as f:
        df = load(f)
    
    # Get the issues from the json and make it into pandas dataframe
    df = DataFrame(df['issues'])

    # Select the columns and rename the ones with different names compared to what's asked
    df = df[['project', 'creationDate', 'hash', 'type', 'component', 'severity', 'line', 'status', 'message', 'effort', 'debt', 'author']]
    df = df.rename(columns={'project':'projectName', 'hash':'creationCommitHash', 'line':'startLine'})

    # Save csv
    df.to_csv('analysis.csv')

if __name__ == "__main__":

    # Reading a test json and reading it
    with open("proto_and_sample_data/data/proto_and_sample_data_data_commons-cli.sonar_data.json") as f:
        df = load(f)

    # Print the dataframe and make it into CSV
    df = DataFrame(df['issues'])
    df = df[['project', 'creationDate', 'hash', 'type', 'component', 'severity', 'line', 'status', 'message', 'effort', 'debt', 'author']]
    df = df.rename(columns={'project':'projectName', 'hash':'creationCommitHash', 'line':'startLine'})
    print(df.loc[15])
    df.to_csv('test.csv')