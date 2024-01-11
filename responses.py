import openai

from nltk.tokenize import word_tokenize

openai.api_key = "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" #RandomWurks

async def summarize_messages (history) :

    chat = ""
    for i in range (len(history)) :
        chat += history[i] + "\n"

    # print("STARTING OPENAI")
    tokens = word_tokenize(chat)
    print(f"Length: {len(tokens)}");


    response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo", # Can be replaced by other models for cheaper/better results!
    messages = [
            {"role": "system", "content": "You are a TLDR Bot, a summary bot running in Discord."},
            {"role": "user", "content": "Summarize the given text: " + chat}
        ]
    )

    print(f"Prompt used: {response['usage']['prompt_tokens']}")
    return response['choices'][0]['message']['content']

async def handle_responses (history) -> str :
    history.pop(0)
    tempHistory = history[::-1]
    broken = []
    outputString = ""

    if (len(tempHistory) > 30):
        num = (len(tempHistory) // 3)
        while (len(tempHistory) > num) :
            broken.append(tempHistory.pop(0))
            if (len(broken) >= num) :
                print(f"broken: {len(broken)}")
                outputString += await summarize_messages(broken)
                print(outputString)
                broken = []
    
    print(f"tempHistory: {len(tempHistory)}")
    if (len(tempHistory) >= 1) :
        outputString += await summarize_messages(tempHistory)
    return outputString