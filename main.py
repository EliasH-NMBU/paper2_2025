from openai import OpenAI
import csvHandler

MODEL = "gpt-5-chat-latest"  # You can also try "gpt-5-chat-latest" if Pro access isn’t enabled


def setup_gpt(systemInstruction=None, systemInfo=None):
    """
    Initialize GPT client and prepare base message template.
    Returns a tuple: (client, base_messages)
    """
    client = OpenAI()

    # none provided
    if systemInstruction is None:
        print("No system instruction provided. Returning empty base messages.")
        return client, []
    
    if systemInfo is not None:
        systemInstruction += f"\n\n \n{systemInfo}"
    
    base_messages = [{"role": "system", "content": systemInstruction}]
    return client, base_messages


def askgpt_LTL_trueVfalse(client, base_messages, prompt: str, promt2: str):
    
    """
    Send a user prompt using an already-initialized GPT session.
    Check if two LTL expressions are equivalent.
    """

    messages = base_messages + [{"role": "user", "content": prompt + promt2}]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=50
    )

    msg = response.choices[0].message.content.strip()
    print(f"Response: {msg}")
    return msg


def askgpt_generate_LTL(client, base_messages, nlprompt: str):
    
    """
    Send a user prompt using an already-initialized GPT session.
    Natural Language to LTL conversion.
    """

    messages = base_messages + [{"role": "user", "content": nlprompt}]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=100
    )

    msg = response.choices[0].message.content.strip()
    print(f"Response: {msg}")
    return msg


# Main execution
if __name__ == "__main__":

    csvData = csvHandler.load_and_validate_csv("masterFiles/masterUseCaseReq.csv") # Adjust path as needed

    ltlClient, base_messages_gen_ltl = setup_gpt(systemInstruction="Answer strictly with the LTL formula. Given this table with variables to work with, can you formalize the natural language requirement of the system into its respective LTL counterpart?:", systemInfo=None)
    ltlValidityClient, base_messages_tvf_ltl = setup_gpt(systemInstruction="Answer strictly with only 'True' or 'False'. Determine if the given LTL expressions express the same behavior.", systemInfo=None)

    # Iterate through rows and query GPT
    #for entry in csvData:
    print(f"\nProcessing: {csvData[0]["NL description"]}")
    result = askgpt_generate_LTL(ltlClient, base_messages_gen_ltl, csvData[0]["NL description"])
    result2 = askgpt_LTL_trueVfalse(ltlValidityClient, base_messages_tvf_ltl, result, csvData[0]["LTL formula"])
        # Optionally store result in entry["Result"] = result
