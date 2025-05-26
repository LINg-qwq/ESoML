import os

import lizard
from unidiff import PatchSet
from unidiff.errors import UnidiffParseError


def parse_diff(diff_content):
    try:
        patch = PatchSet(diff_content)
    except UnidiffParseError as e:
        print(f"Error parsing diff: {e}")
        return {}

    file_changes = {}
    for file in patch:
        file_path = file.target_file
        if file_path.startswith('b/'):
            file_path = file_path[2:]

        file_name = os.path.basename(file_path)

        changed_lines = []
        for hunk in file:
            for line in hunk:
                if line.line_type == '+' and line.target_line_no is not None:
                    changed_lines.append(line.target_line_no)
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
    for func in functions:
        start, end = func.start_line, func.end_line
        if any(start <= line <= end for line in changed_lines):
            affected.append(func)
    return affected


def get_function_signature(func):
    return f"{func.name}({func.parameters})"


# def main(diff_content):
def main(owner, repo, pull_id):
    os.chdir(f"./../files/memleak_files/{owner}-{repo}-{pull_id}")

    diff_content = ""
    with open(f"./patch.diff", 'r') as diff_file:
        diff_content = diff_file.read()
        diff_file.close()

    file_changes = parse_diff(diff_content)

    if not file_changes:
        print("No valid diff content found.")
        return

    for file_name, lines in file_changes.items():
        if not lines:
            continue

        print(f"Analyzing file: {file_name}")
        functions = analyze_functions(f"./{file_name}")
        if not functions:
            print("  No functions found.")
            continue

        affected = find_affected_functions(lines, functions)
        if not affected:
            print("  No affected functions detected.")
            continue

        print(f"  Modified functions ({len(affected)}):")
        for func in affected:
            signature = get_function_signature(func)
            print(f"    - {signature} (Lines {func.start_line}-{func.end_line})")


if __name__ == "__main__":
    main("opencv", "opencv", "10919")

