# lowCode-Graph

一个用于展示低代码高频组件子图的可视化项目。

项目包含两部分：
- 数据预处理：将原始图数据转换为前端可直接消费的结构化 JSON。
- 前端可视化：基于 Vue 3 + Element Plus + ECharts 展示子图表格、聚类实例和关系图。

## 功能特性

- 展示高频子图（`subgraph`）及其 `support` 信息。
- 按语义聚类（`domain_semantic_clusters`）展开查看实例。
- 一键查看子图或实例的关系图（节点/边 + 类型和关系标签）。
- 查看 `structure_analysis` 分析详情（弹窗展示）。

## 技术栈

- 前端：Vue 3、Vite、Element Plus、ECharts
- 脚本：Python 3（用于数据处理）

## 环境要求

- Node.js 18+
- npm 9+
- Python 3.10+（建议使用虚拟环境）

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 处理数据
根目录新建data/
```bash
mkdir data
```
把所需的三个源数据文件放入data/
+ data/edge_and_vertex_mapping.txt
+ data/final_result.json
+ data/origin_graph_data.json

使用python脚本转换为前端数据 `src/assets/graph_table_data.json`：

```bash
npm run process-data
```

等价命令：

```bash
python scripts/process_data.py
```

### 3. 启动开发环境

```bash
npm run dev
```

默认由 Vite 启动本地开发服务。

### 4. 构建与预览

```bash
npm run build
npm run preview
```

## 数据流说明

输入文件：
- `data/final_result.json`：频繁子图结果、实例信息、结构分析等。
- `data/origin_graph_data.json`：原始图基础信息（如 `graph_id` 到 `page_path` 的映射）。
- `data/edge_and_vertex_mapping.txt`：节点类型和边关系编码映射。

处理脚本：
- `scripts/process_data.py`

输出文件：
- `src/assets/graph_table_data.json`

输出内容主要包含：
- `table_rows`：表格分层数据（subgraph -> cluster -> instance）
- `charts.subgraphs`：子图可视化数据
- `charts.instances`：实例可视化数据
- `meta`：生成时间与统计信息

## 项目结构

```text
lowCode-Graph/
├─ data/
│  ├─ edge_and_vertex_mapping.txt
│  ├─ final_result.json
│  └─ origin_graph_data.json
├─ scripts/
│  └─ process_data.py
├─ src/
│  ├─ assets/
│  │  └─ graph_table_data.json
│  ├─ App.vue
│  ├─ main.js
│  └─ style.css
├─ index.html
├─ package.json
└─ vite.config.js
```

## 常用脚本

- `npm run process-data`：执行数据转换。
- `npm run dev`：启动开发服务器。
- `npm run build`：打包生产版本。
- `npm run preview`：本地预览构建产物。

## 注意事项

- 如果 `npm run process-data` 失败，请确认当前 `python` 命令指向可用的 Python 3 环境。
- 数据更新后需重新执行 `npm run process-data`，否则前端仍使用旧的 `graph_table_data.json`。
- `vite.config.js` 已配置 `base: './'`，便于静态部署。
