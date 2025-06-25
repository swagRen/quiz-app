import streamlit as st
import pandas as pd
import random

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

def display_question(q, q_idx):
    st.write(f"**题 {q_idx + 1}/30:** {q['content']}  ({q['type']}, 难度: {q['difficulty']})")

    user_key = f"answer_{q_idx}"

    if q['type'] == '判断题':
        user_answer = st.radio("请选择：", ['正确', '错误'], key=user_key)
    elif q['type'] == '单选题':
        options = [opt['text'] for opt in q['options']]
        user_answer = st.radio("请选择：", options, key=user_key)
    elif q['type'] == '多选题':
        options = [opt['text'] for opt in q['options']]
        user_answer = st.multiselect("请选择：", options, key=user_key)
    else:
        st.warning("未知题型")
        return

    if st.button("提交", key=f"submit_{q_idx}"):
        correct = False
        if q['type'] in ['判断题', '单选题']:
            correct = user_answer in q['answer']
        elif q['type'] == '多选题':
            correct = sorted(user_answer) == sorted(q['answer'])

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

        if st.session_state.question_idx < 29:
            st.session_state.question_idx += 1
        else:
            st.session_state.completed = True

        # 用标志触发刷新，防止 streamlit 错误
        st.session_state.trigger_next = True

def show_result():
    st.header("🎉 答题完成")
    st.success(f"你的得分：{st.session_state.score} / 30")
    st.write(f"正确率：{st.session_state.score / 30 * 100:.2f}%")

    st.subheader("详细答题记录")
    for i, record in enumerate(st.session_state.answers):
        st.write(f"**题 {i+1}**：{record['question']}")
        st.write(f"- 你的答案：{record['your_answer']}")
        st.write(f"- 正确答案：{record['correct_answer']}")
        st.write(f"- 结果：{record['result']}")
        st.markdown("---")

    if st.button("🔄 开始新一轮答题"):
        st.session_state.clear()
        st.experimental_rerun()

def main():
    st.set_page_config(page_title="知识问答小程序", layout="centered")
    st.title("🧠 知识问答小程序")

    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.question_idx = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.completed = False
        st.session_state.trigger_next = False
        st.session_state.questions = random.sample(load_questions("questions.xlsx"), 30)

    if not st.session_state.completed:
        current_question = st.session_state.questions[st.session_state.question_idx]
        display_question(current_question, st.session_state.question_idx)
    else:
        show_result()

    # 安全触发 rerun（用于按钮回调后立即刷新页面）
    if st.session_state.get("trigger_next", False):
        st.session_state.trigger_next = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()
