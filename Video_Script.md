# Video Script / 演讲稿 (Bilingual)

## Intro / 开场

**EN:** Hi, I'm LIYUZHOU, ID 0398565. This is my ITS72604 final exam project. I'll walk through the code file by file.

**中文：** 大家好，我是 LIYUZHOU，学号 0398565。这是我的 ITS72604 期末项目，我会逐个文件讲解代码。

---

## File 1: `energy_pipeline.py` / 数据管道

**EN:** This file reads the raw CSV, cleans it, and engineers features. The constants define required columns, valid categories, and billing rates — AC is MYR 6/hour, DC is MYR 15/hour, 25% peak surcharge for hours 12–17.

**中文：** 这个文件读取原始 CSV、清洗数据、构造特征。常量定义了必需列、有效类别、计费费率——AC 每小时 6 马币，DC 每小时 15 马币，12 到 17 点加收 25%。

**EN:** `read_sessions` loads the CSV and checks for missing columns. `clean_sessions` does the core work: it converts numeric columns, filters impossible battery temperatures, imputes missing Energy_kWh using the **group median by Charger_Type**, and validates categorical labels.

**中文：** `read_sessions` 加载 CSV 并检查缺失列。`clean_sessions` 做核心工作：转换数值列、过滤不可能的电池温度、按 Charger_Type 分组用**中位数填补**缺失的 Energy_kWh、校验类别标签。

**EN:** Feature engineering: Power Rate = Energy ÷ Duration. Carbon Savings = Energy × 0.475. Base Fee = Duration × hourly rate. Peak Surcharge = 25% if hour is 12–17. Overstay Fee = MYR 0.50/min after 15-min grace. Net Billable = Base + Peak + Overstay.

**中文：** 特征工程：功率率 = 能量 ÷ 时长。碳减排 = 能量 × 0.475。基础费 = 时长 × 时费率。高峰附加费 = 12–17 点收 25%。超停费 = 15 分钟宽限后每分钟 0.50 马币。净账单 = 基础 + 高峰 + 超停。

**EN:** The demo dates are assigned by Session_ID order because the source has no timestamp — this is only for demonstrating the date filter.

**中文：** 源文件没有时间戳，所以按 Session_ID 顺序分配演示日期——仅用于演示日期筛选功能。

---

## File 2: `visualizations.py` / 可视化

**EN:** This module creates five charts. Figure 1: hourly demand proxy vs a labelled synthetic solar curve. Figure 2: cost distribution by user type — box plot. Figure 3: battery temperature vs energy — scatter plot with trend line. Figure 4: hourly revenue by charger type — bar chart. Figure 5: correlation heatmap.

**中文：** 这个模块生成五张图。图1：小时负荷代理 vs 标注为合成的太阳能曲线。图2：按用户类型的费用分布——箱线图。图3：电池温度 vs 能量——带趋势线的散点图。图4：按充电类型的小时收入——柱状图。图5：相关性热图。

---

## File 3: `app.py` / 仪表板

**EN:** This is the Streamlit dashboard. `filter_sessions` applies the date, energy, and charger filters. The sidebar has a date picker, energy slider, charger multiselect, and temperature slider.

**中文：** 这是 Streamlit 仪表板。`filter_sessions` 应用日期、电量、充电类型筛选。侧边栏有日期选择器、电量滑块、充电类型多选、温度滑块。

**EN:** High-risk sessions = overstay > 20 min AND temperature above threshold. More than 5 triggers a red error banner; 1–5 shows a yellow warning.

**中文：** 高风险会话 = 超停 > 20 分钟 且 温度超过阈值。超过 5 条触发红色错误横幅；1–5 条显示黄色警告。

**EN:** Four KPI cards show total energy, carbon offset, revenue, and alert count. Below are the revenue bar chart, power-rate trend, user-type box plot, risk table, and a CSV download button.

**中文：** 四张 KPI 卡片显示总能量、碳减排、收入、告警数。下方是收入柱状图、功率率趋势、用户类型箱线图、风险表，以及 CSV 下载按钮。

---

## Demo / 演示

**EN:** Let me run the pipeline first, then open the dashboard. I'll move the temperature slider — the alerts and KPIs update in real time. I can also download the filtered data.

**中文：** 我先运行管道，然后打开仪表板。我移动温度滑块——告警和 KPI 实时更新。还可以下载筛选后的数据。

---

## Closing / 结尾

**EN:** All code, data, figures, and the report are on my GitHub. The link is in the report. Thanks for watching.

**中文：** 所有代码、数据、图表和报告都在我的 GitHub 上，链接在报告里。谢谢观看。

---

## Checklist / 录制清单

| # | What / 内容 | Time / 时长 |
|---|-------------|------------|
| 1 | `energy_pipeline.py` 逐函数讲解 | 3:00 |
| 2 | `visualizations.py` 五张图 | 1:30 |
| 3 | `app.py` 仪表板各部分 | 2:30 |
| 4 | 现场运行演示 | 1:30 |
| | **Total / 总计** | **~8 分钟** |
