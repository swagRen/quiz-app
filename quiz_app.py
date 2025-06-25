import streamlit as st
import pandas as pd
import random

def load_questions(file_path):
    """从Excel加载问题"""
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

def initialize_session_state(questions):
    """初始化会话状态"""
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = random.sample(questions, min(30, len(questions)))
    if 'question_idx' not in st.session_state:
        st.session_state.question_idx = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = [None] * len(st.session_state.selected_questions)
    if 'submitted' not in st.session_state:
        st.session_state.submitted = [False] * len(st.session_state.selected_questions)
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False

def display_question():
    """显示当前问题"""
    question = st.session_state.selected_questions[st.session_state.question_idx]
    
    st.subheader(f"题 {st.session_state.question_idx + 1}/{len(st.session_state.selected_questions)}")
    st.markdown(f"**{question['content']}**")
    st.caption(f"分类: {question['category']} | 题型: {question['type']} | 难度: {question['difficulty']}")

    # 显示选项
    if question['type'] == '判断题':
        options = ['正确', '错误']
        selected = st.radio("请选择答案:", options, index=None)
        st.session_state.user_answers[st.session_state.question_idx] = selected
        correct = st.button("提交答案")
        
        if correct:
            st.session_state.submitted[st.session_state.question_idx] = True
            if selected == question['answer'][0]:
                st.success("✅ 回答正确！")
            else:
                st.error(f"❌ 回答错误！正确答案是: {question['answer'][0]}")

    elif question['type'] == '单选题':
        options = [opt['text'] for opt in question['options']]
        selected = st.radio("请选择答案:", options, index=None)
        st.session_state.user_answers[st.session_state.question_idx] = selected
        correct = st.button("提交答案")
        
        if correct:
            st.session_state.submitted[st.session_state.question_idx] = True
            if selected in question['answer']:
                st.success("✅ 回答正确！")
            else:
                st.error(f"❌ 回答错误！正确答案是: {', '.join(question['answer'])}")

    elif question['type'] == '多选题':
        options = [opt['text'] for opt in question['options']]
        selected = st.multiselect("请选择答案(可多选):", options, default=None)
        st.session_state.user_answers[st.session_state.question_idx] = selected
        correct = st.button("提交答案")
        
        if correct:
            st.session_state.submitted[st.session_state.question_idx] = True
            if sorted(selected) == sorted(question['answer']):
                st.success("✅ 回答正确！")
            else:
                st.error(f"❌ 回答错误！正确答案是: {', '.join(question['answer'])}")
    
    # 导航按钮
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.session_state.question_idx > 0:
            if st.button("上一题"):
                st.session_state.question_idx -= 1
                st.experimental_rerun()
    with col2:
        if st.button("重新开始"):
            reset_quiz()
            st.experimental_rerun()
    with col3:
        if st.session_state.question_idx < len(st.session_state.selected_questions) - 1:
            if st.button("下一题"):
                st.session_state.question_idx += 1
                st.experimental_rerun()
        else:
            if st.button("查看结果"):
                st.session_state.show_results = True
                st.experimental_rerun()

def calculate_score():
    """计算得分"""
    score = 0
    for i, question in enumerate(st.session_state.selected_questions):
        user_answer = st.session_state.user_answers[i]
        
        if question['type'] == '多选题':
            if sorted(user_answer or []) == sorted(question['answer']):
                score += 1
        else:
            if user_answer in question['answer']:
                score += 1
    
    return score

def display_results():
    """显示测试结果"""
    st.title("测试结果")
    
    score = calculate_score()
    total = len(st.session_state.selected_questions)
    percentage = score / total * 100
    
    st.subheader(f"得分: {score}/{total} ({percentage:.1f}%)")
    st.progress(percentage/100)
    
    st.divider()
    st.subheader("答题详情:")
    
    for i, question in enumerate(st.session_state.selected_questions):
        user_answer = st.session_state.user_answers[i] or "未回答"
        correct_answer = ", ".join(question['answer'])
        
        if isinstance(user_answer, list):
            user_answer = ", ".join(user_answer)
            
        status = "✅" if user_answer == correct_answer else "❌"
        
        with st.expander(f"题 {i+1}: {question['content']} {status}"):
            st.markdown(f"**你的答案:** {user_answer}")
            st.markdown(f"**正确答案:** {correct_answer}")
            st.markdown(f"**解析:** 题型: {question['type']} | 难度: {question['difficulty']}")

    if st.button("重新开始测试"):
        reset_quiz()
        st.experimental_rerun()

def reset_quiz():
    """重置测试状态"""
    st.session_state.pop('selected_questions', None)
    st.session_state.pop('question_idx', None)
    st.session_state.pop('user_answers', None)
    st.session_state.pop('submitted', None)
    st.session_state.pop('show_results', None)

def main():
    """主应用"""
    st.title("知识问答小程序")
    
    # 加载问题
    questions = load_questions("questions.xlsx")
    
    # 初始化会话状态
    initialize_session_state(questions)
    
    # 显示内容
    if st.session_state.show_results:
        display_results()
    else:
        display_question()
        
        # 显示进度
        progress = (st.session_state.question_idx + 1) / len(st.session_state.selected_questions)
        st.progress(progress)
        st.caption(f"已完成: {st.session_state.question_idx + 1}/{len(st.session_state.selected_questions)} 题")

if __name__ == "__main__":
    main()
