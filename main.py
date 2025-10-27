from openai import OpenAI
import csvHandler

MODEL = "gpt-5-chat-latest"  # You can also try "gpt-5-chat-latest" if Pro access isn’t enabled
client = OpenAI()


def askgpt_generate_LTL(nlprompt: str):
    
    variableTableInfo = csvHandler.get_master_variable_table_info() # Adjust path as needed

    system_prompt = (
        "Answer strictly with only the past time LTL formula.\n"
        "You are an expert in formal methods and temporal logic. "
        "Your task is to translate natural language requirements into **past-time linear temporal logic (ptLTL)** formulas.\n\n"
        "Use only ptLTL operators:\n"
        "- H φ: 'Historically φ' (φ has always been true in the past)\n"
        "- O φ: 'Once φ' (φ was true at least once in the past)\n"
        "- Y φ: 'Yesterday φ' (φ was true at the immediately previous step)\n"
        "- φ S ψ: 'φ Since ψ' (ψ was true at some point in the past and φ has been true since then)\n\n"
        "Avoid using standard LTL future-time operators such as G, F, X, U, or □.\n"
        "Use the following variable mapping to understand system variables:\n"
        f"{variableTableInfo}\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": nlprompt}
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=500
    )

    msg = response.choices[0].message.content.strip()
    print(f"LTL Result: {msg}")
    return msg


def askgpt_generate_LTL_batch(nl_descriptions):
    
    variableTableInfo = csvHandler.get_master_variable_table_info() # Adjust path as needed

    combined_prompt = (
        "Translate each of the following natural-language requirements "
        "into its corresponding past-time LTL (ptLTL) formula.\n\n"
        "Return only the formulas, one per line, in the same order.\n"
        "Do not include any numbering, explanations, or LaTeX syntax.\n\n"
        "Use only ptLTL operators:\n"
        "- H φ: 'Historically φ'\n"
        "- O φ: 'Once φ'\n"
        "- Y φ: 'Yesterday φ'\n"
        "- φ S ψ: 'φ Since ψ'\n\n"
        f"Variable mapping:\n{variableTableInfo}\n\n"
    )

    for i, desc in enumerate(nl_descriptions, 1):
        combined_prompt += f"{i}. {desc}\n"

    messages = [
        {"role": "system", "content": ("You are an expert in formal methods and temporal logic. "
            "Your task is to translate natural language requirements into **past-time linear temporal logic (ptLTL)** formulas.\n\n"
            "Use only ptLTL operators:\n"
            "- H φ: 'Historically φ' (φ has always been true in the past)\n"
            "- O φ: 'Once φ' (φ was true at least once in the past)\n"
            "- Y φ: 'Yesterday φ' (φ was true at the immediately previous step)\n"
            "- φ S ψ: 'φ Since ψ' (ψ was true at some point in the past and φ has been true since then)\n\n"
            "Avoid using standard LTL future-time operators such as G, F, X, U, or □.\n"
            )},
        {"role": "user", "content": combined_prompt}
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=3000,
        temperature=0 # maybe change later
    )

    msg = response.choices[0].message.content.strip()
    print(f"LTL Batch Result: {msg}")
    return msg


def askgpt_LTL_trueVfalse(prompt1: str, prompt2: str):
    
    base_messages = [{"role": "system", "content": 
        (
        "You are an expert in formal verification using **past-time linear temporal logic (ptLTL)**. "
        "Your task is to check whether two ptLTL formulas are *semantically equivalent* — not just syntactically similar.\n\n"
        "Use strict semantics:\n"
        "- `H φ` (Historically φ): means φ has been true at **all** previous time points.\n"
        "- `O φ` (Once φ): means φ was true at **least one** previous time point.\n"
        "- Therefore, `H φ` is **stronger** than `O φ` — they are **not equivalent**.\n"
        "- Similarly, check for differences between future-time and past-time operators (G vs H, F vs O, etc.).\n\n"
        "When comparing two formulas:\n"
        "1. If one formula uses a past operator (H, O, Y, S) and the other uses a future operator (G, F, X, U), respond 'False'.\n"
        "2. If one uses 'H' and the other 'O' around the same condition, respond 'False'.\n"
        "3. Only answer 'True' if the two formulas are **semantically identical** — not merely similar.\n\n"
        "Answer strictly with only 'True' or 'False'. Do not provide explanations."
        )
    }]

    merged_prompt = f"Expression 1: {prompt1}\nExpression 2: {prompt2}"

    messages = base_messages + [{"role": "user", "content": merged_prompt}]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=100
    )

    msg = response.choices[0].message.content.strip()
    print(f"Equivalence Check: {msg}")
    return msg


# Main execution
if __name__ == "__main__":

    csvData = csvHandler.load_and_validate_csv("masterFiles/masterUseCaseReq.csv") # Adjust path as needed

    # Iterate through rows and query GPT 
    results = []
    for entry in csvData:
        print(f"\nProcessing: {entry["NL description"]}")
        result = askgpt_generate_LTL(entry["NL description"])
        print(f"LTL Fasit: {entry["LTL"]}")
        result2 = askgpt_LTL_trueVfalse(result, entry["LTL"])
        
        # Store result
        results.append(
        {
            "ID": entry["ID"],
            "ptLTL": entry["LTL"],
            "Generated ptLTL": result,
            "Equivalence Check": result2
        })

    # Save entry["ID"], entry["LTL"], result, result2 to a new CSV or data structure
    csvHandler.save_results_to_csv(results)