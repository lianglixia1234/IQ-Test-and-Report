# report.py
import numpy as np
from github import Github
import streamlit as st

# ==========================================
# 🌟 核心硬编码常模数据库（彻底告别 Norm.csv 损坏/列找不到问题）
# ==========================================
# 根据你上传的 Norm.csv 真实标准数据内嵌
NORM_DATABASE = {
    # 年龄: [95%, 90%, 75%, 50%, 25%, 10%, 5%] 对应的截止分数
    5.5:  [34, 29, 25, 16, 13, 12, 9],
    6.0:  [36, 31, 25, 17, 13, 12, 9],
    6.5:  [37, 31, 25, 18, 13, 12, 10],
    7.0:  [43, 36, 25, 19, 13, 12, 10],
    7.5:  [44, 38, 31, 21, 13, 12, 10],
    8.0:  [44, 39, 31, 23, 15, 13, 10],
    8.5:  [45, 40, 33, 29, 20, 14, 12],
    9.0:  [47, 43, 37, 33, 25, 14, 12],
    9.5:  [50, 47, 39, 35, 27, 17, 13],
    10.0: [50, 48, 42, 35, 27, 17, 13],
    10.5: [50, 49, 42, 39, 32, 25, 18],
    11.0: [52, 50, 43, 39, 33, 25, 19],
    11.5: [53, 50, 45, 42, 35, 25, 19],
    12.0: [53, 50, 46, 42, 37, 27, 21],
    12.5: [53, 52, 50, 45, 40, 33, 28],
    13.0: [53, 52, 50, 45, 40, 35, 30],
    13.5: [54, 52, 50, 46, 42, 35, 32],
    14.0: [55, 52, 50, 48, 43, 36, 34],
    14.5: [55, 53, 51, 48, 43, 36, 34],
    15.0: [57, 54, 51, 48, 43, 36, 34],
    15.5: [57, 55, 52, 49, 43, 41, 34],
    16.0: [57, 56, 53, 49, 44, 41, 34],
    16.5: [57, 56, 53, 49, 45, 41, 36],
    17.0: [58, 57, 55, 52, 47, 40, 37],
    20.0: [57, 56, 54, 50, 44, 38, 33],
    30.0: [57, 55, 52, 48, 44, 37, 28],
    40.0: [57, 54, 50, 47, 41, 31, 28],
    50.0: [54, 52, 48, 42, 34, 24, 21],
    60.0: [54, 52, 46, 37, 30, 22, 19],
    70.0: [52, 49, 44, 33, 26, 18, 17],
}

