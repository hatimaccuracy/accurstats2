import openai
from config import OPEN_AI_KEY
from config import yapping_interpret
client =openai.OpenAI(api_key=OPEN_AI_KEY)

def to_GPT(message_to_GPT):
        completion = (client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": message_to_GPT}
            ]
        ))
        message = completion.choices[0].message.content
        return message
def interpret_model(target ,mod):
    message_to_GPT=f"On a trouvé le model économique suivant: {target} ="
    for j in range(0,len(mod),2):
        message_to_GPT+= f"+{mod[j+1]}*{mod[j]} "
    print(message_to_GPT)
    message_to_GPT+= yapping_interpret
    return to_GPT(message_to_GPT)

