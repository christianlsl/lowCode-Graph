# lowCode-Graph

低代码热点组件分析可视化项目，包含 Python 预处理脚本和 Vue 前端展示。

## 项目概览

项目由两部分组成：

- 数据预处理：通过 [scripts/process_data.py](scripts/process_data.py) 聚合输入数据，生成前端统一数据文件。
- 前端可视化：基于 Vue 3、Element Plus、ECharts 展示分析概览、定义、结构热点和语义热点。

## 页面功能

当前界面包含 5 个标签页：

- 分析概览：报告元信息和统计指标。
- 相关定义：热点定义、相似性维度和支持度规则。
- 结构相似热点组件：
  - 结构热点树表和关系图（树形 / 有向图）。
  - 脚本函数相似（code clone）结果融合在该页，支持函数组对比和代码差异查看。
- 语义相似热点组件：
  - 顶部表格展示联合簇（`structure_domain_joint_clusters`）聚合指标。
  - 明细联动到图卡片，并按“联合簇 -> items -> 实例”展示。
- 模型相似热点组件：
  - 数据源为 `data/model_result.json` 的 `frequent_patterns`。
  - 顶部表格展示 `name`、`support`、`support_count`、`total_trans`，并支持“查看详情”。
  - 详情区为单卡模式，仅显示当前选中行；`itemsets` 与 `model_list` 使用表格展示。

## 技术栈

- 前端：Vue 3、Vite、Element Plus、ECharts
- 数据处理：Python 3
- 构建工具：Vite

## 环境要求

- Node.js 18+
- npm 9+
- Python 3.10+

## 快速开始

1. 安装依赖

```bash
npm install
```

2. 准备输入数据（见“输入文件说明”）

3. 生成前端数据

```bash
npm run process-data
```

等价命令：

```bash
python scripts/process_data.py
```

4. 启动开发

```bash
npm run dev
```

5. 构建与预览

```bash
npm run build
npm run preview
```

## 输入文件说明

数据脚本会读取 `data` 目录中的以下文件：

- `data/data_*.json`：主输入数据，支持多份合并。
  - 若不存在 `data_*.json`，会回退读取 `data/data.json`。
- `data/edge_and_vertex_mapping.txt`：节点类型和边关系编码映射。
- `data/clone_detection_result.json`：脚本函数相似（code clone）输入，数组结构，可选。
- `data/defs.json`：定义页静态说明（前端直接使用）。
- `data/model_result.json`：模型相似热点输入（前端直接使用 `frequent_patterns`）。

## 输出文件说明

预处理产物：

- [src/assets/graph_table_data.json](src/assets/graph_table_data.json)

主要输出字段：

- `meta`：报告日期、版本、覆盖仓库等元信息。
- `overview_stats`：全局统计指标。
- `structure_hotspot.rows`：结构热点父子分组数据。
- `clone_detection.rows`：脚本函数组表格数据（挂接到结构热点页）。
- `clone_detection.groups`：脚本函数组详情和相似度区间。
- `semantic_hotspot.rows`：语义热点联合簇聚合结果。
- `charts.subgraphs`：结构子图数据（含 `tree` 字段供树视图展示）。

## 语义热点数据模型（当前实现）

`semantic_hotspot.rows` 每一项来自输入 `structure_domain_joint_clusters` 的一个联合簇，核心字段如下：

- `cluster_id`
- `structure_name`
- `domain_name`
- `type`
- `structure_variant_count`：`items.structure_cluster_id` 去重计数
- `reuse_count`：`items.instance_ids` 去重计数
- `covered_projects_count`：命中实例 `page_path` 一级目录去重计数
- `available_structure_cluster_ids`：可联动图卡片的结构簇 ID 列表
- `items_expanded`：按 item 展开的明细，含 `instances`

排序规则：

1. `domain_name` 分组（升序）
2. `reuse_count` 降序
3. `covered_projects_count` 降序
4. `cluster_id` 升序

## Code Clone 数据模型（当前实现）

`clone_detection_result.json` 会被转换为：

- `clone_detection.rows`：结构页顶部表格可展示的脚本函数组父子行
- `clone_detection.groups`：结构页详情区可展开的 type1 函数组、函数源码与相似度信息

结构页中“脚本”类型行支持：

- 函数组左右对比
- 函数源码展开
- 高亮差异查看

## 模型相似热点数据模型（当前实现）

`data/model_result.json` 中 `frequent_patterns` 每一项用于“模型相似热点组件”页签，核心字段如下：

- `name`：相似簇名称
- `description`：相似簇介绍
- `itemsets`：相似簇包含的所有元素
- `total_trans`：当前工程下所有元素个数
- `support_count`：字段组合同时出现的模型数量（模型支持度）
- `support`：支持率
- `model_list`：使用当前相似簇元素的模型名称列表

页面交互：

- 顶部表格按行展示 `frequent_patterns`。
- 点击“查看详情”后滚动到下方详情区。
- 详情区仅显示当前选中行单卡，`itemsets` 与 `model_list` 以表格形式展示。

## 项目结构

```text
lowCode-Graph/
├─ data/
│  ├─ clone_detection_result.json
│  ├─ defs.json
│  ├─ edge_and_vertex_mapping.txt
│  ├─ model_result.json
│  └─ data_*.json
├─ scripts/
│  └─ process_data.py
├─ src/
│  ├─ assets/
│  │  └─ graph_table_data.json
│  ├─ components/
│  │  └─ tabs/
│  │     ├─ DefinitionsTab.vue
│  │     ├─ ModelSimilarityHotspotTab.vue
│  │     ├─ OverviewTab.vue
│  │     ├─ SemanticHotspotTab.vue
│  │     └─ StructureHotspotTab.vue
│  ├─ utils/
│  │  └─ graphOption.js
│  ├─ App.vue
│  ├─ main.js
│  └─ style.css
├─ index.html
├─ package.json
├─ README.md
└─ vite.config.js
```

## 常用命令

- `npm run process-data`：执行预处理脚本，生成前端数据。
- `npm run dev`：启动开发服务器。
- `npm run build`：构建生产版本。
- `npm run preview`：预览构建产物。

## 部署说明

[vite.config.js](vite.config.js) 已配置 `base: './'`，适合相对路径静态部署。

## 注意事项

- `npm run process-data` 依赖当前环境中的 `python` 命令。
- 修改 `data/data_*.json`、`data/clone_detection_result.json`、`data/edge_and_vertex_mapping.txt` 后，需要重新执行 `npm run process-data`。
- 页面数据异常时，优先检查 [src/assets/graph_table_data.json](src/assets/graph_table_data.json) 是否为最新产物。
