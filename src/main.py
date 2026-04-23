from openai import OpenAI
import csvHandler
import nuXmvHandler

MODEL = "gpt-5-chat-latest"  # You can also try: "gpt-5" "gpt-5-chat-latest" "gpt-4-turbo" "gpt-5-reasoning"
SPEC = "Mars_tempTest"
NUM_ITERATIONS = 50 # Number of iterations for the entire batch process
TEMPERATURE = 0  # Adjust temperature for variability in responses
EQUIVALENCE_HANDLER = nuXmvHandler.check_equivalence_rover
    



### Load CSV data and variable table
#VARIABLETABLE = csvHandler.get_master_variable_table_info()
#CSVDATA = csvHandler.load_and_validate_csv("masterFiles/masterUseCaseReq.csv")

#VARIABLETABLE = csvHandler.get_lung_ventilator_variable_table_info()
#CSVDATA = csvHandler.load_and_validate_csv("lungFiles/lungVentilatorReq.csv")

#VARIABLETABLE = csvHandler.get_rover_variable_table_info()
#CSVDATA = csvHandler.load_and_validate_csv("roverFiles/roverReq.csv")

#VARIABLETABLE = csvHandler.get_abzrover_variable_table_info()
#CSVDATA = csvHandler.load_and_validate_csv("abzRoverFiles/abzRoverReq.csv")

VARIABLETABLE = csvHandler.get_rover_variable_table_info()
CSVDATA = csvHandler.load_and_validate_csv("roverFiles/roverReq.csv")
###


client = OpenAI()


def askgpt_generate_LTL_batch(nl_descriptions):
    
    combined_prompt = (
        "Translate each of the following natural-language requirements "
        "into its corresponding past-time LTL (ptLTL) formula.\n\n"
        "Return only the formulas, one per line, in the same order.\n"
        "Do not include any numbering, explanations, or LaTeX syntax.\n\n"
        "Strictly use variables from the following variable mapping:\n"
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
            "Avoid using standard LTL future-time operators such as F, X, U, or □.\n"
            )},
        {"role": "user", "content": combined_prompt}
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=16384,
        temperature=TEMPERATURE # maybe change later
    )

    msg = response.choices[0].message.content.strip()
    # print(f"LTL Batch Result: {msg}")
    return msg



def chunk_list(lst, chunk_size):
    
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size], i



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
        print(f"\n Iteration {iteration + 1}/{NUM_ITERATIONS}")

        CHUNK_SIZE = 5  # 3–10 works well

        for chunk, base_idx in chunk_list(nl_descriptions, CHUNK_SIZE):

            print(f"  Processing rows {base_idx} → {base_idx + len(chunk) - 1}")

            batch_output = askgpt_generate_LTL_batch(chunk)

            generated_formulas = [
                line.strip() for line in batch_output.split("\n") if line.strip()
            ]

            # Safety guard
            if len(generated_formulas) != len(chunk):
                print(
                    f"Warning: Expected {len(chunk)} results, got {len(generated_formulas)}"
                )
                generated_formulas = (
                    generated_formulas + ["ERROR"] * len(chunk)
                )[:len(chunk)]

            # Validate each generated LTL formula
            for local_idx, generated in enumerate(generated_formulas):
                global_idx = base_idx + local_idx

                entry = csvData[global_idx]
                reference = ltl_references[global_idx]
                req_id = ids[global_idx]
                print(f"    ID {req_id}: Generated ptLTL: {generated}   Reference ptLTL: {reference}")
                result2 = "N/A"

                if reference and reference.strip():
                    result2 = EQUIVALENCE_HANDLER(reference, generated)

                    if result2 is True:
                        success_counts[req_id] += 1
                
                if result2 != "N/A":
                    results.append({
                        "Summary": f"{success_counts[req_id]}/{iteration + 1}",
                        "ID": req_id,
                        "ptLTL": reference if reference else "None",
                        "Generated ptLTL": generated,
                        "Equivalence Check": result2
                    })


    # Step 6: Save results to CSV
    csvHandler.save_results_to_csv(results, temperature=str(TEMPERATURE), model=SPEC)