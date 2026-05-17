import pandas
import json

def ReadFromJsonFile(path:str) -> list:
    try:
        f = open(file=path, mode="rt")
        jason = json.load(f)
        f.close()
        if type(jason) is list:
            return jason
        else:
            return []
    except:
        return []


def AppendJsonFile(path:str, new_list:list) -> bool:
    current = ReadFromJsonFile(path)
    new = current + new_list

    try:
        f = open(file=path, mode="wt")
        json.dump(new, f)
        f.close()
        return True
    except:
        return False


def RecordNewData(new_records:list, json_path:str, csv_path:str, quiet:bool=True):
    AppendJsonFile(path=json_path, new_list=new_records)
    df = pandas.DataFrame(new_records)
    df.to_csv(CSV_FILE, mode="a", index=False, header=False)
    if not quiet:
        print(f"✓ {len(new_records)} kayıt kaydedildi → {json_path} & {csv_path}")