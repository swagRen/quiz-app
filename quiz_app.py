import streamlit as st
import pandas as pd
import random

# 加载题库
def load_questions(file_path):
    df = pd.read_excel(file_path, dtype=str).fillna('')
    questions = []
    current_question = None

    for _, row in df.iterrows():
        if row['序号'].strip() != '':
            if current_question:
                questions.append(current_question)
            current_question = {
                'category': row['分类'],
                'id': row['序号'],
                'content': row['内容'],
                'type': row['题型'],
                'difficulty': row['难度'],
                'options': [],
                'answer': []
            }
            if row['题型'] == '判断题':
                current_question['answer'] = ['正确'] if row['正确答案'].strip() == '是' else ['错误']
        else:
            if current_question is not None:
                option_text = row['内容'].strip()
                if option_text != '':
                    is_correct = row['正确答案'].strip() == '是'
                    current_question['options'].append({'text': option_text, 'is_correct': is_correct})
                    if is_correct:
                        current_question['answer'].append(option_text)
    if current_question:
        questions.append(current_question)
    return questions


# 初始化 session_state
def init_state():
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'question_idx' not in st.session_state:
        st.session_state.question_idx = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'completed' not in st.session_state:
        st.session_state.completed = False


def start_new_round(all_questions):
    st.session_state.questions = random.sample(all_questions, 30)
    st.session_state.question_idx = 0
    st.session_state.score = 0
    st.session_state.answers = []
    st.session_state.completed = False


def display_question(q, idx):
    st.write(f"### 第 {idx + 1} 题: {q['content']} ({q['type']}，难度: {q['difficulty']})")

    key_prefix = f"q_{idx}"
    user_answer = None
    submitted = False

    if q['type'] == '判断题':
        user_answer = st.radio("选择答案", ['正确', '错误'], key=key_prefix)
        submitted = st.button("提交", key=f"{key_prefix}_submit")

    elif q['type'] == '单选题':
        options = [opt['text'] for opt in q['options']]
        user_answer = st.radio("选择答案", options, key=key_prefix)
        submitted = st.button("提交", key=f"{key_prefix}_submit")

    elif q['type'] == '多选题':
        options = [opt['text'] for opt in q['options']]
        user_answer = st.multiselect("选择答案", options, key=key_prefix)
        submitted = st.button("提交", key=f"{key_prefix}_submit")

    if submitted:
        correct = False
        if q['type'] == '多选题':
            correct = sorted(user_answer) == sorted(q['answer'])
        else:
            correct = user_answer in q['answer']

        if correct:
            st.success("✅ 回答正确！")
            st.session_state.score += 1
        else:
            st.error(f"❌ 回答错误，正确答案是：{', '.join(q['answer'])}")

        st.session_state.answers.append({
            'question': q['content'],
            'your_answer': user_answer if isinstance(user_answer, str) else ', '.join(user_answer),
            'correct_answer': ', '.join(q['answer']),
            'result': '正确' if correct else '错误'
        })

        # 进入下一题
        if st.session_state.question_idx < 29:
            st.session_state.question_idx += 1
            st.experimental_rerun()
        else:
            st.session_state.completed = True
            st.experimental_rerun()


def main():
    st.set_page_config(page_title="知识问答", layout="centered")
    st.title("📚 知识问答小程序")
    init_state()

    questions = load_questions("questions.xlsx")

    if not st.session_state.questions:
        start_new_round(questions)

    if st.session_state.completed:
        st.success(f"🎉 本轮完成！得分: {st.session_state.score} / 30")
        st.write("### 答题记录")
        for i, record in enumerate(st.session_state.answers):
            st.write(f"第 {i + 1} 题：{record['question']}")
            st.write(f"你的答案：{record['your_answer']} | 正确答案：{record['correct_answer']} | 结果：{record['result']}")
            st.markdown("---")
        if st.button("🔁 开始新一轮答题"):
            start_new_round(questions)
            st.experimental_rerun()
    else:
        current_question = st.session_state.questions[st.session_state.question_idx]
        display_question(current_question, st.session_state.question_idx)


if __name__ == "__main__":
    main()
