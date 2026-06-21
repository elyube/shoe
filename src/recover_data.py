import pandas as pd
import subprocess
import io
import os

files = [
    "ayakkabidunyasi_prices.csv",
    "derimod_prices.csv",
    "flo_prices.csv",
    "instreet_prices.csv"
]

for file in files:
    print(f"Recovering all history for {file}...")
    
    # Get all commits that modified this file
    cmd = f"git log --pretty=format:'%h' -- data/{file}"
    commits = subprocess.check_output(cmd, shell=True).decode("utf-8").strip().split('\n')
    
    all_dfs = []
    
    for commit in commits:
        if not commit: continue
        try:
            # Get file content at that commit
            content = subprocess.check_output(f"git show {commit}:data/{file}", shell=True).decode("utf-8")
            df = pd.read_csv(io.StringIO(content), on_bad_lines="skip")
            all_dfs.append(df)
        except Exception as e:
            pass
            
    if all_dfs:
        # Combine all historical data
        combined = pd.concat(all_dfs, ignore_index=True)
        
        # We need to deduplicate based on ad, url, zaman (or just ad, url, fiyat, indirimli_fiyat, indirim_orani)
        initial_len = len(combined)
        combined = combined.drop_duplicates()
        print(f"  Total records across history: {initial_len}")
        print(f"  Unique records recovered: {len(combined)}")
        
        # Save back to the current file
        combined.to_csv(f"data/{file}", index=False, encoding="utf-8-sig")
        
        # Also let's do the JSON just in case they need it
        json_file = file.replace(".csv", ".json")
        combined.to_json(f"data/{json_file}", orient="records", force_ascii=False, indent=2)

print("Data recovery complete!")
