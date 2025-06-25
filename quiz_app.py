import streamlit as st
import pandas as pd
import random

# 解析Excel文件，假设数据已经加载
def load_questions(file_path):
    df = pd.read_excel(file_path, dtype=str)
    df = df.fillna('')
    return df

# 根据数据处理题目内容
def process_questions(df):
    questions = []
    current_question = None
    
    for _, row in df.iterrows():
        if row['序号']:
            if current_question:
                questions.append(current_question)
            current_question = {
                'id': row['序号'],
                'content': row['内容'],
                'type': row['题型'],
                'options': [],
                'answer': row['正确答案']
            }
        else:
            # Option row, add it to options
            option = row['内容']
            is_correct = row['正确答案'] == '是'
            current_question['options'].append({'text': option, 'is_correct': is_correct})
            
    if current_question:
        questions.append(current_question)
    return questions

# 显示每个问题并等待用户输入
def quiz_app(questions):
    st.title("问答游戏")
    score = 0
    total_questions = len(questions)
    
    for i, question in enumerate(questions):
        st.subheader(f"问题 {i+1}: {question['content']}")
        
        if question['type'] == '判断题':
            # 判断题选项
            user_answer = st.radio("选择答案", ('正确', '错误'))
            correct_answer = '正确' if question['answer'] == '是' else '错误'
        else:
            # 单选或多选题
            user_answer = st.multiselect("选择答案", [opt['text'] for opt in question['options']])
            correct_answer = [opt['text'] for opt in question['options'] if opt['is_correct']]
        
        if st.button(f"提交问题 {i+1}"):
            if user_answer == correct_answer:
                st.success("答对了！")
                score += 1
            else:
                st.error(f"答错了！正确答案是：{', '.join(correct_answer)}")
            st.write(f"当前分数: {score}/{i+1}")
    
    # 总分显示
    st.write(f"游戏结束！你的总分是 {score}/{total_questions}")

# 加载题目数据
file_path = "questions.xlsx"  # 直接指定文件名，因为与 .py 文件在同一文件夹
df = load_questions(file_path)
questions = process_questions(df)

# 运行问答应用
quiz_app(questions)
