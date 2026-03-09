<template>
    <el-container class="page">
        <el-header class="header">低代码数字孪生关系图</el-header>
        <el-main class="main">
            <el-row :gutter="16" class="layout-row">
                <el-col :xs="24" :lg="13">
                    <el-card class="panel-card" shadow="hover">
                        <template #header>
                            <div class="card-header">频繁子图树形表</div>
                        </template>

                        <el-table :data="subgraphRows" border row-key="row_id" max-height="72vh"
                            :row-style="{ background: '#eff6ff' }">
                            <el-table-column type="expand" width="56">
                                <template #default="scope">
                                    <div class="expand-wrap">
                                        <el-card v-for="cluster in scope.row.children || []" :key="cluster.row_id"
                                            class="cluster-card" shadow="never">
                                            <template #header>
                                                <div class="cluster-title">
                                                    {{ cluster.group_name }}
                                                </div>
                                            </template>

                                            <el-table :data="cluster.children || []" size="small" border>
                                                <el-table-column prop="instance_id" label="instance_id"
                                                    min-width="100" />
                                                <el-table-column prop="graph_id" label="graph_id" min-width="100" />
                                                <el-table-column prop="domain_label" label="domain_label"
                                                    min-width="160" show-overflow-tooltip />
                                                <el-table-column prop="page_path" label="page_path" min-width="300"
                                                    show-overflow-tooltip />
                                                <el-table-column label="visualization" min-width="130" fixed="right">
                                                    <template #default="instanceScope">
                                                        <el-button v-if="instanceScope.row.visualization" type="success"
                                                            plain @click="handleVisualization(instanceScope.row)">
                                                            查看关系图
                                                        </el-button>
                                                    </template>
                                                </el-table-column>
                                            </el-table>
                                        </el-card>
                                    </div>
                                </template>
                            </el-table-column>

                            <!-- <el-table-column label="层级" min-width="110">
                                <template #default>
                                    <el-tag size="small" type="primary">
                                        subgraph
                                    </el-tag>
                                </template>
                            </el-table-column> -->

                            <el-table-column prop="subgraph_id" label="subgraph_id" min-width="110" />
                            <el-table-column prop="support" label="support" min-width="90" />
                            <el-table-column label="structure_analysis" min-width="320" show-overflow-tooltip>
                                <template #default="scope">
                                    <el-button type="success" plain class="analysis-link"
                                        @click="openAnalysisDialog(scope.row)">
                                        查看分析详情
                                    </el-button>
                                </template>
                            </el-table-column>

                            <el-table-column label="visualization" min-width="130" fixed="right">
                                <template #default="scope">
                                    <el-button v-if="scope.row.visualization" type="success" plain
                                        @click="handleVisualization(scope.row)">
                                        查看关系图
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-card>
                </el-col>

                <el-col :xs="24" :lg="11">
                    <el-card class="panel-card" shadow="hover">
                        <template #header>
                            <div class="card-header">{{ chartTitle }}</div>
                        </template>
                        <div ref="chartRef" class="graph-canvas"></div>
                    </el-card>
                </el-col>
            </el-row>

            <el-dialog v-model="analysisDialogVisible" :title="analysisDialogTitle" width="62%" class="analysis-dialog">
                <div class="markdown-content" v-html="analysisDialogHtml"></div>
            </el-dialog>
        </el-main>
    </el-container>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import processedData from './assets/graph_table_data.json'

const tableRows = processedData.table_rows || []
const subgraphRows = computed(() => tableRows.filter((row) => row.row_type === 'subgraph'))
const charts = processedData.charts || { subgraphs: {}, instances: {} }

const chartRef = ref(null)
const chartTitle = ref('点击表格中的 visualization 按钮查看关系图')
const analysisDialogVisible = ref(false)
const analysisDialogTitle = ref('structure_analysis')
const analysisDialogHtml = ref('')

let chartInstance = null

