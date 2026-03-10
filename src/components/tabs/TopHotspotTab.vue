<template>
    <el-card class="panel-card" shadow="hover">
        <template #header>
            <div class="card-header with-action">
                <span>热点簇列表</span>
                <el-radio-group v-model="mode" size="small">
                    <el-radio-button label="structure">结构相似</el-radio-button>
                    <el-radio-button label="semantic">语义相似</el-radio-button>
                </el-radio-group>
            </div>
        </template>

        <el-table v-if="mode === 'structure'" :data="structureRows" border max-height="52vh">
            <el-table-column prop="type" label="组件类型" min-width="120" />
            <el-table-column prop="subgraph_id" label="结构cluster_id" min-width="120" />
            <el-table-column prop="name" label="热点簇名称" min-width="180" show-overflow-tooltip />
            <el-table-column prop="support" label="复用次数" min-width="100" />
            <el-table-column prop="size" label="组件大小" min-width="100" />
            <el-table-column prop="code_lines" label="复用代码量" min-width="110" />
            <el-table-column prop="relevent_projects_num" label="涉及工程个数" min-width="120" />
            <el-table-column label="关系图" min-width="120" fixed="right">
                <template #default="scope">
                    <el-button type="success" plain @click="renderByRow(scope.row)">查看关系图</el-button>
                </template>
            </el-table-column>
        </el-table>

        <el-table v-else :data="semanticRows" border max-height="52vh">
            <el-table-column prop="type" label="组件类型" min-width="120" />
            <el-table-column prop="subgraph_id" label="语义cluster_id" min-width="120" />
            <el-table-column prop="name" label="语义簇名称" min-width="180" show-overflow-tooltip />
            <el-table-column prop="struc_cluster_num" label="包含的结构cluster_id个数" min-width="180" />
            <el-table-column prop="support" label="复用次数" min-width="100" />
            <el-table-column prop="relevent_projects_num" label="涉及工程个数" min-width="120" />
            <el-table-column label="关系图" min-width="120" fixed="right">
                <template #default="scope">
                    <el-button type="success" plain @click="renderByRow(scope.row)">查看关系图</el-button>
                </template>
            </el-table-column>
        </el-table>
    </el-card>

    <el-card class="panel-card chart-card" shadow="hover">
        <template #header>
            <div class="card-header">{{ chartTitle }}</div>
        </template>
        <div ref="chartRef" class="graph-canvas"></div>
    </el-card>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { buildGraphOption } from '../../utils/graphOption'

const props = defineProps({
    structureRows: {
        type: Array,
        default: () => []
    },
    semanticRows: {
        type: Array,
        default: () => []
    },
    charts: {
        type: Object,
        default: () => ({ subgraphs: {}, instances: {} })
    },
    isActive: {
        type: Boolean,
        default: false
    }
})

const mode = ref('structure')
const chartRef = ref(null)
const chartTitle = ref('点击表格中的关系图按钮查看关系图')
let chartInstance = null

const ensureChart = () => {
    if (chartRef.value && !chartInstance) {
        chartInstance = echarts.init(chartRef.value)
    }
}

const firstVisualizationFromRows = (rows) => rows.find((row) => row.visualization)?.visualization || null

const getPayloadByVisualization = (visualization) => {
    if (!visualization) return null
    if (visualization.kind === 'subgraph') {
        return props.charts.subgraphs?.[visualization.key] || null
    }
    if (visualization.kind === 'instance') {
        return props.charts.instances?.[visualization.key] || null
    }
    return null
}

const renderByVisualization = async (visualization) => {
    const payload = getPayloadByVisualization(visualization)
    if (!payload) return

    await nextTick()
    ensureChart()
    if (!chartInstance) return

    chartTitle.value = payload.title || '关系图'
    chartInstance.setOption(buildGraphOption(payload), true)
}

const renderByRow = (row) => {
    renderByVisualization(row.visualization)
}

const renderDefaultChart = async () => {
    const rows = mode.value === 'structure' ? props.structureRows : props.semanticRows
    const first = firstVisualizationFromRows(rows)
    if (first) {
        await renderByVisualization(first)
    }
}

watch(mode, async () => {
    if (props.isActive) {
        await renderDefaultChart()
    }
})

watch(() => props.isActive, async (value) => {
    if (value) {
        await renderDefaultChart()
    }
})

const handleResize = () => {
    if (chartInstance) {
        chartInstance.resize()
    }
}

onMounted(() => {
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
.panel-card {
    border-radius: 12px;
}

.chart-card {
    margin-top: 16px;
}

.card-header {
    font-weight: 700;
    color: #0f172a;
}

.with-action {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.graph-canvas {
    width: 100%;
    height: 66vh;
    min-height: 420px;
}

@media (max-width: 992px) {
    .graph-canvas {
        height: 52vh;
        min-height: 340px;
    }

    .with-action {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>
