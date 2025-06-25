import streamlit as st
import pandas as pd
import random
import os
from io import BytesIO

def load_questions():
    file_path = "questions.xlsx"
    if not os.path.exists(file_path):
        st.error(f"\u65e0\u6cd5\u627e\u5230\u95ee\u9898\u6587\u4ef6: {file_path}")
        st.stop()
    try:
        df = pd.read_excel(file_path, dtype=str).fillna('')
    except Exception as e:
        st.error(f"\u52a0\u8f7d\u95ee\u9898\u6587\u4ef6\u65f6\u51fa\u9519: {str(e)}")
        st.stop()

    questions = []
    current_question = None

    for _, row in df.iterrows():
        if row['\u5e8f\u53f7'].strip() != '':
            if current_question:
                questions.append(current_question)
            current_question = {
                'category': row['\u5206\u7c7b'],
                'id': row['\u5e8f\u53f7'],
                'content': row['\u5185\u5bb9'],
                'type': row['\u9898\u578b'],
                'difficulty': row['\u96be\u5ea6'],
                'options': [],
                'answer': []
            }
            if row['\u9898\u578b'] == '\u5224\u65ad\u9898':
                if row['\u6b63\u786e\u7b54\u6848'].strip() == '\u662f':
                    current_question['answer'] = ['\u6b63\u786e']
                else:
                    current_question['answer'] = ['\u9519\u8bef']
        else:
            if current_question is not None:
                option_text = row['\u5185\u5bb9'].strip()
                if option_text != '':
                    is_correct = row['\u6b63\u786e\u7b54\u6848'].strip() == '\u662f'
                    current_question['options'].append({'text': option_text, 'is_correct': is_correct})
                    if is_correct:
                        current_question['answer'].append(option_text)
    if current_question:
        questions.append(current_question)
    return questions

def select_random_questions(questions, num=30):
    return random.sample(questions, min(num, len(questions)))

def initialize_session_state():
    if 'question_idx' not in st.session_state:
        st.session_state.question_idx = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'submitted' not in st.session_state:
        st.session_state.submitted = []
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False

def display_question(questions):
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = select_random_questions(questions)

    if len(st.session_state.user_answers) != len(st.session_state.selected_questions):
        st.session_state.user_answers = [None] * len(st.session_state.selected_questions)
        st.session_state.submitted = [False] * len(st.session_state.selected_questions)

    question = st.session_state.selected_questions[st.session_state.question_idx]

    st.subheader(f"\u9898 {st.session_state.question_idx + 1}/{len(st.session_state.selected_questions)}")
    st.markdown(f"**{question['content']}**")
    st.caption(f"\u5206\u7c7b: {question['category']} | \u9898\u578b: {question['type']} | \u96be\u5ea6: {question['difficulty']}")

    if question['type'] == '\u5224\u65ad\u9898':
        options = ['\u6b63\u786e', '\u9519\u8bef']
        selected = st.radio("\u8bf7\u9009\u62e9\u7b54\u6848:", options, index=None, key=f"radio_{st.session_state.question_idx}")
        st.session_state.user_answers[st.session_state.question_idx] = selected
        if st.button("\u63d0\u4ea4\u7b54\u6848"):
            st.session_state.submitted[st.session_state.question_idx] = True

        if st.session_state.submitted[st.session_state.question_idx]:
            if selected == question['answer'][0]:
                st.success("\u56de\u7b54\u6b63\u786e!")
            else:
                st.error(f"\u56de\u7b54\u9519\u8bef\uff01\u6b63\u786e\u7b54\u6848\u662f: {question['answer'][0]}")

    elif question['type'] == '\u5355\u9009\u9898':
        options = [opt['text'] for opt in question['options']]
        selected = st.radio("\u8bf7\u9009\u62e9\u7b54\u6848:", options, index=None, key=f"radio_{st.session_state.question_idx}")
        st.session_state.user_answers[st.session_state.question_idx] = selected
        if st.button("\u63d0\u4ea4\u7b54\u6848"):
            st.session_state.submitted[st.session_state.question_idx] = True

        if st.session_state.submitted[st.session_state.question_idx]:
            if selected in question['answer']:
                st.success("\u56de\u7b54\u6b63\u786e!")
            else:
                st.error(f"\u56de\u7b54\u9519\u8bef\uff01\u6b63\u786e\u7b54\u6848\u662f: {', '.join(question['answer'])}")

    elif question['type'] == '\u591a\u9009\u9898':
        options = [opt['text'] for opt in question['options']]
        selected = st.multiselect("\u8bf7\u9009\u62e9\u7b54\u6848(\u53ef\u591a\u9009):", options, default=None, key=f"multi_{st.session_state.question_idx}")
        st.session_state.user_answers[st.session_state.question_idx] = selected
        if st.button("\u63d0\u4ea4\u7b54\u6848"):
            st.session_state.submitted[st.session_state.question_idx] = True

        if st.session_state.submitted[st.session_state.question_idx]:
            if sorted(selected) == sorted(question['answer']):
                st.success("\u56de\u7b54\u6b63\u786e!")
            else:
                st.error(f"\u56de\u7b54\u9519\u8bef\uff01\u6b63\u786e\u7b54\u6848\u662f: {', '.join(question['answer'])}")

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.session_state.question_idx > 0:
            if st.button("\u4e0a\u4e00\u9898"):
                st.session_state.question_idx -= 1
    with col2:
        if st.button("\u91cd\u65b0\u5f00\u59cb"):
            reset_quiz(questions)
    with col3:
        if st.session_state.question_idx < len(st.session_state.selected_questions) - 1:
            if st.button("\u4e0b\u4e00\u9898"):
                st.session_state.question_idx += 1
        else:
            if st.button("\u67e5\u770b\u7ed3\u679c"):
                st.session_state.show_results = True

