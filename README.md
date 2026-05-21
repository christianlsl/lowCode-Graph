# lowCode-Graph

低代码热点组件分析可视化项目，包含 Python 预处理脚本和 Vue 前端展示。

## 项目概览

项目由两部分组成：

- **数据预处理**：通过 [scripts/process_data.py](scripts/process_data.py) 聚合输入数据，生成前端统一数据文件。
- **前端可视化**：基于 Vue 3、Element Plus、ECharts 展示分析概览、定义、结构热点和语义热点。

## 技术栈

**前端**

- Vue 3 (Composition API + `<script setup>`)
- Element Plus (UI 组件库)
- ECharts (图表可视化)
- highlight.js (代码高亮)
- v-code-diff (代码差异对比)

**构建工具**

- Vite 5
- @vitejs/plugin-legacy (IE 11 兼容)

**数据处理**

- Python 3.10+

## 环境要求

- Node.js 18+
- npm 9+
- Python 3.10+（需在 PATH 中可用 `python` 命令）

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 准备输入数据

将数据文件放入 `data/` 目录（详见"输入文件说明"）。

### 3. 生成前端数据

```bash
npm run process-data
```

等价命令：

```bash
python scripts/process_data.py
```

### 4. 启动开发服务器（可选）

用于dev开发

```bash
npm run dev
```

### 5. 构建与预览

构建静态结果文件

```bash
npm run build
npm run preview
```

### 6. 查看分析结果

点击./dist/index.html即可查看可视化页面

## 所需数据说明

数据处理脚本会读取 `data` 目录中的以下文件：

| 文件                               | 说明                                                          | 必需 |
| ---------------------------------- | ------------------------------------------------------------- | ---- |
| `data/data_*.json`                 | 主输入数据，支持多份合并。若不存在则回退读取 `data/data.json` | 是   |
| `data/edge_and_vertex_mapping.txt` | 节点类型和边关系编码映射                                      | 是   |
| `data/clone_detection_result.json` | 脚本函数克隆检测结果（code clone）                            | 否   |
| `data/model_result.json`           | 模型相似热点输入                                              | 否   |
| `data/defs.json`                   | 定义页静态说明（前端直接使用）                                | 否   |

## 数据处理脚本输出

预处理产物：[src/assets/graph_table_data.json](src/assets/graph_table_data.json)

主要输出字段：

- `meta`：报告日期、版本、覆盖仓库等元信息。
- `overview_stats`：全局统计指标（按组件类型分类）。
- `structure_hotspot.rows`：结构热点父子分组数据。
- `clone_detection.rows`：脚本函数组表格数据（挂接到结构热点页）。
- `clone_detection.groups`：脚本函数组详情和相似度区间。
- `semantic_hotspot.rows`：语义热点联合簇聚合结果。
- `charts.subgraphs`：结构子图数据（含 `tree` 字段供树视图展示）。

## 页面功能

界面包含 5 个标签页：

### 分析概览

报告元信息（日期、版本、覆盖仓库）和统计指标。

### 相关定义

热点定义、相似性维度和支持度规则的静态说明。

### 结构相似热点组件

- **顶部表格**：展示结构热点父子分组，支持搜索和类型筛选
  - 簇类型、结构 cluster_id、热点簇名称、组件大小、复用次数、涉及工程个数
  - 父行可展开子行，支持自定义排序
- **关系图区**：
  - 树形视图：El Tree 展示层级结构
  - 有向图：ECharts force-directed 布局，节点按类型着色
- **脚本函数组（Code Clone）**：
  - 函数组对比：左右选择两个函数形态，使用 v-code-diff 进行代码差异对比
  - 函数详情：展示整体功能、相似函数组差异、复用机会、涉及工程、相似度范围
  - 函数形态列表：每种形态可展开查看代码，展示文件路径和行号范围
- **详情区**：
  - 结构簇详情：组件类型、摘要、关键差异点（语义）、实例列表
  - 实例列表支持查看关联文件（弹窗多列对比，JSON 语法高亮）

### 语义相似热点组件

- **顶部表格**：展示联合簇聚合指标
  - cluster_id、业务领域、技术功能、类型、结构变体总数、复用次数、覆盖工程数
  - 支持按技术功能、业务领域、组件类型筛选
- **关系图区**：可切换结构簇，支持树形/有向图视图
- **详情区**：
  - 展示业务领域、类型等信息
  - 按结构簇分组展示实例列表
  - 实例支持查看关联文件

