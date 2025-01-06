from collections import Counter 
from nltk.corpus import stopwords 
from string import punctuation
from wordcloud import WordCloud

import re
import requests 
import speech_recognition as sr 

from API_KEY import KEY 

def audio_file(r: sr.Recognizer):

    print("\033[H\033[2JEnter the absolute path of the audio file to process: ")
    path = input(">> ").strip()

    try:
        with sr.AudioFile(path) as source:
            print("\nStarting speech recognition...\n")

            r.adjust_for_ambient_noise(source)
            audio_duration = source.DURATION 
            chunk_size = 30 

            with open("transcript.txt", "w") as file:
                start = 0
                while start < audio_duration:
                    audio_data = r.record(source, duration=chunk_size, offset=start)
                    try:
                        text = r.recognize_google(audio_data)
                        file.write(text + "\n")
                    except sr.UnknownValueError:
                        file.write("[Unrecognized speech]\n")
                    except sr.RequestError as e:
                        file.write(f"[API error: {e}]\n")
                    start += chunk_size
                    print(f"\033[1A\033[K\tTask Completion: {min(start * 100 // audio_duration, 100)}%")
        print()
        return False
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    print("Terminating process.")
    return True

    
def microphone(r: sr.Recognizer):

    def callback(r, audio):
        with open("transcript.txt", "a") as file:
            try:
                text = r.recognize_google(audio)
                file.write(text + "\n")
            except sr.UnknownValueError:
                file.write("[Unrecognized speech]\n")
            except sr.RequestError as e:
                file.write(f"[API error: {e}]\n")

    try:
        open('transcript.txt', 'w').close()
        mic = sr.Microphone()
        with mic as source:
            r.adjust_for_ambient_noise(source)

        print("Begin speaking!")
        print("Type 'quit' when done.\n")
        
        stop_listening = r.listen_in_background(mic, callback)

        while (inp := input("\033[1A\033[K>> ").lower()) != 'quit':
            continue 

        stop_listening(wait_for_stop=True)
        return False 
    
    except Exception as e:
        print(e)
    print("Terminating process.")
    return True 


def analyse_text():

    url = "https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{}?key=" + KEY
    try:
        with open("transcript.txt", "r") as file:
            text = ' '.join(file.readlines())
            # text preprocessing
            exclude = punctuation
            text = text.translate(str.maketrans(exclude, ' ' * len(exclude)))

            STOPWORDS = stopwords.words('english')
            pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in STOPWORDS) + r')\b')
            filtered = pattern.sub('', text)
            # text analysis
            data = Counter(filtered.split())
            content = data.most_common(5)

            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
            wordcloud.to_file("img/wordcloud.png")
            # synonyms
            for tup in content:
                word = tup[0]
                try:
                    response = requests.get(url.format(word))

                    print(f"Synonyms for '{word}':")
                    print(response.json()[0]['meta']['syns'][0])

                except Exception as e:
                    print(f"Couldn't fetch synonyms due to an error: {e}")
                print()
    except Exception as e:
        print(e)
        print("Terminating process.")

def main():

    r = sr.Recognizer() 
    r.dynamic_energy_threshold = True 

    print("Choose your audio source from the following: ")
    print("Microphone [Enter M]")
    print("Audio File [Enter A]\n")

    while (choice := input("\033[1A\033[K>> ").upper()) not in ('M', 'A'):
        continue 

    match choice:
        case 'A':
            error = audio_file(r)
        case 'M':
            error = microphone(r)

    if not error:
        analyse_text()

if __name__ == "__main__":
    main()