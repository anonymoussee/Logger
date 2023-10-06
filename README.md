# SCLogger

This is the anonymous replication package for the FSE2024 submission "Go Static: Contextualized Logging Statement Generation". In this paper, we propose SCLogger, the first  logging statement generation approach powered by inter-method static contexts.

SCLogger consists of four phases: static scope extension, logging style adaption, contextulized prompt construction, logging variable refinement.

We will maintain this open source tool once the paper get accepted and continue improve the tool for further practical application.

![overview](Figure/logger_overview.jpg)

## Repository Organization
```bash
├── Baselines # Baselines
│   ├── GPT-3.5.py
│   ├── GPT-4.py
│   ├── davinci-003.py
│   ├── lance
│   │   ├── README.md
│   │   └── lance.py
│   ├── lance2
│   │   └── lance2.py
│   ├── lance_eva
│   └── llama2.py
├── Build
│   ├── AvaVarList.jar # Available variable list
│   ├── CodeSlicer.jar  # Code graph and slicing
│   ├── LogEPGen.jar # Log graph and slicing
│   ├── LogStatGen.jar # Log graph and slicing
│   └── VarRefine.jar # Variable refinement
├── Figure
│   ├── logger_overview.jpg
│   └── logger_overview.pdf
├── README.md
├── Scripts
│   ├── demo_case_selection.py
│   ├── generate_log_slice.py
│   └── log_methods_generator.py
│   └── run.sh
├── Src
│   ├── CodeSlicer # Code graph and slicing
│   │   ├── Analyzer
│   │   │   └── util
│   │   │       └── MethodFinder.java
│   │   └── CodeSlicer.java
│   ├── LogGraph # Log graph and slicing
│   │   ├── LogEPGen.java
│   │   ├── LogStatGen.java
│   │   ├── OptionsCfg.java
│   │   ├── Util
│   │   │   ... 
│   │   ├── analyseDepth
│   │   │  ... # Constraint solving
│   └── Var
│       ├── AvaVarList.java # Available variable list
│       └── VarRefine.java # Variable refinement
└── ThirdParty
    ├── javacg-0.1-SNAPSHOT-static.jar
    └── soot-4.3.0-jar-with-dependencies.jar
```

## Datasets

Please download the processed datasets from [ProjectsSRC](https://drive.google.com/file/d/13f1qzi3Il5LHdeIiE7jw1cZTXo5PSwF_/view?usp=sharing), [ProcessedDatasets](https://drive.google.com/file/d/1sKaj_Bn1xYtACHQk2j7tIAQr5bGabBdw/view?usp=sharing) and then unzip these datasets into the directory of `./ProjectsSRC` and `./ProcessedDatasets`.

## Baselines

All baselines we used are reimplemented in the folder `./Baselines.`

## Static Analysis Part
We have packaged all the static analysis related Java code with all required dependencies into JARs for reproduction, you can refer these Jars in folder `./Build`. All the correpsonding code are shown in folder `./Src`.

### Code Slicing
Instruction for running the callgraph generators:

```bash
java -jar javacg-0.1-SNAPSHOT-static.jar project1.jar ... > cg.txt
```
Instruction for generate code slice:

```bash
java -jar CodeSlicer.jar -i cg.txt -m methodSignature -d projectSrcDir
```


### Log Slicing

Instruction for pruning log-related call graphs:

```bash
python generate_log_methods.py --cg cg.txt --output log_methods.csv --matcher 'log'
```

Instruction for getting log paths:

```bash
java -jar LogEPGen.jar -j input_jar.jar -l log_methods.txt -o log_file.json
```

Instruction for the generate and slice log graphs:

```bash
python generate_log_slice.py --call-graph-file cg.txt --log-file log_file.json --method target_method_signature --output-path ./prompts --hop 2
```


### Available Variable List
Instruction for getting available variable list:
```bash
java -jar AvaVarList.jar -i inputFilePath -o outputFilePath -m methodName -s srcPathsFilePath -c classpathEntriesFilePath
```

### Variable Refinement
Instruction for getting detailed variable information:
```bash
java -jar VarRefine.jar -i inputFilePath -o outputFilePath -v variableName -s srcPathsFilePath -c classpathEntriesFilePath
```

## Prompt Generation
We offer one-click execution script for all componenets and can generate corresponding prompts for given target method.
