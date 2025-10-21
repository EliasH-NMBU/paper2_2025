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
            "Answer strictly with only the LTL formula.\n"
            "You are a model that formalizes natural language requirements into LTL expressions "
            "using the provided variable mapping."
        ),
        systemInfo=variableTableInfo
    )

    ltlValidityClient = setup_gpt(
        systemInstruction=
        "Answer strictly with only 'True' or 'False'. Determine if two LTL expressions represent the same logic.",
        systemInfo=None
    )

    # Iterate through rows and query GPT
    #for entry in csvData:
    entry = csvData[0]
    print(f"\nProcessing: {entry["NL description"]}")
    result = askgpt_generate_LTL(ltlClient[0], ltlClient[1], entry["NL description"])
    result2 = askgpt_LTL_trueVfalse(ltlValidityClient[0], ltlValidityClient[1], result, entry["LTL formula"])
        # Optionally store result in entry["Result"] = result
