from flask import Flask, render_template, request, redirect
import pandas as pd
import random

app = Flask(__name__)

df = pd.DataFrame()
df_unknown = pd.DataFrame()
current = 0
current_in_all = 0
counter = 0

@app.before_first_request
def load_data():
    '''load words from csv'''
    global df, df_unknown
    try:
        df = pd.read_csv("data/words.csv", encoding='utf-8')
    except FileNotFoundError as e:
        print(f'Data load failed: {e}')

    df_unknown = df[df['I know already'] != 1].copy()

def save_data():
    '''save progress to csv'''
    global df
    df.to_csv('data/words.csv', index=False, encoding='utf-8')

def draw():
    '''draw random word'''
    lng = len(df_unknown)
    n = lng
    while n not in range(0, lng):
        r = random.gauss(0, lng / 2)
        n = int(r)
    return n

def get_current_in_all():
    '''get index of word in total words based on index from unkown words'''
    target_value = df_unknown["word"].iloc[current]
    index = df.index[df["word"] == target_value].tolist()[0]
    return index

@app.route('/')
def display_word():
    '''get new flash card'''
    global current, current_in_all, df_unknown, counter, total, known_count
    counter += 1
    current = draw()
    current_in_all = get_current_in_all()
    total = len(df)
    known_count = total - len(df_unknown)
    return render_template('word_display.html',
                           counter=counter,
                           rank=df_unknown["rank"].iloc[current],
                           total=total,
                           known_count=known_count,
                           word=df_unknown["word"].iloc[current],
                           lemma=df_unknown["lemma forms"].iloc[current])

@app.route('/update', methods=['POST'])
def update_word():
    '''button actions'''
    global current, current_in_all, df, df_unknown, counter, total, known_count
    action = request.form['action']
    
    if action == 'know':
        df.at[current_in_all, "I know already"] = 1
        df_unknown = df[df['I know already'] != 1].copy()

    elif action == 'translate':
        translation = df_unknown["translation"].iloc[current]
        lemma_form = df_unknown["translation lemma"].iloc[current]
        return render_template('translation_display.html',
                               translation=translation,
                               lemma_form=lemma_form,
                           counter=counter,
                           rank=df_unknown["rank"].iloc[current],
                           total=total,
                           known_count=known_count,
                           word=df_unknown["word"].iloc[current],
                           lemma=df_unknown["lemma forms"].iloc[current]                               
                               )

    elif action == 'next':
        pass

    elif action == 'save':
        save_data()
        return render_template('word_display.html',
                           counter=counter,
                           rank=df_unknown["rank"].iloc[current],
                           total=total,
                           known_count=known_count,
                           word=df_unknown["word"].iloc[current],
                           lemma=df_unknown["lemma forms"].iloc[current])

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
