from openai import OpenAI
import csvHandler
import nuXmvHandler

MODEL = "gpt-5-chat-latest"  # You can also try: "gpt-5" "gpt-5-chat-latest" "gpt-4-turbo" "gpt-5-reasoning"
NUM_ITERATIONS = 1 # Number of iterations for the entire batch process
TEMPERATURE = 0  # Adjust temperature for variability in responses

#VARIABLETABLE = csvHandler.get_master_variable_table_info() # Adjust path as needed
#CSVDATA = csvHandler.load_and_validate_csv("masterFiles/masterUseCaseReq.csv") # Adjust path as needed

VARIABLETABLE = csvHandler.get_lung_ventilator_variable_table_info() # Adjust path as needed
CSVDATA = csvHandler.load_and_validate_csv("lungFiles/lungVentilatorReq.csv") # Adjust path as needed


client = OpenAI()


def askgpt_generate_LTL_batch(nl_descriptions):
    
    combined_prompt = (
        "Translate each of the following natural-language requirements "
        "into its corresponding past-time LTL (ptLTL) formula.\n\n"
        "Return only the formulas, one per line, in the same order.\n"
        "Do not include any numbering, explanations, or LaTeX syntax.\n\n"
        f"Variable mapping:\n{VARIABLETABLE}\n\n"
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
        temperature=TEMPERATURE # maybe change later
    )

    msg = response.choices[0].message.content.strip()
    # print(f"LTL Batch Result: {msg}")
    return msg


# Main execution
if __name__ == "__main__":

    csvData = CSVDATA

    # --- Batch processing with LTL generation and validation ---
    results = []

    # Step 1: Gather all NL descriptions
    nl_descriptions = [entry["NL description"] for entry in csvData]
    ids = [entry["ID"] for entry in csvData]
    ltl_references = [entry["LTL"] for entry in csvData]
    success_counts = {id_: 0 for id_ in ids}

    # Iteration Loop
    for iteration in range(NUM_ITERATIONS):    
        print(f"\n🔁 Iteration {iteration + 1}/{NUM_ITERATIONS}")

        # Step 2: Generate all LTLs in one call
        batch_output = askgpt_generate_LTL_batch(nl_descriptions)

        # Step 3: Split batch output into lines (each should match one NL description)
        generated_formulas = [line.strip() for line in batch_output.split("\n") if line.strip()]

        # Step 4: Handle mismatched counts safely
        if len(generated_formulas) != len(csvData):
            print(f"⚠️ Warning: Expected {len(csvData)} results, got {len(generated_formulas)}")
            generated_formulas = (generated_formulas + ["ERROR"] * len(csvData))[:len(csvData)]

        # Step 5: Validate each generated LTL formula
        for idx, entry in enumerate(csvData):
            reference = ltl_references[idx]
            generated = generated_formulas[idx]

            # Default if no reference
            result2 = "N/A"

            if reference and reference.strip():

                # Run semantic equivalence check
                result2 = nuXmvHandler.check_equivalence_master(generated, reference)
           
                # Increment true count
                if result2 is True:
                    success_counts[ids[idx]] += 1

            # Store results
            results.append({
                "Summary": f"{success_counts[ids[idx]]}/{iteration + 1}",
                "ID": ids[idx],
                "ptLTL": reference if reference else "None",
                "Generated ptLTL": generated,
                "Equivalence Check": result2
            })

    # Step 6: Save results to CSV
    csvHandler.save_results_to_csv(results)