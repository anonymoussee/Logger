import argparse
import itertools
import json
import os
import random
from collections import defaultdict

import networkx as nx
import pandas as pd
from string import digits

parser = argparse.ArgumentParser(
    description="Generating log sequence for given jar file."
)

parser.add_argument("--call-graph-file", type=str, required=True, help="Path to the call graph file")
parser.add_argument("--log-file", type=str, required=True, help="Path to the log file")
parser.add_argument("--label-file", type=str, required=True, help="Path to the log file")
parser.add_argument("--method", type=str, help="Target method signature")
parser.add_argument("--output-path", type=str, help="Directory to save generated log slice")
parser.add_argument("--hop", type=int, help="Hops for log slicing", default=2)
parser.add_argument("--stopper", type=int, help="Stopper for frequent pattern", default=3)

args = parser.parse_args()

call_graph_file = args.call_graph_file
call_file = args.log_file
label_file = args.label_file
output_dir = args.output_path
stopper = args.stopper
hop = args.hop
target_method = args.method
length = 1000000


def get_file_name(file_dir):
    real_files = []
    for root, _, files in os.walk(file_dir):
        real_files.extend(files)
    return real_files


def log_method_refinement(call_graph_file):
    with open(call_graph_file) as lines:
        edges = list(set(line.strip() for line in lines))

    methods = set()
    for edge in edges:
        caller, callee = edge.split(' ')[0][2:], edge.split(' ')[1][3:]
        if 'logg' in callee.lower():
            methods.add(caller)
    return methods


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return list(zip(a, b))


def analyze_calls(call_signature):
    class_name, method_and_params = call_signature.split(':')
    method_name, params = method_and_params.split('(')
    return f"{class_name} {method_name} {params[:-1]}"


def analyze_soots(soot_signature):
    class_name, method_and_params = soot_signature[1:].split(':')
    method_name, params = method_and_params.split('(')
    return f"{class_name} {method_name.split(' ')[-1]} {params[:-2]}"


def clean_call(call):
    cleaned_call = ''.join([char for char in call if char not in digits])
    cleaned_call = cleaned_call.replace('"', '')
    return cleaned_call.replace('$stack', '<*>')

def log_generator_raw(method, called_method, current_path):
    if not method['CallSequences']:
        return
    call_sequence = random.choice(method['CallSequences'])
    for call in call_sequence:
        if not call:
            current_path.append((call, method['Method']))
            continue
        if call[0] == '<':  # method
            if call in method['CallInLoops']:
                called_method[call].append(1)
                if len(called_method[call]) > stopper:
                    continue
                loop = random.randint(1, 3)
                for _ in range(loop):
                    log_generator_raw(sub_graph_dict[analyze_soots(call)], called_method, current_path)
            else:
                called_method[method['Method']].append(1)
                if len(called_method[call]) > 3:
                    continue
                log_generator_raw(sub_graph_dict[analyze_soots(call)], called_method, current_path)
        else:  # log
            new_call = clean_call(call)
            if call in method['CallInLoops']:
                loop = random.randint(1, 3)
                for _ in range(loop):
                    current_path.append((new_call, method['Method']))
            else:
                current_path.append((new_call, method['Method']))



def find_logs_around_method(log_sequence, method, hops):
    logs_around_method = []
    for i, (log, method_name) in enumerate(log_sequence):
        if method in method_name:
            start = max(0, i - hops)
            end = min(len(log_sequence), i + hops + 1)
            logs_around_method.extend(log_sequence[start:end])



if __name__ == '__main__':
    label_data = pd.read_csv(label_file)
    log_level_dict = defaultdict(str)
    log_method_dict = defaultdict(str)
    for i in range(len(label_data)):
        key = label_data['Log'][i]
        new_call = clean_call(key)
        log_level_dict[new_call] = label_data['LoggingLevel'][i]
        log_method_dict[new_call] = label_data['Method'][i]

    with open(call_graph_file) as lines:
        edges = list(set(line.strip() for line in lines))

    G = nx.DiGraph()
    for edge in edges:
        caller, callee = edge.split(' ')[0][2:], edge.split(' ')[1][3:]
        G.add_edge(analyze_calls(caller), analyze_calls(callee))

    sub_graph_dict = dict()
    with open(call_file, 'r') as f:
        call_data = f.readlines()

    for calldata in call_data:
        data = json.loads(calldata)
        sub_graph_dict[analyze_soots(data['Method'])] = data

    remove_list = [node for node in G.nodes if node not in sub_graph_dict.keys()]
    for node in remove_list:
        G.remove_node(node)

    roots_temp = list(G.nodes)

    i = 0
    length_stat = []
    while sum(length_stat) < length:
        called_method = defaultdict(list)
        root = random.choice(roots_temp)
        method = sub_graph_dict[root]
        current_path = []
        if method['CallSequences']:
            called_method[method['Method']].append(1)
            try:
                log_generator_raw(method, called_method, current_path)
            except:
                continue
            if len(current_path) > 0:
                i += 1
                length_stat.append(len(current_path))
                content = str(i)
                for log, method_name in current_path:
                    if log_level_dict[log]:
                        with open(os.path.join(output_dir, "all_logs.txt"), "a") as f:
                            f.write(f"{log_level_dict[log].upper()} {method_name[1:-1].split(':')[0]}: {log}\n")

                logs_around_method = find_logs_around_method(current_path, target_method, hop)
                with open(os.path.join(output_dir, "logs_around_method.txt"), "a") as f:
                    for log, method_name in logs_around_method:
                        f.write(f"{log_level_dict[log].upper()} {method_name[1:-1].split(':')[0]}: {log}\n")