const palette = [
    // 1-5: 基础高辨识度色（深蓝、翠绿、亮橙、紫、红）
    '#2563eb', '#10b981', '#f59e0b', '#7c3aed', '#ef4444',

    // 6-10: 间色调（青、粉、酸橙、靛蓝、琥珀）
    '#06b6d4', '#ec4899', '#84cc16', '#6366f1', '#f97316',

    // 11-15: 柔和过渡色（天蓝、玫瑰、薄荷、紫罗兰、金黄）
    '#0ea5e9', '#f43f5e', '#34d399', '#a855f7', '#eab308',

    // 16-20: 深色系对比（海军蓝、森林绿、褐、浆果紫、深灰蓝）
    '#1e40af', '#065f46', '#9a3412', '#9d174d', '#334155',

    // 21-25: 浅色系点缀（湖蓝、珊瑚、草绿、薰衣草、沙褐）
    '#60a5fa', '#fb7185', '#4ade80', '#c084fc', '#d97706'
];

const hashString = (value) => {
    let hash = 0
    for (let index = 0; index < value.length; index += 1) {
        hash = (hash << 5) - hash + value.charCodeAt(index)
        hash |= 0
    }
    return Math.abs(hash)
}

const createTypeVisualMap = (categories) => {
    const map = new Map()
    const categoryNames = categories.map((item) => item.name)

    categoryNames.forEach((typeName, index) => {
        const hash = hashString(typeName)
        const color = palette[hash % palette.length]
        const size = 46 + ((hash + index) % 7) * 4
        map.set(typeName, {
            color,
            size
        })
    })

    return map
}

const ensureChart = () => {
    if (!chartRef.value) return
    if (!chartInstance) {
        chartInstance = echarts.init(chartRef.value)
    }
}

const buildOption = (payload) => {
    const categories = (payload.categories || []).map((name) => ({ name }))
    const typeVisualMap = createTypeVisualMap(categories)

    categories.forEach(category => {
        category.itemStyle = {
            color: typeVisualMap.get(category.name)?.color || '#334155'
        }
    })

    const data = (payload.nodes || []).map((node) => ({
        id: String(node.id),
        name: node.display_name,
        category: categories.findIndex((item) => item.name === node.type_name),
        symbolSize: typeVisualMap.get(node.type_name)?.size || 48,
        itemStyle: {
            color: typeVisualMap.get(node.type_name)?.color || '#334155'
        },
        value: node.tooltip || []
    }))

    const links = (payload.edges || []).map((edge) => ({
        source: String(edge.source),
        target: String(edge.target),
        value: edge.tooltip || [],
        lineStyle: {
            width: edge.relation === 'ser_invoke' ? 3 : 2,
            opacity: 0.86,
            curveness: 0.18
        },
        label: {
            show: true,
            formatter: edge.relation,
            color: '#475569',
            fontSize: 11
        }
    }))

    return {
        animationDuration: 600,
        tooltip: {
            confine: true,
            formatter(params) {
                const lines = Array.isArray(params.data?.value) ? params.data.value : []
                if (!lines.length) return params.name || ''
                return lines.join('<br/>')
            }
        },
        legend: [
            {
                type: 'scroll',
                orient: 'horizontal',
                top: 8,
                data: categories.map((item) => item.name)
            }
        ],
        series: [
            {
                type: 'graph',
                layout: 'force',
                roam: true,
                draggable: true,
                categories,
                data,
                links,
                edgeSymbol: ['none', 'arrow'],
                edgeSymbolSize: [4, 10],
                label: {
                    show: true,
                    position: 'top',
                    fontSize: 12,
                    color: '#0f172a'
                },
                force: {
                    repulsion: 280,
                    edgeLength: [90, 180],
                    gravity: 0.08
                }
            }
        ]
    }
}

const renderChartByVisualization = (visualization) => {
    if (!visualization) return

    let payload = null
    if (visualization.kind === 'subgraph') {
        payload = charts.subgraphs?.[visualization.key]
    }
    if (visualization.kind === 'instance') {
        payload = charts.instances?.[visualization.key]
    }
    if (!payload) return

    ensureChart()
    if (!chartInstance) return
    chartTitle.value = payload.title || '关系图'
    chartInstance.setOption(buildOption(payload), true)
}

const findFirstVisualization = (rows) => {
    for (const row of rows) {
        if (row.visualization) return row.visualization
        if (row.children?.length) {
            const found = findFirstVisualization(row.children)
            if (found) return found
        }
    }
    return null
}