# ==========================================
# 🌟 核心硬编码中文评语库
# ==========================================
TEXT_DATABASE = {
    "≥95": {
        "level": "优秀", 
        "rank": "1.0",
        "interpretation": """受测者展现出卓越的智力潜能，在空间感知、观察辨别、图形比较、具象想象与组合，以及逻辑推理等方面能力尤为突出。其思维深刻且具灵活性，专注力强，能够敏锐地捕捉事物的内在联系；善于高效整合并运用信息，具备极强的复杂问题解决能力。综合认知水平显著领先于同龄群体，在日常学习与适应中具备极高的起点与优势。""",
        "suggestions": """受测者具备优异的认知基石，若能匹配良好的成长环境并充分释放潜能，未来极具发展空间。在后续的培养中，建议关注以下几点：
（1）建立高阶目标，激发内在驱动：卓越的天赋仍需持续的现实历练。建议引导受测者树立更高的自我标准，勇于走出“舒适圈”面对挑战，培养应对复杂挫折的韧性与不懈努力的品质。
（2）提供定制化挑战，满足求知需求：鉴于其较强的学习效能与认知耐力，常规的教学内容可能难以满足其求知欲。建议为其提供更多深度学习、跨学科探究或社会实践的机会，以保持其思维的活跃度.
（3）注重非智力因素的均衡发展：在关注智力成长的同时，应高度重视其心理素质与健全人格的塑造。着重培养其意志力、诚实、正直、责任感以及同理心，实现全人发展。"""
    },
    "75~94": {
        "level": "高于平均水平", 
        "rank": "2.0",
        "interpretation": """受测者具备较高的智力素质，在空间感知、观察辨别以及逻辑推理等维度表现出较强的能力。其思维具有一定的深刻性与灵活性，专注力集中，能够较好地捕捉事物间的内在联系。在信息整合与实际问题解决方面具备良好的人才潜质。受测者对周围环境保持着积极的探索欲，在日常学习、生活及人际适应中，通过阶段性的努力投入，极易取得优异的表现。""",
        "suggestions": """受测者认知水平良好，具备妥善处理绝大多数常规与复杂问题的能力。其学习效能高、可塑性强，通过科学的引导与自身努力，能够实现高水平的能力转化。后续培养建议关注以下几点：
（1）引导务实笃行，追求持续成长：鉴于受测者具备较好的天赋基础，教育者应引导其保持谦逊、笃实的态度。鼓励其建立长期目标，将阶段性优势转化为持之以恒的行动力，脚踏实地地实现自我提升。
（2）重视情商（EQ）培养，优化综合素养：智力发展离不开情感能力的协同。应着重培养受测者在情绪识别、表达与自我调控方面的能力，提升自控力与反思意识。
（3）强化非智力因素，促进全人发展：在日常生活中，应同步注重其意力、诚实、正直和责任感等良好品格的塑造。健全的情商与人格不仅能为智力发展赋能，更是保障其身心健康成长与长远发展的核心基石。"""
    },
    "25~74": {
        "level": "平均水平", 
        "rank": "3.0",
        "interpretation": """受测者的智力素质处于同龄群体的常规（中等）水平。在空间感知、观察辨别和逻辑推理方面具备基础的认知能力，通常能够理解事物的内在联系，并在常规情境下展现出一定的信息整合与运用能力。受测者的兴趣发展相对聚焦，解决复杂问题的能力处于常模平均线附近。在面对高难度挑战时可能会遇到阶段性瓶颈，但通过持续的努力与合理的策略调整，完全能够在学习、生活及人际适应中取得良好且稳定的表现。""",
        "suggestions": """受测者认知结构相对均衡，具备与大多数人相当的发展基石。为进一步优化其能力结构，建议关注以下几点：
（1）深化自我认知，推行优势发展：建议引导受测者全面评估自身认知特点，敏锐捕捉并着重培养其优势智能领域；同时，针对相对薄弱的认知维度进行常态化的巩固与专项提升。
（2）践行成长型思维，重视勤勉效能：认知能力并非一成不变，亦非决定未来成就的单一维度。扎实的努力与科学的训练对该区间受测者尤为关键，建议通过制定清晰的阶梯式目标，以持之以恒的行动促成能力的渐进式跃升。
（3）强化核心素养，构建心理韧性：关注自信心、意志力、诚实、正直及责任感等非智力因素的培育，健全的人格品质将为其健康成长与社会适应提供长效的保障。"""
    },
    "5~24": {
        "level": "低于平均水平", 
        "rank": "4.0",
        "interpretation": """受测者目前的整体智力素质发展相对缓滞。测评结果显示，其在观察能力与空间感知维度的发展略微滞后，通常倾向于捕捉直观、表面化的线索，对复杂空间关系的识别与转化尚显吃力。思维的灵活性与条理性有待提升，在把握事物深层内在逻辑以及高效整合关联信息方面存在一定局限。整体认知发展速度略慢于同龄群体，对周围环境与新事物的探索兴趣相对偏弱。""",
        "suggestions": """鉴于受测者当前的认知起点相对较低，若要达到同龄群体的平均学业水平，需要付出更多的耐心与努力。同时，需注意发掘其可能存在的单一优势智能。后续教育干预建议关注以下几点：
（1）实施精准特长发掘，开展补偿性训练：教育者需保持充分的耐心，注重观察并捕捉受测者的潜在优势领域并给予倾斜性培养；对于空间、逻辑等薄弱环节，应提供阶梯式的专项辅导。
（2）设定合理预期，推行循序渐进策略：建议为其量身定制难度适宜的任务，遵循“小步子、多循环、多鼓励”的原则，给予其更充裕的时间进行认知消化，通过阶段性成就感引导其稳步成长。
（3）引入具象化教学，强化实践练习：在面对抽象或高难度问题时，教育者应提供更多直观的模型、图示及个性化指导，通过反复的重构与练习帮助其内化知识。"""
    },
    "<5": {
        "level": "远低于平均水平", 
        "rank": "5.0",
        "interpretation": """受测者目前的整体认知与智力发展水平显著滞后。测评显示，其在观察辨别与空间感知维度存在明显的局限，难以有效捕捉常规的视觉线索或识别基础的空间关系。思维呈现出较高的局限性与具象性，通常难以理解抽象的内在逻辑，在信息捕捉与综合整合方面存在较大困难。受测者整体发育与发展速度明显缓于同龄人，日常表现出注意力集中困难、反应相对缓滞，且对外部环境的探究兴趣较为匮乏或难以持久。由于认知适应力存在显著缺口，在普通教学环境下的高强度学业及社交适应可能面临较大挑战。""",
        "suggestions": """受测者目前的认知与思维发展面临较大局限，需要全方位、定制化的支持系统帮助其提升社会适应能力与生活自理能力。建议关注以下几点：
（1）评估教育安置渠道，引入支持性教育：建议根据专业评估，为其匹配更符合其身心发展特点的支持性教育资源或特殊教育课程，采用个别化教育计划以契合其成长节奏。
（2）淡化学业结果评价，秉持多元价值导向：避免因学业表现或认知差异对其进行负面定性。个体的价值不应由单一的试卷成绩衡量，教育者与家长应给予充分的接纳，关注其诚实、善良、同理心等社会性品质的塑造。
（3）丰富环境刺激，激发潜在认知活力：智力发展受遗传与环境的交互影响。建议多为受测者创造多感官互动的环境，经常引导其参与需要观察、动手的简单生活情境，以温和、持续的外部刺激激发其对新事物的好奇心，最大限度地促进其潜能的开发。"""
    }
}

