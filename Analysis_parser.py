from pandas import read_json, DataFrame

df = read_json('analysis.json')
df.to_csv('analysis.csv')