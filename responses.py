import openai
openai.api_key = "YOUR_API_KEY"

async def summarize_messages (history) :

    chat = ""
    for i in range (len(history)) :
        chat += history[i] + "\n"

    response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo", # Can be replaced by other models for cheaper/better results!
    messages = [
            {"role": "system", "content": "You are a summary bot."},
            {"role": "user", "content": "Summarize the given text: " + chat}
        ]
    )

    return response['choices'][0]['message']['content']

async def handle_responses (history) -> str :
    history.pop(0)
    tempHistory = history[::-1]
    output = await summarize_messages(tempHistory)
    return output