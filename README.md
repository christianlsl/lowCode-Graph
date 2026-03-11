# lowCode-Graph

一个用于展示低代码热点组件分析结果的可视化项目。

项目由两部分组成：

- Python 数据处理脚本：将原始热点子图数据转换成前端可直接消费的结构化 JSON。
- Vue 可视化前端：基于 Vue 3、Element Plus 和 ECharts 展示概览、定义、结构相似热点和语义相似热点。

## 页面功能

当前界面包含 4 个主要标签页：

- 分析概览：展示报告元信息和热点组件统计。
- 相关定义：展示热点组件挖掘定义、相似性维度和支持度规则。
- 结构相似热点组件：查看结构热点簇列表、实例详情，并支持树形图 / 有向图切换。
- 语义相似热点组件：查看语义热点簇及其关联的结构簇、语义描述与关键差异点。

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

- `data/data.json`：热点簇主数据，包含结构相似与语义相似聚类、统计信息、报告元信息等。
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

- `data/data.json`
- `data/edge_and_vertex_mapping.txt`

静态说明数据：

- `src/assets/defs.json`：定义页展示内容和支持度规则。

输出文件：

- `src/assets/graph_table_data.json`

输出 JSON 主要包含：

- `meta`：报告日期、版本、生成工具版本、覆盖仓库等元信息。
- `overview_stats`：热点簇数量、实例数量、项目数、页面数和组件类型统计。
- `structure_hotspot.rows`：结构相似热点簇数据（含实例列表和关系图键）。
- `semantic_hotspot.rows`：语义相似热点簇数据（含关联结构簇映射）。
- `charts.subgraphs`：子图级关系图数据。

其中 `charts.subgraphs[*]` 额外包含 `tree` 字段，供结构热点页的树形视图使用。

## 项目结构

