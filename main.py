from openai import OpenAI
import csvHandler

MODEL = "gpt-5-chat-latest"  # You can also try "gpt-5-chat-latest" if Pro access isn’t enabled

def setup_gpt(systemInstruction=None, systemInfo=None):
    """
    Initialize GPT client and prepare base message template.
    Returns a tuple: (client, base_messages)
    """
    client = OpenAI()

    # default system instruction if none provided
    if systemInstruction is None:
        systemInstruction = "Answer strictly with 'True' or 'False'. Do these two expressions achieve the same logic?"

    base_messages = [{"role": "system", "content": systemInstruction}]
    return client, base_messages


def ask_gpt_trueVfalse(client, base_messages, prompt: str):
    """
    Send a user prompt using an already-initialized GPT session.
    """
    messages = base_messages + [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=50
    )
    msg = response.choices[0].message.content.strip()
    print(f"Response: {msg}")
    return msg

# Main execution
if __name__ == "__main__":

    csvData = csvHandler.load_and_validate_csv("masterFiles/masterUseCaseReq.csv") # Adjust path as needed
    for entry in csvData:
        print(f"NL description: {entry['NL description']} \n")


    client, base_messages_logic = setup_gpt(systemInstruction="Answer only 'True' or 'False'.")
    client, base_messages_ltl = setup_gpt(systemInstruction="Generate an LTL expression for the described behavior.", systemInfo=None)

    # Iterate through rows and query GPT
    for entry in csvData:
        nl_text = entry["NL description"]
        print(f"\nProcessing: {nl_text}")
        result = ask_gpt_trueVfalse(client, base_messages_ltl, nl_text)
        # Optionally store result in entry["Result"] = result
