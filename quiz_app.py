import streamlit as st
import pandas as pd

def load_questions(file_path):
    df = pd.read_excel(file_path, dtype=str).fillna('')
    questions = []
    current_question = None

    for _, row in df.iterrows():
        if row['序号'].strip() != '':
            # 新题开始
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
            # 判断题直接答案
            if row['题型'] == '判断题':
                if row['正确答案'].strip() == '是':
                    current_question['answer'] = ['正确']
                else:
                    current_question['answer'] = ['错误']
        else:
            # 题目选项部分
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

def quiz_app(questions):
    st.title("知识问答小程序")

    score = 0
    for i, q in enumerate(questions):
        st.write(f"**题 {i+1}:** {q['content']}  ({q['type']}, 难度: {q['difficulty']})")

        if q['type'] == '判断题':
            # 判断题选项固定
            options = ['正确', '错误']
            user_answer = st.radio(f"选择答案 - 题{i+1}", options, key=f"q{i}")
            correct_answer = q['answer'][0]
            submitted = st.button(f"提交答案 - 题{i+1}", key=f"btn{i}")

            if submitted:
                if user_answer == correct_answer:
                    st.success("回答正确！")
                    score += 1
                else:
                    st.error(f"回答错误！正确答案是: {correct_answer}")

        else:
            options = [opt['text'] for opt in q['options']]
            if q['type'] == '单选题':
                user_answer = st.radio(f"选择答案 - 题{i+1}", options, key=f"q{i}")
                submitted = st.button(f"提交答案 - 题{i+1}", key=f"btn{i}")

                if submitted:
                    if user_answer in q['answer']:
                        st.success("回答正确！")
                        score += 1
                    else:
                        st.error(f"回答错误！正确答案是: {', '.join(q['answer'])}")

            elif q['type'] == '多选题':
                user_answer = st.multiselect(f"选择答案 - 题{i+1}", options, key=f"q{i}")
                submitted = st.button(f"提交答案 - 题{i+1}", key=f"btn{i}")

                if submitted:
                    if sorted(user_answer) == sorted(q['answer']):
                        st.success("回答正确！")
                        score += 1
                    else:
                        st.error(f"回答错误！正确答案是: {', '.join(q['answer'])}")

    st.write("---")
    st.write(f"总得分: **{score} / {len(questions)}**")
    st.write(f"正确率: **{score/len(questions)*100:.2f}%**")

if __name__ == "__main__":
    # 你要确保 questions.xlsx 文件在同目录
    questions = load_questions("questions.xlsx")
    quiz_app(questions)
