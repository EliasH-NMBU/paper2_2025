from openai import OpenAI
import csvHandler
import nuXmvHandler

MODEL = "gpt-5-chat-latest"
NUM_ITERATIONS = 100
TEMPERATURE = 2
EQUIVALENCE_HANDLER = nuXmvHandler.check_equivalence_pipeline

client = OpenAI()


def run_full_ptltl_cycle(client):
    """
    Executes the full pipeline stage:
    1. GPT generates ptLTL from scratch (using only variable_1…variable_6)
    2. GPT translates ptLTL -> natural language
    3. GPT translates NL -> ptLTL again
    4. NuXMV checks syntactic correctness of both ptLTL formulas
    """

    # ============================================================
    # Step 1 — Generate a random ptLTL formula
    # ============================================================
    gen_prompt = (
        "Generate a single realistic **past-time LTL (ptLTL)** requirement.\n"
        "The goal is to produce a syntactically valid ptLTL formula using only these variables:\n\n"
        "variable_1 (input integer)\n"
        "variable_2 (integer)\n"
        "variable_3 (bool)\n"
        "variable_4 (bool)\n"
        "variable_5 (integer constant)\n"
        "variable_6 (internal integer)\n\n"
        "Use only ptLTL operators:\n"
        "- H φ (Historically)\n"
        "- O φ (Once)\n"
        "- Y φ (Yesterday)\n"
        "- φ S ψ (Since)\n\n"
        "Constraints:\n"
        "- Provide **only the formula** on a single line.\n"
    )

    step1 = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You generate realistic ptLTL requirements."},
            {"role": "user", "content": gen_prompt}
        ],
        max_completion_tokens=512,
        temperature=0
    )

    ptltl_1 = step1.choices[0].message.content.strip()


    # ============================================================
    # Step 2 — Convert ptLTL → natural language
    # ============================================================
    step2_prompt = (
        "Convert the following ptLTL requirement into natural language.\n"
        "Write a natural-language description that sounds like the requirement.\n"
        "Make sure to strictly keep the variable names as they are and don't add any other variables. Do not use markdown formatting. No bold, italics, headers, commas, semi comma, or lists. \n\n"
        f"Formula:\n{ptltl_1}"
    )

    step2 = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You convert temporal logic into natural language."},
            {"role": "user", "content": step2_prompt}
        ],
        max_completion_tokens=512,
       temperature=0
    )

    nl_description = step2.choices[0].message.content.strip()


    # ============================================================
    # Step 3 — Convert NL → ptLTL again
    # ============================================================
    step3_prompt = (
        "Translate the following natural-language requirement into a plain-text "
        "past-time LTL (ptLTL) formula.\n\n"

        "Generate a single realistic **past-time LTL (ptLTL)** requirement.\n"
        "The goal is to produce a syntactically valid ptLTL formula using only these variables:\n\n"
        "variable_1 (input integer)\n"
        "variable_2 (integer)\n"
        "variable_3 (bool)\n"
        "variable_4 (bool)\n"
        "variable_5 (integer constant)\n"
        "variable_6 (internal integer)\n\n"
        "Use only ptLTL operators:\n"
        "- H φ (Historically)\n"
        "- O φ (Once)\n"
        "- Y φ (Yesterday)\n"
        "- φ S ψ (Since)\n\n"
        "Constraints:\n"
        "- Provide **only the formula** on a single line.\n"
        "- The formula must look realistic as part of a safety-critical embedded system. Strictly only deliver the ptLTL formula.\n"
        f"Requirement:\n{nl_description}"
    )


    step3 = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You translate natural language back into ptLTL."},
            {"role": "user", "content": step3_prompt}
        ],
        max_completion_tokens=512,
        temperature=TEMPERATURE
    )

    ptltl_2 = step3.choices[0].message.content.strip()


    print(f"\nGenerated ptLTL 1: {ptltl_1}")
    print(f"\nGenerated ptLTL 2: {ptltl_2}")

    # ============================================================
    # Step 4: NuXMV equivalence check
    # ============================================================
    equivalence = EQUIVALENCE_HANDLER(ptltl_1, ptltl_2)

    if equivalence is not True and equivalence is not False:
        return
    print(f"\nEquivalence Check Result: {equivalence}")

    return ptltl_1, nl_description, ptltl_2, equivalence



# ==================================================================
# MAIN LOOP WITH SUMMARY AND CSV SAVE
# ==================================================================
if __name__ == "__main__":

    results = []
    true_count = 0
    iteration = 0

    while iteration < NUM_ITERATIONS:
        print(f"\n=== Iteration {iteration+1}/{NUM_ITERATIONS} ===")

        cycleData = run_full_ptltl_cycle(client)
        if not cycleData:
            print("⚠️  Skipping iteration due to error in equivalence check.")
            continue

        ptltl_1, nl_desc, ptltl_2, equivalence = cycleData

        if equivalence is True:
            true_count += 1
        
        nl_desc = nl_desc.replace("\n", " ").replace(",", ";")

        # Build CSV row using your required schema
        results.append({
            "Summary": f"{true_count}/{iteration+1}",
            "ID": nl_desc,
            "ptLTL": ptltl_1,
            "Generated ptLTL": ptltl_2,
            "Equivalence Check": equivalence
        })
        iteration += 1


    # Save to CSV using your existing function
    csvHandler.save_results_to_csv(results, temperature=str(TEMPERATURE), model="pipeline")