def calculate_score():
    score = 0
    for i, question in enumerate(st.session_state.selected_questions):
        user_answer = st.session_state.user_answers[i]
        if question['type'] == '\u591a\u9009\u9898':
            if sorted(user_answer or []) == sorted(question['answer']):
                score += 1
        else:
            if user_answer in question['answer']:
                score += 1
    return score

def display_results():
    st.title("\u6e38\u620f\u7ed3\u679c")
    score = calculate_score()
    total = len(st.session_state.selected_questions)
    st.subheader(f"\u5f97\u5206: {score}/{total} ({score/total*100:.1f}%)")
    for i, question in enumerate(st.session_state.selected_questions):
        user_answer = st.session_state.user_answers[i] or "\u672a\u56de\u7b54"
        correct_answer = ", ".join(question['answer'])
        if isinstance(user_answer, list):
            user_answer = ", ".join(user_answer)
        status = "\u6b63\u786e" if user_answer == correct_answer else "\u9519\u8bef"
        with st.expander(f"\u9898 {i+1}: {question['content']} ({status})"):
            st.markdown(f"**\u4f60\u7684\u7b54\u6848:** {user_answer}")
            st.markdown(f"**\u6b63\u786e\u7b54\u6848:** {correct_answer}")

    if st.button("\u91cd\u65b0\u5f00\u59cb\u6e38\u620f"):
        reset_quiz(st.session_state.questions)

def reset_quiz(questions):
    for key in ['selected_questions', 'question_idx', 'user_answers', 'submitted', 'show_results']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.selected_questions = select_random_questions(questions)
    st.session_state.question_idx = 0
    st.session_state.user_answers = [None] * len(st.session_state.selected_questions)
    st.session_state.submitted = [False] * len(st.session_state.selected_questions)
    st.session_state.show_results = False

def main():
    st.title("\u77e5\u8bc6\u95ee\u7b54\u5c0f\u7a0b\u5e8f")
    if 'questions' not in st.session_state:
        st.session_state.questions = load_questions()
    initialize_session_state()

    if st.button("\u91cd\u65b0\u5f00\u59cb\u6e38\u620f"):
        reset_quiz(st.session_state.questions)

    if st.session_state.show_results:
        display_results()
    else:
        display_question(st.session_state.questions)
        progress = (st.session_state.question_idx + 1) / len(st.session_state.selected_questions)
        st.progress(progress)
        st.caption(f"\u5df2\u5b8c\u6210: {st.session_state.question_idx + 1}/{len(st.session_state.selected_questions)} \u9898")

if __name__ == "__main__":
    main()
