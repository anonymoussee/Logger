#!/bin/bash

# Default values for script parameters
set -e
set -x

input_file=""
output_file=""
method_signature=""
src_paths_file=""
classpath_entries_file=""
log_matcher=""
target_method_signature=""
output_path=""
hop=2

# Usage message
usage() {
  echo "Usage: $0 [-i <input_file>] [-o <output_file>] [-m <method_signature>] [-s <src_paths_file>] [-c <classpath_entries_file>] [-l <log_matcher>] [-t <target_method_signature>] [-p <output_path>] [-h <hop>]"
  exit 1
}

# Parse script parameters
while getopts ":i:o:m:s:c:l:t:p:h:" opt; do
  case ${opt} in
    i ) input_file=$OPTARG;;
    o ) output_file=$OPTARG;;
    m ) method_signature=$OPTARG;;
    s ) src_paths_file=$OPTARG;;
    c ) classpath_entries_file=$OPTARG;;
    l ) log_matcher=$OPTARG;;
    t ) target_method_signature=$OPTARG;;
    p ) output_path=$OPTARG;;
    h ) hop=$OPTARG;;
    \? ) usage;;
    : ) usage;;
  esac
done

if [[ -z "$input_file" || -z "$output_file" || -z "$method_signature" ]]; then
  usage
fi

if [[ ! -z "$src_paths_file" && ! -z "$classpath_entries_file" ]]; then
  java -jar AvaVarList.jar -i "$input_file" -o "$output_file" -m "$method_signature" -s "$src_paths_file" -c "$classpath_entries_file"
fi

if [[ ! -z "$variable_name" && ! -z "$src_paths_file" && ! -z "$classpath_entries_file" ]]; then
  java -jar VarRefine.jar -i "$input_file" -o "$output_file" -v "$variable_name" -s "$src_paths_file" -c "$classpath_entries_file"
fi

if [[ ! -z "$log_matcher" ]]; then
  python generate_log_methods.py --cg "$input_file" --output "$output_file" --matcher "$log_matcher"
fi

if [[ ! -z "$input_jar_file" && ! -z "$log_methods_file" && ! -z "$output_file" ]]; then
  java -jar LogEPGen.jar -j "$input_jar_file" -l "$log_methods_file" -o "$output_file"
fi

if [[ ! -z "$input_file" && ! -z "$log_file" && ! -z "$target_method_signature" && ! -z "$output_path" ]]; then
  python generate_log_slice.py --call-graph-file "$input_file" --log-file "$log_file" --method "$target_method_signature" --output-path "$output_path" --hop "$hop"
fi
