import streamlit as st
import pandas as pd
import random

def load_questions(file_path):
    """从Excel加载问题"""
    df = pd.read_excel(file_path, dtype=str).fillna('')  # 加载数据并填充空值
    questions = []
    current_question = None

    # 解析数据
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
                if row['正确答案'].strip() == '是':
                    current_question['answer'] = ['正确']
                else:
                    current_question['answer'] = ['错误']
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

def quiz_app(questions):
    """运行答题应用"""
    st.title("知识问答小程序")
    
    # 随机抽取30道题
    selected_questions = random.sample(questions, 30)
    score = 0
    answers = []
    
    # 跟踪当前题目索引
    if 'question_idx' not in st.session_state:
        st.session_state.question_idx = 0
    if 'answered_questions' not in st.session_state:
        st.session_state.answered_questions = []

    # 当前题目
    current_question = selected_questions[st.session_state.question_idx]
    
    st.write(f"**题 {st.session_state.question_idx + 1}:** {current_question['content']}  ({current_question['type']}, 难度: {current_question['difficulty']})")

    if current_question['type'] == '判断题':
        options = ['正确', '错误']
        user_answer = st.radio(f"选择答案 - 题{st.session_state.question_idx + 1}", options, key=f"q{st.session_state.question_idx}")
        correct_answer = current_question['answer'][0]
        submitted = st.button(f"提交答案 - 题{st.session_state.question_idx + 1}", key=f"btn{st.session_state.question_idx}")

        if submitted:
            if user_answer == correct_answer:
                st.success("回答正确！")
                score += 1
            else:
                st.error(f"回答错误！正确答案是: {correct_answer}")
            st.session_state.answered_questions.append((st.session_state.question_idx, user_answer, correct_answer))

            if st.session_state.question_idx < len(selected_questions) - 1:
                st.session_state.question_idx += 1
            else:
                st.session_state.question_idx = 0  # 重新开始答题

    else:
        options = [opt['text'] for opt in current_question['options']]
        if current_question['type'] == '单选题':
            user_answer = st.radio(f"选择答案 - 题{st.session_state.question_idx + 1}", options, key=f"q{st.session_state.question_idx}")
            submitted = st.button(f"提交答案 - 题{st.session_state.question_idx + 1}", key=f"btn{st.session_state.question_idx}")

            if submitted:
                if user_answer in current_question['answer']:
                    st.success("回答正确！")
                    score += 1
                else:
                    st.error(f"回答错误！正确答案是: {', '.join(current_question['answer'])}")
                st.session_state.answered_questions.append((st.session_state.question_idx, user_answer, ', '.join(current_question['answer'])))

                if st.session_state.question_idx < len(selected_questions) - 1:
                    st.session_state.question_idx += 1
                else:
                    st.session_state.question_idx = 0  # 重新开始答题

        elif current_question['type'] == '多选题':
            user_answer = st.multiselect(f"选择答案 - 题{st.session_state.question_idx + 1}", options, key=f"q{st.session_state.question_idx}")
            submitted = st.button(f"提交答案 - 题{st.session_state.question_idx + 1}", key=f"btn{st.session_state.question_idx}")

            if submitted:
                if sorted(user_answer) == sorted(current_question['answer']):
                    st.success("回答正确！")
                    score += 1
                else:
                    st.error(f"回答错误！正确答案是: {', '.join(current_question['answer'])}")
                st.session_state.answered_questions.append((st.session_state.question_idx, ', '.join(user_answer), ', '.join(current_question['answer'])))

                if st.session_state.question_idx < len(selected_questions) - 1:
                    st.session_state.question_idx += 1
                else:
                    st.session_state.question_idx = 0  # 重新开始答题
    
    st.write("---")
    st.write(f"总得分: **{score} / 30**")
    st.write(f"正确率: **{score/30*100:.2f}%**")

    # 显示详细答案
    st.write("**详细答案**")
    for q_num, user, correct in st.session_state.answered_questions:
        st.write(f"题 {q_num + 1}: 用户答案: {user} | 正确答案: {correct}")

    # 开始新一轮答题
    if st.button("开始新一轮答题"):
        st.session_state.question_idx = 0  # 重置题目索引
        st.session_state.answered_questions = []  # 清空答案记录
        quiz_app(questions)

if __name__ == "__main__":
    # 加载问题数据并运行
    questions = load_questions("questions.xlsx")
    quiz_app(questions)
