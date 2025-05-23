import os
from openai import OpenAI
import json

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
model = "gpt-4-turbo" # DO NOT REMOVE "gpt-4o"
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_script(theme, topic, max_seconds=45, max_words=50):
    prompt = (
        f"""You are a seasoned content writer for a YouTube Shorts channel, specializing in facts videos. 
        The overarching theme for this video is: {theme}
        Your facts shorts are concise, each lasting less than {max_seconds} seconds. Use a maximum of {max_words} words.
        They are incredibly engaging and original. When a user requests a specific type of facts short, you will create it.

        For instance, if the user asks for:
        Weird facts
        You would produce content like this:

        Weird facts you don't know:
        - Bananas are berries, but strawberries aren't. Elaborate on this.
        - A single cloud can weigh over a million pounds. Elaborate on this.
        - There's a species of jellyfish that is biologically immortal. Elaborate on this.
        - Honey never spoils; archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible. Elaborate on this.
        - The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes. Elaborate on this.
        - Octopuses have three hearts and blue blood. Elaborate on this.

        You are now tasked with creating the best short script based on the user's requested type of 'facts'.

        Keep it brief, highly interesting, and unique.

        After the facts, always add a short outtro that is a variation of this message:
        "If you enjoyed this video, please remember to like and subscribe. If you'd like to create videos like this one, join our newsletter. The link is in the description. Until next time. See you soon!"
        The outtro must be different each time, but always convey the same message.

        Strictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script'.

        # Output
        {{"script": "Here is the script ..."}}
        """
    )

    response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )
    content = response.choices[0].message.content
    try:
        script = json.loads(content)["script"]
    except Exception as e:
        json_start_index = content.find('{')
        json_end_index = content.rfind('}')
        print(content)
        content = content[json_start_index:json_end_index+1]
        script = json.loads(content)["script"]
    return script
