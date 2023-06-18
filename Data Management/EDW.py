#%%
import tokens, pyodbc
import pandas as pd

#%%
conn = pyodbc.connect(
    DRIVER='{NetezzaSQL}',
    SERVER=tokens.EDW['server'],
    PORT=tokens.EDW['port'],
    DATABASE='REMIS',
    UID=tokens.EDW['username'],
    PWD=tokens.EDW['password']
    )

#%% get list of all tables in connection
tables = pd.read_sql("SELECT * FROM _v_table", conn)
tables = tables['TABLENAME'].tolist()
# %% Read specific table



rfm_lease_df = pd.read_sql("SELECT * FROM S0CIA123.ALL_CIVIL_OUTGRANTS  WHERE CONTRACT_NUMBER LIKE '%A67%' OR CONTRACT_NUMBER LIKE '%W67%' OR CONTRACT_NUMBER LIKE '%A-67%' OR CONTRACT_NUMBER LIKE '%W-67%'", conn)

#%% Read all tables (!!! not recommended, trim tables list first !!!)
for table in tables:
    if "STG_" not in table:
        df1 = pd.read_sql(f'SELECT * FROM S0CIA123.{table}', conn)
        df1.to_csv(r'C:\Users\g3retjjj\Documents\Projects\Building Leases\REMIS\\'+table+".csv")
    #exec(f"{table}_df = pd.read_sql('SELECT * FROM {table}', conn)") #uncomment to read all tables

# %% Close connection
conn.close()
#%%
conn = pyodbc.connect(f"DRIVER={{NetezzaSQL}};SERVER={tokens.EDW['server']};DATABASE=RFMIS;UID={tokens.EDW['username']};PWD={tokens.EDW['password']}")

# %%
tables
# %%
rfm_lease_df.to_csv('g3civoutgrants.csv')
# %%