### 模型相似热点组件

- **数据源**：`data/model_result.json` 的 `frequent_patterns`
- **顶部表格**：展示相似簇名称、支持率、模型支持度
- **详情区**：
  - 相似字段组名称、介绍、模型支持度、支持率
  - 相似字段组包含的所有字段（表格）
  - 关联模型列表（表格，支持查看模型文件）

## 数据模型

### 语义热点数据模型

`semantic_hotspot.rows` 每一项来自输入 `structure_domain_joint_clusters` 的一个联合簇，核心字段：

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

### Code Clone 数据模型

`clone_detection_result.json` 会被转换为：

- `clone_detection.rows`：结构页顶部表格可展示的脚本函数组父子行
- `clone_detection.groups`：结构页详情区可展开的 type1 函数组、函数源码与相似度信息

结构页中"脚本"类型行支持：

- 函数组左右对比
- 函数源码展开
- 高亮差异查看

### 模型相似热点数据模型

`data/model_result.json` 中 `frequent_patterns` 每一项用于"模型相似热点组件"页签，核心字段：

- `name`：相似簇名称
- `description`：相似簇介绍
- `itemsets`：相似簇包含的所有元素
- `total_trans`：当前工程下所有元素个数
- `support_count`：字段组合同时出现的模型数量（模型支持度）
- `support`：支持率
- `model_list`：使用当前相似簇元素的模型名称列表
- `model_path_list`：模型文件路径列表（用于查看模型文件）

## 交互功能

### 文件夹选择

页面顶部支持选择本地文件夹，用于：

- 查看实例关联的原始文件内容
- 查看模型文件内容
- 文件匹配支持相对路径和文件名模糊匹配

### 搜索与筛选

各标签页均支持：

- 关键词搜索（支持多字段模糊匹配）
- 类型/领域筛选
- 自定义排序
- 分页显示

### 图表交互

- 树形视图：El Tree 组件，默认展开所有节点
- 有向图：ECharts force-directed 布局
  - 节点按类型着色（25 色调色板）
  - 支持拖拽、缩放
  - 边标签显示关系类型
  - Tooltip 显示详细信息

## 项目结构

```text
lowCode-Graph/
├─ data/
│  ├─ data_single_page.json          # 主输入数据（示例）
│  ├─ clone_detection_result.json    # 克隆检测结果
│  ├─ defs.json                      # 定义页说明
│  ├─ edge_and_vertex_mapping.txt    # 节点/边类型映射
│  └─ model_result.json              # 模型相似热点数据
├─ scripts/
│  └─ process_data.py                # 数据预处理脚本
├─ src/
│  ├─ assets/
│  │  └─ graph_table_data.json       # 预处理输出
│  ├─ components/
│  │  └─ tabs/
│  │     ├─ OverviewTab.vue          # 分析概览
│  │     ├─ DefinitionsTab.vue       # 相关定义
│  │     ├─ StructureHotspotTab.vue  # 结构相似热点（含 Code Clone）
│  │     ├─ SemanticHotspotTab.vue   # 语义相似热点
│  │     └─ ModelSimilarityHotspotTab.vue  # 模型相似热点
│  ├─ utils/
│  │  └─ graphOption.js              # ECharts 图表配置
│  ├─ App.vue                        # 主应用（标签页 + 文件夹选择）
│  ├─ main.js                        # 入口文件
│  └─ style.css                      # 全局样式
├─ index.html
├─ package.json
├─ vite.config.js
└─ README.md
```

## 常用命令

| 命令                   | 说明                         |
| ---------------------- | ---------------------------- |
| `npm run process-data` | 执行预处理脚本，生成前端数据 |
| `npm run dev`          | 启动开发服务器               |
| `npm run build`        | 构建生产版本                 |
| `npm run preview`      | 预览构建产物                 |

## 注意事项

1. `npm run process-data` 依赖当前环境中的 `python` 命令
2. 修改 `data/data_*.json`、`data/clone_detection_result.json`、`data/edge_and_vertex_mapping.txt` 后，需要重新执行 `npm run process-data`
3. `data/model_result.json` 由前端直接读取，无需预处理
4. 页面数据异常时，优先检查 [src/assets/graph_table_data.json](src/assets/graph_table_data.json) 是否为最新产物
5. 文件夹选择功能使用 WebkitDirectory API，需要浏览器支持
6. 项目已配置 legacy 插件支持 IE 11，但建议使用现代浏览器获得最佳体验
