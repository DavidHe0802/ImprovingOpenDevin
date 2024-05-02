# OpenDevin Enhancement Repository

## Overview
This repository is dedicated to enhancing the OpenDevin platform by introducing new test cases, a refined testing pipeline, and a modified agent implementation. The primary goal is to address and improve upon the limitations identified in the current OpenDevin framework.

## Modifications to Agent and Utilities
To integrate the enhancements:
- Replace the existing agent with `agent.py` found in this repository. This should be done at `OpenDevin/agenthub/monologue agent/agent`.
- Replace the utility files `monologue` and `prompt` in `OpenDevin/agenthub/monologue agent/utils` with `monologue.py` and `prompt.py` respectively from this repository.

## Testing Enhancements
Refer to the script `OpenDevin Testing.py` for detailed usage instructions. This script outlines the methodology to apply the testing pipeline and demonstrates the expected outputs when using the enhanced agent and utilities.

## OpenDevin Test Cases
The repository includes a critical set of test cases provided in `OpenDevin Testcases.xlsx`. This set is designed to supplement the existing benchmarks and addresses specific categories that were underrepresented in previous tests:

1. **Variant of Coding Request**: Tests aimed at evaluating the agent’s response to various coding-related queries.
2. **Variant of Non-Coding Request**: Focuses on the agent’s performance with non-coding but technically oriented queries.
3. **Unrelated Question Series**: Assesses the agent's handling of queries that are unrelated to the main context of discussion.
4. **Related Question Series**: Tests the agent's ability to handle a series of related queries, checking for consistency and relevance in the responses.

## Citation
To reference the shortcomings identified in previous benchmarks and the motivation for this new test set, use the following citation:
```latex
\cite{sweBench}
