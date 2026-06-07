import numpy as np

def generate_report_html(data):
    """
    根据《智力测试模板.docx》深度定制的 HTML 报告模板
    """
    html_template = f"""
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
                    <td style="border: 1px solid #dcdfe6; padding: 10px; background-color: #f5f7fa; font-weight: bold;">年龄</td>
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
                    <tr>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; text-align: left; padding-left: 20px;">感知辨别</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; font-weight: bold;">{data['factor_scores'].get('感知辨别', 0)}</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; color: #909399;">12</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; text-align: left; padding-left: 20px;">相似性比较</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; font-weight: bold;">{data['factor_scores'].get('相似性比较', 0)}</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; color: #909399;">12</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; text-align: left; padding-left: 20px;">比较推理</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; font-weight: bold;">{data['factor_scores'].get('比较推理', 0)}</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; color: #909399;">12</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; text-align: left; padding-left: 20px;">系列关系</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; font-weight: bold;">{data['factor_scores'].get('系列关系', 0)}</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; color: #909399;">12</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; text-align: left; padding-left: 20px;">抽象推理</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; font-weight: bold;">{data['factor_scores'].get('抽象推理', 0)}</td>
                        <td style="border: 1px solid #dcdfe6; padding: 10px; color: #909399;">12</td>
                    </tr>
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
                <div style="background-color: #fafafa; padding: 15px; border: 1px solid #eee; border-radius: 4px; color: #5e6d82; margin-bottom: 15px;">
                    {data['interpretation']}
                </div>
                <p><strong>指导建议：</strong></p>
                <div style="background-color: #fafafa; padding: 15px; border: 1px solid #eee; border-radius: 4px; color: #5e6d82; white-space: pre-wrap;">{data['suggestions']}</div>
            </div>
        </div>

        <div style="margin-top: 35px; border-top: 1px solid #e6a23c; background-color: #fdf6ec; padding: 15px; border-radius: 6px; font-size: 13px; color: #e6a23c; line-height: 1.6;">
            <strong style="font-size: 14px; display: block; margin-bottom: 5px;">⚠️ 评估提醒：</strong>
            1. 瑞文标准渐进矩阵测试仅测量流体智力（逻辑推理、抽象思维），并不涵盖语言表达、记忆力、情商、实践能力、创造力等多种智力维度。请勿仅凭测试结果判断整体智力水平。<br>
            2. 测试结果受测试环境、个人状态、专注程度、答题态度等因素影响，单次测试结果仅供参考。<br>
            3. 未成年受试者的智力仍处于发展阶段，可通过有针对性的思维训练得到显著提升。<br>
            4. 所有评估结果都应综合考虑多种因素进行全面理解。认知能力可以通过科学训练不断发展。每个人都拥有独特的才能组合。建议在专业人士的指导下制定个性化的发展计划。<br>
            <span style="display: block; margin-top: 8px; font-weight: bold;">* 由于该量表仅为辅助筛查工具，测试结果仅供参考。</span>
        </div>
    

    </div>
    """
    return html_template



# ---------------------------------------------------------------------------------------------
# 把用户的年龄和总分在你的 Norm.csv 里比对，查出百分位数；再拿着百分位数去 text.csv 里把对应的解读和建议捞出来



def calculate_report_data(name, gender, age, test_date, total_score, factor_scores, norm_df, text_df):
    """
    核心对常模及评语匹配算法
    """
    # ----------- 1. 查找常模表 (Norm.csv) 匹配百分位数 -----------
    # 锁定最接近的年龄行
    available_ages = norm_df['Age'].astype(float).values
    target_age = float(age)
    
    # 寻找常模中与用户实际年龄最接近的那一行
    closest_age = available_ages[np.abs(available_ages - target_age).argmin()]
    age_row = norm_df[norm_df['Age'].astype(float) == closest_age].iloc[0]
    
    # 获取常模中定义的所有百分位列名：['0.95', '0.9', '0.75', '0.5', '0.25', '0.1', '0.05']
    percentile_columns = ['0.95', '0.9', '0.75', '0.5', '0.25', '0.1', '0.05']
    
    matched_p = "0.05"  # 默认兜底（极低分数）
    
    # 从高到低比对分数界限
    for p_col in percentile_columns:
        boundary_score = int(age_row[p_col])
        if total_score >= boundary_score:
            matched_p = p_col
            break  # 找到了符合的最高百分位，跳出循环

    # 将小数值格式化为易懂的文本（例如 0.95 -> ≥95）
    p_num = float(matched_p) * 100
    if p_num == 95:
        p_text = "≥95"
    elif p_num == 5:
        p_text = "＜5" if total_score < int(age_row["0.05"]) else "5~24"
    else:
        # 对应 text.csv 中的区间范围
        if p_num == 90: p_text = "75~94"
        elif p_num == 75: p_text = "75~94"
        elif p_num == 50: p_text = "25~74"
        elif p_num == 25: p_text = "25~74"
        elif p_num == 10: p_text = "5~24"
        else: p_text = "5~24"

    # ----------- 2. 查找评语表 (text.csv) 匹配文字内容 -----------
    # 根据生成的 p_text 区间，去 text_df 中匹配
    text_match = text_df[text_df['标准分数'] == p_text]
    
    if not text_match.empty:
        level_text = text_match['智力水平'].iloc[0]
        rank_val = text_match['等级'].iloc[0]
        interpretation_text = text_match['结果解读'].iloc[0]
        suggestions_text = text_match['指导建议'].iloc[0]
    else:
        # 万一匹配失败的兜底安全方案
        level_text = "平均水平"
        rank_val = "3.0"
        interpretation_text = "受测者的智力素质处于同龄群体的常规水平。"
        suggestions_text = "建议制定针对性的思维训练计划。"

    # ----------- 3. 打包完整数据结构 -----------
    report_data = {
        "name": name,
        "gender": gender,
        "age": age,
        "date": test_date,
        "total_score": total_score,
        "factor_scores": factor_scores,  # 传入字典，例如：{"感知辨别": 10, "相似性比较": 11...}
        "percentile": f"第 {int(float(matched_p)*100)} 百分位数 ({p_text})",
        "level": level_text,
        "rank": rank_val,
        "interpretation": interpretation_text,
        "suggestions": suggestions_text
    }
    
    return report_data


