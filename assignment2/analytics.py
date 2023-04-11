# %%
import zipfile
import pandas as pd

# %%
with zipfile.ZipFile('assignment2/all-events.zip', 'r') as zip_file:
    with zip_file.open('all-events.csv') as csv_file:
        df = pd.read_csv(csv_file)


# %%
df.describe()
df['event'].value_counts()

# %%


# %%
# df = df.sort_values('timestamp',ascending=True)
df.head()

# %%
df['prev_activity'] = df['activity_type'].shift(1)
df.head()

# %%
df['new_activity'] = ((df['event']!= 'location') & (df['activity_type'] != df['prev_activity'])).astype(int)
df.head(10)

# %%
df['activity_end_time'] = df['timestamp'].shift(-1)
df.head()

# %%
df = df[df['new_activity'] == 1 | df['activity_type'].isna()]
df.head()

# %%
df['activity_type'] = df['activity_type'].replace({0:'Car',1:'Bicycle',2:'On Foot', 3:'Still',4:'UNKNOWN',5:'UNKNOWN',6:'UNKNOWN', 7:'Walking',8:'Running'})
df.head()

# %%
activity_df = df[df['event'] == 'activity'][['timestamp', 'activity_end_time','activity_type']]
activity_df.head()
activity_df.rename(columns={'timestamp':'start_time', 'activity_type':'activity'}, inplace=True)
# activity_df = activity_df[activity_df['activity'] != 'UNKNOWN']
activity_df.head(10)

# %%
activity_df['activity'].value_counts()