```text
lowCode-Graph/
├─ data/
│  ├─ edge_and_vertex_mapping.txt
│  └─ data.json
├─ scripts/
│  └─ process_data.py
├─ src/
│  ├─ assets/
│  │  ├─ defs.json
│  │  └─ graph_table_data.json
│  ├─ components/
│  │  └─ tabs/
│  │     ├─ DefinitionsTab.vue
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

- `npm run process-data`：执行数据转换脚本。
- `npm run dev`：启动 Vite 开发服务器。
- `npm run build`：构建生产版本。
- `npm run preview`：本地预览构建产物。

## 部署说明

`vite.config.js` 中已配置 `base: './'`，适合将构建产物部署为相对路径静态站点。

## 注意事项

- `npm run process-data` 依赖当前环境中的 `python` 命令，请确保它指向可用的 Python 3。
- 更新 `data/data.json` 或 `data/edge_and_vertex_mapping.txt` 后，需要重新执行 `npm run process-data`。
- 如果页面数据与最新分析结果不一致，优先检查 `src/assets/graph_table_data.json` 是否已重新生成。

## 文件结构

### `data.json`

#### 字段定义文档

```json
{
  "fields_definition": {
    "meta_data": {
      "type": "Object",
      "description": "报告的元数据信息",
      "properties": {
        "report_date": { "type": "String", "description": "报告生成的日期 (YYYY-MM-DD)" },
        "report_version": { "type": "String", "description": "报告的版本号" },
        "generator_tool_version": { "type": "String", "description": "生成该报告的工具版本" },
        "covered_repositories": { "type": "Array[String]", "description": "报告覆盖的代码仓库名称列表" }
      }
    },
    "statistic": {
      "type": "Object",
      "description": "全局统计数据摘要",
      "properties": {
        "hotspot_clusters": { "type": "Integer", "description": "识别出的热点簇总数" },
        "hotspot_instances": { "type": "Integer", "description": "热点实例总数" },
        "projects_involved": { "type": "Integer", "description": "涉及的项目数量" },
        "pages_involved": { "type": "Integer", "description": "涉及的页面数量" },
        "components_involved": { "type": "Integer", "description": "涉及的组件数量" },
        "services_involved": { "type": "Integer", "description": "涉及的服务接口数量" },
        "models_involved": { "type": "Integer", "description": "涉及的数据模型数量" }
      }
    },
    "structure_similar_clusters": {
      "type": "Array[Object]",
      "description": "基于结构相似度聚类的结果列表",
      "items_properties": {
        "structure_cluster_id": { "type": "Integer", "description": "结构簇的唯一标识 ID" },
        "type": { "type": "String", "description": "簇的类别（如：页面、组件）" },
        "name": { "type": "String", "description": "该结构簇的业务名称" },
        "support": { "type": "Integer", "description": "支持度（该结构出现的频次或实例数）" },
        "size": { "type": "Integer", "description": "结构内部节点的规模" },
        "code_lines": { "type": "Integer", "description": "该结构涉及的代码行数" },
        "relevent_projects_num": { "type": "Integer", "description": "涉及的项目总数" },
        "graph_structure_data": { "type": "Array[String]", "description": "图结构数据，包含顶点(v)和边(e)的拓扑信息" },
        "summary": { "type": "String", "description": "该结构的功能与应用场景总结" },
        "instances": {
          "type": "Array[Object]",
          "description": "该结构簇下的具体实现实例",
          "properties": {
            "instance_id": { "type": "Integer", "description": "实例唯一 ID" },
            "page_path": { "type": "String", "description": "实例所在的源代码路径" },
            "component_id_list": { "type": "Array[String]", "description": "该实例包含的组件或服务 ID 列表" },
            "instance_summary": { "type": "String", "description": "该特定实例的功能描述" }
          }
        },
        "instance_defference": { "type": "String", "description": "描述该簇下不同实例之间的主要差异点" }
      }
    },
    "semantic_similar_clusters": {
      "type": "Array[Object]",
      "description": "基于语义相似度（业务逻辑）聚类的结果列表",
      "items_properties": {
        "semantic_similar_cluster_id": { "type": "Integer", "description": "语义簇的唯一标识 ID" },
        "type": { "type": "String", "description": "簇的类别" },
        "name": { "type": "String", "description": "语义聚类的名称" },
        "struc_cluster_num": { "type": "Integer", "description": "包含的结构簇数量" },
        "relevent_projects_num": { "type": "Integer", "description": "涉及的项目数量" },
        "description": { "type": "String", "description": "业务语义的详细描述" },
        "structure_cluster_id": { "type": "Array[Integer]", "description": "该语义簇关联的结构簇 ID 列表" },
        "instance_defference": { "type": "String", "description": "不同实现方式（如按钮与工具栏）的语义差异描述" }
      }
    }
  }
}
```

#### example

```json
{
  "meta_data":{
      "report_date": "2026-3-11",
      "report_version": "v1.0",
      "generator_tool_version": "v1.0",
      "covered_repositories": ["SQM","Trouble_ticket"]
  },
  "statistic":{
    "hotspot_clusters": 1,
    "hotspot_instances": 2,
    "projects_involved": 1,
    "pages_involved": 1,
    "components_involved": 1,
    "services_involved": 1,
    "models_involved": 1
  },
  "structure_similar_clusters": [
    {
      "structure_cluster_id": 0,
      "type": "页面",
      "name": "登录组件",
      "support": 2,
      "size": 5,
      "code_lines": 10,
      "relevent_projects_num": 2,
      "graph_structure_data": [
        "v 0 1001",
        "v 1 0",
        "v 2 1002",
        "v 3 1003",
        "v 4 1004",
        "v 5 1005",
        "v 6 3000",
        "v 7 3000",
        "e 1 0 8",
        "e 0 3 8",
        "e 0 4 8",
        "e 0 5 8",
        "e 1 2 8",
        "e 4 7 4",
        "e 5 6 4"
      ],
      "summary": "用于登录的组件，包括xxxxxx",
      "instance_defference": "instance_defference",
      "instances": [
        {
          "instance_id": 0,
          "page_path": "AbnormalCheckInDashboard/AbnormalCheckInDashboard/abnormal_business_trips_management",
          "component_id_list": ["",""],
          "instance_summary": "instance_summary_0_1"
        },
        {
          "instance_id": 1,
          "page_path": "AbnormalCheckInDashboard/AbnormalCheckInDashboard/abnormal_business_trips_management",
          "component_list": ["",""],
          "instance_summary": "instance_summary_0_2"
        }
      ]    
    }
  ],
  "semantic_similar_clusters": [
    {
      "semantic_similar_cluster_id": 0,
      "type": "页面",
      "name": "通信基站查询组件组合",
      "struc_cluster_num": 10,
      "relevent_projects_num": 2,
      "description": "都是关于通信基站的查询操作",
      "structure_cluster_id":[1,2,3],
      "instance_defference":"有些是使用按钮和表格的结实现，有些是使用工具栏和表格的结构实现"
    }
  ]
}
```

### `edge_and_vertex_mapping.txt`

node和edge的定义dict