##################################################################
# NOTE: The SonarQube doesn't give resolution, endLine nor squid #
##################################################################
from pandas import read_json, DataFrame
from json import load

## analysisParse
#  @brief Makes a CSV file from the pandas dataframe
#  @param df        The pandas dataframe
#  @param csv_name  Filename for output
def analysisParse(df, csv_name):
    # Select the columns and rename the ones with different names compared to what's asked
    df = df[['project', 'creationDate', 'hash', 'type', 'component', 'severity', 'line', 'status', 'message', 'effort', 'debt', 'author']]
    df = df.rename(columns={'project':'projectName', 'hash':'creationCommitHash', 'line':'startLine'})

    # Save csv
    df.to_csv(csv_name, index=False)

## analysisParseFile
#  @brief Makes json file into pandas dataframe and passes it to analysisParse()
#  @param json_file The json as a .json file
#  @param csv_name  Filename for output
def analysisParseFile(json_file, csv_name='analysis.csv'):

    # Open json file and load it
    with open(json_file) as f:
        df = load(f)
    
    # Get the issues from the json and make it into pandas dataframe
    df = DataFrame(df['issues'])
    analysisParse(df, csv_name)

## analysisParseList
#  @brief Makes list into pandas dataframe and passes it to analysisParse()
#  @param df_list   List with issues
#  @param csv_name  Filename for output
def analysisParseList(df_list, csv_name='analysis.csv'):
    df = DataFrame(df_list)
    analysisParse(df, csv_name)

## analysisParseJson
#  @brief Makes json string into pandas dataframe and passes it to analysisParse()
#  @param json_string   Issues in JSON string
#  @param csv_name      Filename for output
def analysisParseJson(json_string, csv_name='analysis.csv'):
    df = read_json(json_string, orient='index')
    analysisParse(df, csv_name)

## analysisParseGit
#  @brief Takes the dict with git info and dumps it into .csv
#  @param git_info      Dictionary with info
#  @param csv_name      Filename for output
def analysisParseGit(git_info, csv_name='analysis_git.csv'):
    str_info = {}
    for key in git_info.keys():
        str_info[key] = str(git_info[key])

    df = DataFrame(str_info, index=[0])
    df.to_csv(csv_name)

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