def generate_report_html(data):
    """根据测试模板定制的精美 HTML 渲染"""
    return f"""
    <div style="font-family: 'Microsoft YaHei', sans-serif; max-width: 850px; margin: 0 auto; padding: 30px; border: 1px solid #dcdfe6; border-radius: 8px; background-color: #ffffff; color: #303133;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1a73e8; margin: 0; font-size: 28px;">测 试 报 告</h1>
            <p style="color: #606266; margin: 10px 0 0 0; font-size: 16px; font-weight: bold;">瑞文智力测验（60题），标准渐进矩阵（SPM）</p>
        </div>
        <div style="margin-bottom: 25px;">
            <h3 style="color: #1a73e8; border-left: 4px solid #1a73e8; padding-left: 10px; margin-bottom: 10px;">一、 基本信息</h3>
            <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 15px;">
                <tr>
                    <td style="border: 1px solid #dcdfe6; padding: 10px; background-color: #f5f7fa; font-weight: bold; width: 15%;">姓名</td>
                    <td style="border: 1px solid #dcdfe6; padding: 10px; width: 35%;">{data['name']}</td>
                    <td style="border: 1px solid #dcdfe6; padding: 10px; background-color: #f5f7fa; font-weight: bold; width: 15%;">性别</td>
                    <td style="border: 1px solid #dcdfe6; padding: 10px; width: 35%;">{data['gender']}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #dcdfe6; padding: 10px; background-color: #f5f7fa; font-weight: bold;">Age</td>
                    <td style="border: 1px solid #dcdfe6; padding: 10px;">{data['age']} 岁</td>
                    <td style="border: 1px solid #dcdfe6; padding: 10px; background-color: #f5f7fa; font-weight: bold;">测试日期</td>
                    <td style="border: 1px solid #dcdfe6; padding: 10px;">{data['date']}</td>
                </tr>
            </table>
        </div>
        <div style="margin-bottom: 25px;">
            <h3 style="color: #1a73e8; border-left: 4px solid #1a73e8; padding-left: 10px; margin-bottom: 10px;">二、 原始分数</h3>
            <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 15px;">
                <thead>
                    <tr style="background-color: #f5f7fa; font-weight: bold;">
                        <th style="border: 1px solid #dcdfe6; padding: 10px; text-align: left; padding-left: 20px;">因素</th>
                        <th style="border: 1px solid #dcdfe6; padding: 10px; width: 25%;">分数</th>
                        <th style="border: 1px solid #dcdfe6; padding: 10px; width: 25%;">最高分</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f"<tr><td style='border:1px solid #dcdfe6;padding:10px;text-align:left;padding-left:20px;'>{k}</td><td style='border:1px solid #dcdfe6;padding:10px;font-weight:bold;'>{v}</td><td style='border:1px solid #dcdfe6;padding:10px;color:#909399;'>12</td></tr>" for k,v in data['factor_scores'].items()])}
                    <tr style="background-color: #fdf6ec; font-weight: bold; color: #e6a23c;">
                        <td style="border: 1px solid #dcdfe6; padding: 10px; text-align: left; padding-left: 20px;">总分</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; font-size: 18px;">{data['total_score']}</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; color: #909399;">60</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div style="margin-bottom: 25px;">
            <h3 style="color: #1a73e8; border-left: 4px solid #1a73e8; padding-left: 10px; margin-bottom: 10px;">三、 智力水平</h3>
            <div style="background-color: #f4f4f5; padding: 15px; border-radius: 6px; font-size: 15px; line-height: 2;">
                <div><strong>评估标准分数（百分位）：</strong> <span style="color: #e6a23c; font-weight: bold; font-size: 16px;">{data['percentile']}</span></div>
                <div><strong>智力水平：</strong> <span style="color: #67c23a; font-weight: bold; font-size: 16px;">{data['level']}</span></div>
                <div><strong>智商值（测验等级）：</strong> <span style="color: #409eff; font-weight: bold;">{data['rank']} 级</span></div>
            </div>
        </div>
        <div style="margin-bottom: 25px;">
            <h3 style="color: #1a73e8; border-left: 4px solid #1a73e8; padding-left: 10px; margin-bottom: 10px;">四、 结果解读与发展建议</h3>
            <div style="font-size: 15px; line-height: 1.6; text-align: justify;">
                <p><strong>结果解读：</strong></p>
                <div style="background-color: #fafafa; padding: 15px; border: 1px solid #eee; border-radius: 4px; color: #5e6d82; margin-bottom: 15px;">{data['interpretation']}</div>
                <p><strong>指导建议：</strong></p>
                <div style="background-color: #fafafa; padding: 15px; border: 1px solid #eee; border-radius: 4px; color: #5e6d82; white-space: pre-wrap;">{data['suggestions']}</div>
            </div>
        </div>
    </div>
    """