const handleVisualization = (row) => {
    renderChartByVisualization(row.visualization)
}

const escapeHtml = (value) => {
    return value
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
}

const renderMarkdown = (markdownText) => {
    if (!markdownText) return '<p>暂无分析内容</p>'

    const escaped = escapeHtml(markdownText)
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/^###\s+(.+)$/gm, '<h3>$1</h3>')
        .replace(/^##\s+(.+)$/gm, '<h2>$1</h2>')
        .replace(/^#\s+(.+)$/gm, '<h1>$1</h1>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br/>')

    return `<p>${escaped}</p>`
}

const openAnalysisDialog = (row) => {
    analysisDialogTitle.value = `Subgraph ${row.subgraph_id} - structure_analysis`
    analysisDialogHtml.value = renderMarkdown(row.structure_analysis)
    analysisDialogVisible.value = true
}

const handleResize = () => {
    if (chartInstance) {
        chartInstance.resize()
    }
}

onMounted(async () => {
    await nextTick()
    ensureChart()
    const first = findFirstVisualization(subgraphRows.value)
    if (first) {
        renderChartByVisualization(first)
    }
    window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
    if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
    }
})
</script>

<style scoped>
.page {
    min-height: 100vh;
    background:
        radial-gradient(circle at 20% 10%, #dbeafe 0%, transparent 40%),
        radial-gradient(circle at 80% 0%, #fce7f3 0%, transparent 35%),
        linear-gradient(180deg, #eff6ff 0%, #f8fafc 100%);
}

.header {
    display: flex;
    align-items: center;
    height: 64px;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #0f172a;
}

.main {
    padding-top: 8px;
}

.layout-row {
    row-gap: 16px;
}

.panel-card {
    border-radius: 12px;
}

.card-header {
    font-weight: 700;
    color: #0f172a;
}

.expand-wrap {
    width: 92%;
    padding: 6px 0 2px;
    margin-left: auto;
    margin-right: auto;
}

.cluster-card+.cluster-card {
    margin-top: 12px;
}

.cluster-title {
    font-weight: 600;
    color: #334155;
}

.analysis-link {
    padding: 6px 10px;
}

.markdown-content {
    padding: 0 4px;
    max-height: 60vh;
    overflow-y: auto;
}

.markdown-content :deep(h1) {
    margin: 1.2rem 0 0.8rem;
    font-size: 1.8rem;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #e0e7ff;
    padding-bottom: 0.6rem;
}

.markdown-content :deep(h2) {
    margin: 1rem 0 0.6rem;
    font-size: 1.4rem;
    font-weight: 600;
    color: #1e293b;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.4rem;
}

.markdown-content :deep(h3) {
    margin: 0.8rem 0 0.4rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: #334155;
}

.markdown-content :deep(p) {
    margin: 0 0 1rem;
    line-height: 1.8;
    color: #475569;
    font-size: 14px;
}

.markdown-content :deep(strong) {
    color: #0f172a;
    font-weight: 600;
}

.markdown-content :deep(br) {
    display: block;
    content: '';
}

.analysis-dialog :deep(.el-dialog) {
    border-radius: 8px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.analysis-dialog :deep(.el-dialog__header) {
    background: linear-gradient(135deg, #f0f4ff 0%, #fff5f9 100%);
    border-bottom: 1px solid #e0e7ff;
    border-radius: 8px 8px 0 0;
    padding: 16px 20px;
}

.analysis-dialog :deep(.el-dialog__title) {
    font-size: 16px;
    font-weight: 600;
    color: #0f172a;
}

.analysis-dialog :deep(.el-dialog__body) {
    padding: 24px;
    background-color: #fafbfc;
}

.analysis-dialog :deep(.el-dialog__close) {
    color: #64748b;
    font-size: 20px;
}

.analysis-dialog :deep(.el-dialog__close:hover) {
    color: #0f172a;
}

.graph-canvas {
    width: 100%;
    height: 72vh;
    min-height: 460px;
}

@media (max-width: 992px) {
    .graph-canvas {
        height: 60vh;
        min-height: 380px;
    }
}
</style>
