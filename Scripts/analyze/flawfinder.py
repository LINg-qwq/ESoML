import subprocess
import pandas as pd
import os
import csv
from analyze.Leak_CWE import LEAK_CWE

ANALYZER_PATH = "flawfinder"

def run_flawfinder(folder_path):
    output_file = os.path.join(folder_path, "flawfinder_result.csv")
    
    try:
        command = [
            ANALYZER_PATH,
            "--csv",
            ">",
            output_file,
            folder_path
        ]
        
        # 执行 flawfinder 命令
        subprocess.run(" ".join(command), shell=True, check=True)
        return output_file
    except Exception as e:
        print(f"Exception: {e}")
    return None

def parse_flawfinder_csv(csv_file):
    try:
        df = pd.read_csv(csv_file, skiprows=1)

        df = df[df['Level'] > 3]

        df = df.rename(columns={
            'File': 'file',
            'Line': 'line',
            'CWEs': 'cwe'
        })

        df['file'] = df['file'].apply(os.path.basename)
        
        return df
        
    except Exception as e:
        print(f"Exception: {e}")
        return pd.DataFrame()

def flawfinder_analyze(dir_name):
    csv_output = run_flawfinder(dir_name)
    if csv_output:
        return parse_flawfinder_csv(csv_output)
    return pd.DataFrame()

def evaluate_flawfinder_effect(dir_path):
    df_flawfinder = flawfinder_analyze(dir_path)

    if len(df_flawfinder) == 0:
        return 0
        
    csv_path = os.path.join(dir_path, 'memleak_func.csv')

    if not os.path.isfile(csv_path):
        print(f'{csv_path} not exist')
        return 0

    df_memleak = pd.read_csv(csv_path)

    df_memleak['Start Line'] = pd.to_numeric(df_memleak['Start Line'], errors='coerce')
    df_memleak['End Line'] = pd.to_numeric(df_memleak['End Line'], errors='coerce')
    df_flawfinder['line'] = pd.to_numeric(df_flawfinder['line'], errors='coerce')

    leak_functions = df_memleak.shape[0]

    if leak_functions == 0:
        if any(cwe in LEAK_CWE for cwe in df_flawfinder['cwe'].dropna()):
            return 4

    correctly_marked_count = 0
    marked_count = 0

    for _, row_leak in df_memleak.iterrows():
        file_name = row_leak['File Name']
        start_line = row_leak['Start Line']
        end_line = row_leak['End Line']

        df_filtered = df_flawfinder[
            (df_flawfinder['file'] == file_name) &
            (df_flawfinder['line'] >= start_line) &
            (df_flawfinder['line'] <= end_line)
        ]
        
        if not df_filtered.empty:
            marked_count += 1
            if any(cwe in LEAK_CWE for cwe in df_filtered['cwe'].dropna()):
                correctly_marked_count += 1

    if correctly_marked_count == leak_functions:
        return 4
    elif marked_count == leak_functions:
        return 3
    elif correctly_marked_count >= 1:
        return 2
    elif marked_count >= 1:
        return 1
    else:
        return 0

if __name__ == '__main__':
    batch_begin = 0
    batch_end = 100
    
    root_dir = "./../files/memleak_files"
    sub_dirs = [sub_dir for sub_dir in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, sub_dir))]
    
    res_dict = {}
    
    print(min(batch_end, len(sub_dirs)))
    
    for i in range(batch_begin, min(batch_end, len(sub_dirs))):
        pull_name = sub_dirs[i]
        sub_dir_path = os.path.join(root_dir, pull_name)
        print(f"FlawFinder analyzing NO.{i}: {sub_dir_path}......")
        res_i = evaluate_flawfinder_effect(sub_dir_path)
        res_dict[pull_name] = res_i
        
    with open("./flawfinder_results.csv", "a", newline="", encoding="utf-8") as flawfinder_res_f:
        writer = csv.writer(flawfinder_res_f)
        for row in res_dict.items():
            writer.writerow(row)