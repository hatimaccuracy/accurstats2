import openai
from config import OPEN_AI_KEY
yapping_interpret = ". Ce que je te demande de faire c'est de proposer une interpretation du scénarios economique que ce modèle suggère , c'est à dire justifier les variables proposer et les signes de leurs coefficients d'une façon à décrire les scénarios économiques engendré par les changement des variables"
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

