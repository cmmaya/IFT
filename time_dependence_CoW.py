import pandas as pd

df = pd.read_csv('query_result.csv')

def getDataFrameFirstMinutes(minutes: int):
    df['time'] = pd.to_datetime(df['time'], utc=True)

    # Filter the DataFrame for rows within the first 15 minutes
    filtered_df = df[df['time'] > df['time'].max() - pd.Timedelta(minutes=minutes)]

    return filtered_df

def getWeightProportion(df):
    df = df.fillna(0)
    product = df['fill_proportion'] * df['buy_value_usd']
    total = df['buy_value_usd'].sum()
    return product.sum()/total

df_minutes = getDataFrameFirstMinutes(15)
print(getWeightProportion(df_minutes))