from openai import OpenAI
import csvHandler

MODEL = "gpt-5-chat-latest"  # You can also try "gpt-5-chat-latest" if Pro access isn’t enabled


def setup_gpt(systemInstruction=None, systemInfo=None):
    
    """
    Initialize GPT client and prepare base message template.
    Returns a list: (client, base_messages)
    """

    client = OpenAI()

    # none provided
    if systemInstruction is None:
        print("No system instruction provided. Returning empty base messages.")
        return client, []
    
    if systemInfo:
        systemInstruction += f"\n\n{systemInfo}"
    
    base_messages = [{"role": "system", "content": systemInstruction}]
    return [client, base_messages]


def askgpt_generate_LTL(client, base_messages, nlprompt: str):

    messages = base_messages + [{"role": "user", "content": nlprompt}]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=150
    )

    msg = response.choices[0].message.content.strip()
    print(f"LTL Result: {msg}")
    return msg


def askgpt_LTL_trueVfalse(client, base_messages, prompt1: str, prompt2: str):
    
    """
    Send a user prompt using an already-initialized GPT session.
    Check if two LTL expressions are equivalent.
    """
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
    variableTableInfo = csvHandler.get_master_variable_table_info() # Adjust path as needed

    # Create GPT sessions once
    ltlClient = setup_gpt(
        systemInstruction=
        (
            "Answer strictly with only the past time LTL formula.\n"
            "You are an expert in formal methods and temporal logic. "
            "Your task is to translate natural language requirements into **past-time linear temporal logic (ptLTL)** formulas.\n\n"
            "Use only ptLTL operators:\n"
            "- H φ: 'Historically φ' (φ has always been true in the past)\n"
            "- O φ: 'Once φ' (φ was true at least once in the past)\n"
            "- Y φ: 'Yesterday φ' (φ was true at the immediately previous step)\n"
            "- φ S ψ: 'φ Since ψ' (ψ was true at some point in the past and φ has been true since then)\n\n"
            "Avoid using standard LTL future-time operators such as G, F, X, U, or □.\n"
            "Use the following variable mapping to understand system variables:"
        ),
        systemInfo=variableTableInfo
    )

    ltlValidityClient = setup_gpt(
        systemInstruction=(
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
        ),
        systemInfo=None
    )

    # Iterate through rows and query GPT ❤ RIP Daniel Naroditsky ❤
    #for entry in csvData:
    entry = csvData[1]
    print(f"\nProcessing: {entry["NL description"]}")
    result = askgpt_generate_LTL(ltlClient[0], ltlClient[1], entry["NL description"])
    print(f"LTL Fasit: {entry["LTL"]}")
    result2 = askgpt_LTL_trueVfalse(ltlValidityClient[0], ltlValidityClient[1], result, entry["LTL"])
        # Optionally store result in entry["Result"] = result
