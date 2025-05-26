import os
from unidiff import PatchSet
from unidiff.errors import UnidiffParseError
import lizard
import csv
from lizard import FunctionInfo


def parse_diff(diff_content):
    try:
        patch = PatchSet(diff_content)
    except UnidiffParseError as e:
        print(f"Error parsing diff: {e}")
        return {}

    file_changes = {}
    for file in patch:
        file_path = file.source_file
        if file_path.startswith('a/'):
            file_path = file_path[2:]

        file_name = os.path.basename(file_path)

        changed_lines = []
        for hunk in file:
            # for line in hunk:
            #     if (line.line_type == '+' or line.line_type == '-') and line.source_line_no is not None:
            #         changed_lines.append(line.source_line_no)
            for i in range(0, len(hunk)):
                line = hunk[i]
                if line.line_type == '-' and line.source_line_no is not None:
                    changed_lines.append(line.source_line_no)
                elif line.line_type == '+':
                    if i > 0:
                        prior_line_index = i - 1
                        prior_line_type = hunk[prior_line_index].line_type
                        if prior_line_type == '+' or prior_line_type == '-':
                            continue
                        else:
                            if hunk[prior_line_index].source_line_no is not None:
                                changed_lines.append(hunk[prior_line_index].source_line_no)
                    else:
                        changed_lines.append(1)

        file_changes[file_name] = changed_lines
    return file_changes


def analyze_functions(file_path):
    try:
        analysis = lizard.analyze_file(file_path)
        return analysis.function_list
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return []


def find_affected_functions(changed_lines, functions):
    affected = []

    # for line in changed_lines:
    #     for function in functions:
    #         if function.start_line <= line <= function.end_line:
    #             affected.append(function)
    #             break
    #     global_item = FunctionInfo('*non-function*', '?', line)
    #     affected.append(global_item)
    try:
        for func in functions:
            start, end = func.start_line, func.end_line
            if any(start <= line <= end for line in changed_lines):
                affected.append(func)
                continue
    except Exception as e:
        print(e)

    return list(set(affected))


def find_bug_functions(code_file_path, diff_file_path):
    with open(diff_file_path, 'r', encoding='utf-8', errors='replace') as diff_file:
        diff_content = diff_file.read()

    file_changes = parse_diff(diff_content)
    file_name = os.path.basename(code_file_path)
    if file_name not in file_changes:
        print(f"No changes found for {file_name} in the diff file.")
        return []

    changed_lines = file_changes[file_name]

    functions = analyze_functions(code_file_path)
    affected_functions = find_affected_functions(changed_lines, functions)

    return affected_functions

if __name__ == "__main__":
    batch_size = 10
    root_dir = "./../files/memleak_files"
    sub_dirs = [sub_dir for sub_dir in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, sub_dir))]

    for i in range(0, len(sub_dirs), batch_size):
        batch = sub_dirs[i:i + batch_size]
        for sub_dir in batch:
            sub_dir_path = os.path.join(root_dir, sub_dir)
            print(f"Parsing diff file in {sub_dir_path} of batch index {i}...")
            diff_file_path = os.path.join(sub_dir_path, "patch.diff")
            if os.path.exists(diff_file_path):
                for entry in os.scandir(sub_dir_path):
                    if entry.is_file() and entry.name.endswith((".c", ".cpp", ".h", ".hpp", ".cc")):
                        code_file_path = entry.path
                        affected_functions = find_bug_functions(code_file_path, diff_file_path)

                        csv_file_path = os.path.join(sub_dir_path, "memleak_func.csv")
                        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                            fieldnames = ['File Name', 'Function Signature', 'Start Line', 'End Line']
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            if csvfile.tell() == 0:
                                writer.writeheader()

                            if affected_functions:
                                for func in affected_functions:
                                    signature = func.long_name
                                    writer.writerow({
                                        'File Name': os.path.basename(code_file_path),
                                        'Function Signature': signature,
                                        'Start Line': func.start_line,
                                        'End Line': func.end_line
                                    })
