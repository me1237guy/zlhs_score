import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
import matplotlib

def create_performance_report(student_scores, class_data):
    # Set font family for Chinese characters
    font_dirs = ["Microsoft-JhengHei.ttf"]  # The path to the custom font file.
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    # font_set = {f.name for f in font_manager.fontManager.ttflist}
    # for f in font_set:
    #     print(f)
    # for font_file in font_files:
    #     font_manager.fontManager.addfont(font_file)
    matplotlib.rc('font', family='Microsoft-JhengHei')
    plt.rcParams['font.family']  = ['Microsoft-JhengHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # Convert class data
    class_df = pd.DataFrame({
        'Subject': ['國語文', '英語文', '數學', '歷史', '地理', '物理', '化學', '生物', '地球科學'],
        'Class_Average': [72.54, 68.23, 69.76, 68.72, 68.22, 75.07, 79.65, 68.81, 63.94]
    })
    
    # Convert student scores to DataFrame
    student_df = pd.DataFrame(student_scores)
    
    # Merge student scores with class averages
    analysis_df = pd.merge(student_df, class_df, on='Subject', how='left')
    analysis_df['Difference'] = analysis_df['Student_Score'] - analysis_df['Class_Average']
    
    # Distribution data
    distributions = {
        '國語文': {'99-90': 9, '89-80': 75, '79-70': 147, '69-60': 94, '59-50': 26, '49-40': 3, '39-30': 0, '29-20': 0, '19-10': 1, '9-0': 0},
        '英語文': {'99-90': 18, '89-80': 82, '79-70': 92, '69-60': 61, '59-50': 57, '49-40': 27, '39-30': 11, '29-20': 4, '19-10': 3, '9-0': 0},
        '數學': {'99-90': 24, '89-80': 78, '79-70': 94, '69-60': 90, '59-50': 33, '49-40': 19, '39-30': 9, '29-20': 8, '19-10': 0, '9-0': 0},
        '歷史': {'99-90': 0, '89-80': 37, '79-70': 155, '69-60': 101, '59-50': 52, '49-40': 10, '39-30': 3, '29-20': 0, '19-10': 0, '9-0': 0},
        '化學': {'99-90': 31, '89-80': 75, '79-70': 36, '69-60': 18, '59-50': 7, '49-40': 3, '39-30': 3, '29-20': 0, '19-10': 0, '9-0': 0},
        '生物': {'99-90': 2, '89-80': 36, '79-70': 60, '69-60': 34, '59-50': 26, '49-40': 15, '39-30': 3, '29-20': 1, '19-10': 0, '9-0': 0}
    }
    
    def calculate_percentile(row, distributions):
        subject = row['Subject']
        score = row['Student_Score']
        
        if subject not in distributions:
            return np.nan
            
        ranges = distributions[subject]
        total = sum(ranges.values())
        count_above = 0
        
        for range_str, count in ranges.items():
            range_min = int(range_str.split('-')[1])
            range_max = int(range_str.split('-')[0])
            if score > range_max:
                count_above += count
            elif range_min <= score <= range_max:
                count_above += count / 2
                
        percentile = (count_above / total) * 100
        return round(100 - percentile, 1)
    
    # Calculate percentile ranks
    analysis_df['Percentile_Rank'] = analysis_df.apply(lambda row: calculate_percentile(row, distributions), axis=1)
    
    # Sort by student score
    analysis_df = analysis_df.sort_values('Student_Score', ascending=False)
    
    return analysis_df

def plot_comparison(analysis_df):
    fig = plt.figure(figsize=(12, 8))
    
    subjects = analysis_df['Subject']
    x = np.arange(len(subjects))
    width = 0.35
    
    plt.bar(x - width/2, analysis_df['Student_Score'], width, label='個人成績', color='#4299e1')
    plt.bar(x + width/2, analysis_df['Class_Average'], width, label='班級平均', color='#9ae6b4')
    
    plt.xlabel('科目', fontsize=12)
    plt.ylabel('分數', fontsize=12)
    plt.title('個人成績與班級平均比較', fontsize=14, pad=20)
    plt.xticks(x, subjects, rotation=45)
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig

def plot_percentile(analysis_df):
    fig = plt.figure(figsize=(12, 8))
    
    plt.bar(analysis_df['Subject'], analysis_df['Percentile_Rank'], color='#4299e1')
    plt.xlabel('科目', fontsize=12)
    plt.ylabel('百分位數', fontsize=12)
    plt.title('各科目成績百分位數分布', fontsize=14, pad=20)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig

# Streamlit app
st.set_page_config(page_title="學生成績分析", layout="wide")

st.title("學生成績分析系統")

st.markdown("""
### 使用說明
1. 在左側輸入各科目的分數（0-100分）
2. 系統會自動生成成績分析報告和視覺化圖表
3. 可以隨時調整分數，圖表會即時更新
""")

# Sidebar for input
st.sidebar.header("輸入成績")

# Initialize session state for scores if it doesn't exist
if 'scores' not in st.session_state:
    st.session_state.scores = {
        '國語文': 70,
        '英語文': 70,
        '數學': 70,
        '生物': 70,
        '化學': 70,
        '歷史': 70
    }

# Input fields for each subject
for subject in ['國語文', '英語文', '數學', '生物', '化學', '歷史']:
    st.session_state.scores[subject] = st.sidebar.slider(
        f"{subject}",
        0, 100,
        st.session_state.scores[subject],
        help=f"輸入{subject}的分數 (0-100)"
    )

# Create student scores dictionary
student_scores = {
    "Subject": list(st.session_state.scores.keys()),
    "Student_Score": list(st.session_state.scores.values())
}

# Generate analysis
analysis_df = create_performance_report(student_scores, None)

# Display summary statistics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("平均分數", f"{analysis_df['Student_Score'].mean():.1f}")
with col2:
    st.metric("最高分數", f"{analysis_df['Student_Score'].max()}")
with col3:
    st.metric("最低分數", f"{analysis_df['Student_Score'].min()}")

# Display detailed analysis
st.header("詳細分析")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["成績比較", "百分位數分布", "詳細數據"])

with tab1:
    st.pyplot(plot_comparison(analysis_df))

with tab2:
    st.pyplot(plot_percentile(analysis_df))

with tab3:
    # Format the dataframe for display
    display_df = analysis_df.copy()
    display_df = display_df.round(2)
    display_df.columns = ['科目', '個人分數', '班級平均', '差異', '百分位數']
    st.dataframe(
        display_df.style.background_gradient(subset=['差異'], cmap='RdYlGn'),
        hide_index=True,
        width=None
    )

# Display recommendations
st.header("學習建議")

# Generate recommendations based on performance
above_average = analysis_df[analysis_df['Difference'] > 0]['Subject'].tolist()
below_average = analysis_df[analysis_df['Difference'] < 0]['Subject'].tolist()

if above_average:
    st.success(f"表現優異的科目：{', '.join(above_average)}")
    st.write("建議：")
    st.write("- 維持現有的學習方法和態度")
    st.write("- 可以考慮參加進階課程或競賽")

if below_average:
    st.warning(f"需要加強的科目：{', '.join(below_average)}")
    st.write("建議：")
    st.write("- 建議尋求教師額外指導")
    st.write("- 增加練習題目的數量")
    st.write("- 考慮參加補救教學或補習課程")

# Footer
st.markdown("---")
st.markdown("📊 本分析工具僅供參考，請結合老師建議做為學習改進依據。")