def calculate_report_data(name, gender, age, test_date, total_score, factor_scores):
    """100%内置算法：无需读取外部常模文件"""
    # 锁定最接近的年龄常模
    available_ages = np.array(list(NORM_DATABASE.keys()))
    closest_age = available_ages[np.abs(available_ages - float(age)).argmin()]
    boundaries = NORM_DATABASE[closest_age] # 拿到对应的7个分数边界
    
    # 匹配百分位
    percentiles = [95, 90, 75, 50, 25, 10, 5]
    matched_p = 0  # 🌟 修复关键：初始默认值设为 0，代表未达最低常模
    for b_score, p_val in zip(boundaries, percentiles):
        if total_score >= b_score:
            matched_p = p_val
            break

    # 规范化文字区间与评语匹配
    # -------------------------------------------------------------
    # 🌟 精确切分百分位区间，完美对应 5 种中文评语
    # -------------------------------------------------------------
    if matched_p == 95:
        p_text = "≥95"
    elif matched_p in [90, 75]:
        p_text = "75~94"
    elif matched_p in [50, 25]:
        p_text = "25~74"
    elif matched_p == 10:
        p_text = "5~24"
    elif matched_p == 5:
        p_text = "5~24"   # 🌟 修复关键：刚好压线 5 百分位的人，应当属于 5~24 档次
    else:
        p_text = "<5"     # 🌟 修复关键：matched_p == 0（完全低于常模下限），对应 "<5" 区间

    # 从 100% 格式正确的内置数据库中抓取文本
    txt_info = TEXT_DATABASE.get(p_text, TEXT_DATABASE["25~74"])

    # 格式化百分位数展示：如果是未及常模，文字直接展示为 <5
    percentile_display = f"第 {matched_p} 百分位数 ({p_text})" if matched_p > 0 else f"低于第 5 百分位数 ({p_text})"

    return {
        "name": name, "gender": gender, "age": age, "date": test_date,
        "total_score": total_score, "factor_scores": factor_scores,
        "percentile": percentile_display,
        "level": txt_info["level"], "rank": txt_info["rank"],
        "interpretation": txt_info["interpretation"], "suggestions": txt_info["suggestions"]
    }

def upload_report_to_github(file_name, html_content):
    """GitHub 自动同步函数（适配扁平化 Secrets）"""
    try:
        # 🌟 改为直接读取你现有的全大写变量名
        TOKEN = st.secrets["GITHUB_TOKEN"]
        REPO_NAME = st.secrets["GITHUB_REPO"]
        BRANCH = "main" # 或者使用 st.secrets.get("GITHUB_BRANCH", "main")
        
        g = Github(TOKEN)
        repo = g.get_repo(REPO_NAME)
        github_path = f"report/{file_name}"
        try:
            contents = repo.get_contents(github_path, ref=BRANCH)
            repo.update_file(github_path, f"Update {file_name}", html_content, contents.sha, branch=BRANCH)
        except Exception:
            repo.create_file(github_path, f"Create {file_name}", html_content, branch=BRANCH)
        return True, "同步成功"
    except Exception as e:
        return False, str(e)
