# lowCode-Graph

一个用于展示低代码热点组件分析结果的可视化项目。

项目由两部分组成：

- Python 数据处理脚本：将原始热点子图数据转换成前端可直接消费的结构化 JSON。
- Vue 可视化前端：基于 Vue 3、Element Plus 和 ECharts 展示概览、定义、热点簇列表和热点详情。

## 页面功能

当前界面包含 4 个主要标签页：

- 分析概览：展示报告元信息和热点组件统计。
- 相关定义：展示热点组件挖掘定义、相似性维度和支持度规则。
- Top 热点组件：按结构相似或语义相似查看热点簇列表，并支持关系图预览。
- 热点组件详情：展开查看热点簇实例、语义描述、关键差异点和实例关系图。

## 技术栈

- 前端：Vue 3、Vite、Element Plus、ECharts
- 数据处理：Python 3
- 构建工具：Vite

## 环境要求

- Node.js 18+
- npm 9+
- Python 3.10+

## 快速开始

### 1. 安装前端依赖

```bash
npm install
```

### 2. 准备数据文件

项目当前使用以下输入文件：

- `data/frequent_subgraphs.json`：热点簇主数据，包含结构相似与语义相似聚类、实例、报告元信息等。
- `data/edge_and_vertex_mapping.txt`：节点类型与边关系编码映射。

如果你已经有现成的 `src/assets/graph_table_data.json`，可以跳过数据处理，直接启动前端。

### 3. 生成前端数据

```bash
npm run process-data
```

等价命令：

```bash
python scripts/process_data.py
```

该步骤会生成或覆盖：

- `src/assets/graph_table_data.json`

### 4. 启动开发环境

```bash
npm run dev
```

### 5. 构建与预览

```bash
npm run build
npm run preview
```

## 数据流说明

处理脚本为：

- `scripts/process_data.py`

输入文件：

- `data/frequent_subgraphs.json`
- `data/edge_and_vertex_mapping.txt`

静态说明数据：

- `src/assets/defs.json`：定义页展示内容和支持度规则。

输出文件：

- `src/assets/graph_table_data.json`

输出 JSON 主要包含：

- `meta`：报告日期、版本、生成工具版本、覆盖仓库等元信息。
- `overview_stats`：热点簇数量、实例数量、项目数、页面数和组件类型统计。
- `top_hotspot`：Top 热点簇表格数据。
- `hotspot_details`：热点簇详情数据。
- `charts.subgraphs`：子图级关系图数据。
- `charts.instances`：实例级关系图数据。

## 项目结构

```text
lowCode-Graph/
├─ data/
│  ├─ edge_and_vertex_mapping.txt
│  └─ frequent_subgraphs.json
├─ scripts/
│  └─ process_data.py
├─ src/
│  ├─ assets/
│  │  ├─ defs.json
│  │  └─ graph_table_data.json
│  ├─ components/
│  │  └─ tabs/
│  │     ├─ DefinitionsTab.vue
│  │     ├─ HotspotDetailsTab.vue
│  │     ├─ OverviewTab.vue
│  │     └─ TopHotspotTab.vue
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

- `npm run process-data`：执行数据转换脚本。
- `npm run dev`：启动 Vite 开发服务器。
- `npm run build`：构建生产版本。
- `npm run preview`：本地预览构建产物。

## 部署说明

`vite.config.js` 中已配置 `base: './'`，适合将构建产物部署为相对路径静态站点。

## 注意事项

- `npm run process-data` 依赖当前环境中的 `python` 命令，请确保它指向可用的 Python 3。
- 更新 `data/frequent_subgraphs.json` 或 `data/edge_and_vertex_mapping.txt` 后，需要重新执行 `npm run process-data`。
- 如果页面数据与最新分析结果不一致，优先检查 `src/assets/graph_table_data.json` 是否已重新生成。
