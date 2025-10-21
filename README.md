## 2nd paper, LLMs capabilities of generating Copilot formally  verified specifications/requirements/monitors.

### Research Questions

RQs:
1. Is it possible to use LLMs to generate Copilot syntax with high reliability and accuracy?
2. What LLM performs the best in generating safety critical code?
3. Is it possible to use LLM technology to continuously improve system requirements during runtime? 

Early thoughts on problem statement:
1. Feasibility: To what extent can large language models generate syntactically correct and semantically valid Copilot specifications and monitors?
2. Comparative performance: Which LLMs (open-source vs. proprietary, instruction-tuned vs. code-specialized) demonstrate the highest reliability and accuracy in producing safety-critical Copilot code?
3. Adaptivity: Can LLMs support continuous refinement of system requirements and runtime monitors during execution, without compromising safety assurance?

Contributions:
Proper use of LLM, going from manual to automated tool chain.

To FRET, To Copilot, or through both



### Methodology

<p align="center">
<img width="512" height="768" align="center" alt="bilde" src="https://github.com/user-attachments/assets/7f77a677-dcb4-4464-9cc8-48a14e30e104" />
</p>



### LLM

1. GPT-4o (OpenAI)
   
	• Best for: Strong reasoning, natural language understanding, and multimodal input (text + images).

	• Why use it: Handles complex technical prompts well, useful for aerospace and mission-planning style queries.

Access: Available via OpenAI API.



### Specifications

System (x requirements)
	- Master case (13)
	- Rover (28)
	- Drone (46)
	- Lung Ventilation (121)



### Testing Results

🔴 **False Positive:**
Processing: While seeing any person the distance to target should be at or above 0.

LTL Result: O(Classifier ≠ 0 → distance_to_target ≥ 0)

LTL Fasit: (H ((! (classifier = 0)) -> (distance_to_target >= 0)))

Equivalence Check: True


🟢 **True Positive:**
Processing: While seeing any person the distance to target should always be at or above 0.

LTL Result: H (Classifier ≠ 0 → distance_to_target ≥ 0)

LTL Fasit: (H ((! (classifier = 0)) -> (distance_to_target >= 0)))

Equivalence Check: True


🟢 **True Negative:**
Processing: While seeing any person the distance to target should once be at or above 0.

LTL Result: O(distance_to_target ≥ 0)

LTL Fasit: (H ((! (classifier = 0)) -> (distance_to_target >= 0)))

Equivalence Check: False

