import csv
import subprocess
import xml.etree.ElementTree as ET
import pandas as pd
import os

from analyze.Leak_CWE import LEAK_CWE

MISSING_RELATED_ID = ["unknownMacro"]


def run_cppcheck(folder_path):
    output_file = os.path.join(folder_path, "cppcheck_result.xml")

    # if os.path.exists(output_file):
    #     print(f"Already exists: {output_file}")
    #     return output_file

    try:
        source_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith((".h", ".hpp", ".c", ".cpp", ".cc")):
                    source_files.append(os.path.join(root, file))

        check_paths = source_files.copy()

        command = [
            "cppcheck",
            *check_paths,
            "--xml-version=2",
            f"--output-file={output_file}",
            "--verbose",
            "--check-level=exhaustive",
            "--enable=warning",
            "--inconclusive"
        ]

        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # print(f"Cppcheck analysis completed. Results saved to {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running cppcheck: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return output_file


def parse_cppcheck_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        data = []
        for error in root.findall('.//error'):
            severity = error.get('severity')
            id_ = error.get('id')
            if severity in ['error', 'warning'] and id_ not in MISSING_RELATED_ID:
                msg = error.get('msg')
                verbose = error.get('verbose')
                for location in error.findall('location'):
                    file_ = os.path.basename(location.get('file'))
                    line = location.get('line')
                    cwe = error.get('cwe')
                    data.append({
                        'id': id_,
                        'severity': severity,
                        'msg': msg,
                        'verbose': verbose,
                        'cwe': cwe,
                        'file': file_,
                        'line': line
                    })

        return pd.DataFrame(data)
    except Exception as e:
        print(f"An error occurred while parsing the XML file: {e}")
        return pd.DataFrame()


def cppcheck_analyze(dir_name):
    xml_output = run_cppcheck(dir_name)
    if xml_output:
        return parse_cppcheck_xml(xml_output)
    return pd.DataFrame()


def evaluate_cppcheck_effect(dir_path):
    df_cppcheck = cppcheck_analyze(dir_path)

    if len(df_cppcheck) == 0:
        return 0

    csv_path = os.path.join(dir_path, 'memleak_func.csv')

    if not os.path.isfile(csv_path):
        print(f'{csv_path} file not exist')
        return 0

    df_memleak = pd.read_csv(csv_path)

    df_memleak['Start Line'] = pd.to_numeric(df_memleak['Start Line'], errors='coerce')
    df_memleak['End Line'] = pd.to_numeric(df_memleak['End Line'], errors='coerce')
    df_cppcheck['line'] = pd.to_numeric(df_cppcheck['line'], errors='coerce')

    leak_functions = df_memleak.shape[0]

    # global
    if leak_functions == 0:
        if any(cwe in LEAK_CWE for cwe in df_cppcheck['cwe'].dropna()):
            return 4

    correctly_marked_count = 0
    marked_count = 0

    for _, row_leak in df_memleak.iterrows():
        file_name = row_leak['File Name']
        start_line = row_leak['Start Line']
        end_line = row_leak['End Line']

        df_filtered = df_cppcheck[
            (df_cppcheck['file'] == file_name) &
            (df_cppcheck['line'] >= start_line) &
            (df_cppcheck['line'] <= end_line)
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
        print(f"CPPCheck analyzing NO.{i}: {sub_dir_path}......")
        res_i = evaluate_cppcheck_effect(sub_dir_path)
        res_dict[pull_name] = res_i

    with open("./cppcheck_results.csv", "a", newline="", encoding="utf-8") as cppcheck_res_f:
        writer = csv.writer(cppcheck_res_f)
        for row in res_dict.items():
            writer.writerow(row)

