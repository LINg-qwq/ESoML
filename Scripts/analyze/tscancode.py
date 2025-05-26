import subprocess
import xml.etree.ElementTree as ET
import os
import csv
import pandas as pd
from analyze.Leak_CWE import LEAK_CWE

ANALYZER_PATH = ""


def run_tscancode(folder_path):
    output_file = os.path.join(folder_path, "tscancode_result.xml")

    try:
        command = [
            ANALYZER_PATH,
            "--enable=warning",
            folder_path,
            "--xml",
            "2>",
            output_file
        ]

        subprocess.run(" ".join(command), shell=True, check=True)
        return output_file

    except Exception as e:
        print(f"Exception: {e}")
    return None


def parse_tscancode_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        data = []
        for error in root.findall('error'):
            severity = error.get('severity')
            if severity in ['Critical', 'Serious', 'Warning']:
                msg = error.get('msg')
                file_ = os.path.basename(error.get('file'))
                line = error.get('line')
                id_ = error.get('id')
                data.append({
                    'severity': severity,
                    'msg': msg,
                    'file': file_,
                    'line': line,
                    'id': id_
                })

        return pd.DataFrame(data)
    except Exception as e:
        print(f"Exception: {e}")
        return pd.DataFrame()


def tscancode_analyze(dir_name):
    xml_output = run_tscancode(dir_name)
    if xml_output:
        return parse_tscancode_xml(xml_output)
    return pd.DataFrame()


def evaluate_tscancode_effect(dir_path):
    df_tscancode = tscancode_analyze(dir_path)

    if len(df_tscancode) == 0:
        return 0

    csv_path = os.path.join(dir_path, 'memleak_func.csv')

    if not os.path.isfile(csv_path):
        print(f'{csv_path} file not exist')
        return 0

    df_memleak = pd.read_csv(csv_path)

    df_memleak['Start Line'] = pd.to_numeric(df_memleak['Start Line'], errors='coerce')
    df_memleak['End Line'] = pd.to_numeric(df_memleak['End Line'], errors='coerce')
    df_tscancode['line'] = pd.to_numeric(df_tscancode['line'], errors='coerce')

    leak_functions = df_memleak.shape[0]

    if leak_functions == 0:
        if any(id_ == 'memory leak' for id_ in df_tscancode['id'].dropna()):
            return 4

    correctly_marked_count = 0
    marked_count = 0

    for _, row_leak in df_memleak.iterrows():
        file_name = row_leak['File Name']
        start_line = row_leak['Start Line']
        end_line = row_leak['End Line']

        df_filtered = df_tscancode[
            (df_tscancode['file'] == file_name) &
            (df_tscancode['line'] >= start_line) &
            (df_tscancode['line'] <= end_line)
            ]

        if not df_filtered.empty:
            marked_count += 1
            if any(id_ == 'memory leak' for id_ in df_filtered['id'].dropna()):
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
        print(f"TscanCode analyzing NO.{i}: {sub_dir_path}......")
        res_i = evaluate_tscancode_effect(sub_dir_path)
        res_dict[pull_name] = res_i

    with open("./tscancode_results.csv", "a", newline="", encoding="utf-8") as tscancode_res_f:
        writer = csv.writer(tscancode_res_f)
        for row in res_dict.items():
            writer.writerow(row)
