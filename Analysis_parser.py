from pandas import read_json, DataFrame

## analysisParse
#  @brief Makes a CSV file from the JSON
#  @param json The json as string
def analysisParse(json):
    df = read_json(json, orient='index')
    df.to_csv('analysis.csv')

if __name__ == "__main__":

    # Making a test json and reading it
    json = '{"row 1":{"col 1":"a","col 2":"b"},"row 2":{"col 1":"c","col 2":"d"}}'
    df = read_json(json,orient='index')

    # Print the dataframe and make it into CSV
    print(df)
    df.to_csv('test.csv')