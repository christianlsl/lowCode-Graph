<template>
    <el-card class="panel-card" shadow="hover">
        <template #header>
            <div class="card-header with-action">
                <span>热点簇明细</span>
                <el-radio-group v-model="mode" size="small">
                    <el-radio-button label="structure">结构相似的热点簇</el-radio-button>
                    <el-radio-button label="semantic">语义相似的热点簇</el-radio-button>
                </el-radio-group>
            </div>
        </template>

        <el-table :data="rows" border row-key="subgraph_id" max-height="56vh">
            <el-table-column type="expand" width="56">
                <template #default="scope">
                    <div class="expand-wrap">
                        <el-descriptions :column="1" border>
                            <el-descriptions-item v-if="mode === 'structure'" label="摘要">
                                {{ scope.row.summary || '-' }}
                            </el-descriptions-item>
                            <el-descriptions-item v-else label="语义相似点">
                                {{ scope.row.semantic_same_points || '-' }}
                            </el-descriptions-item>
                        </el-descriptions>

                        <div class="instance-title">实例列表</div>
                        <el-table :data="scope.row.instances || []" border size="small">
                            <el-table-column prop="instance_id" label="id" min-width="80" />
                            <el-table-column prop="project_name" label="项目名" min-width="130" show-overflow-tooltip />
                            <el-table-column prop="module_name" label="模块名" min-width="130" show-overflow-tooltip />
                            <el-table-column prop="page_name" label="页面名" min-width="130" show-overflow-tooltip />
                            <el-table-column label="语义描述" min-width="120">
                                <template #default="instanceScope">
                                    <el-button type="primary" link
                                        @click="openDescriptionDialog(instanceScope.row)">查看详情</el-button>
                                </template>
                            </el-table-column>
                            <el-table-column label="关系图" min-width="120" fixed="right">
                                <template #default="instanceScope">
                                    <el-button type="success" plain
                                        @click="renderByRow(instanceScope.row)">查看关系图</el-button>
                                </template>
                            </el-table-column>
                        </el-table>

                        <el-descriptions :column="1" border class="difference-box">
                            <el-descriptions-item :label="mode === 'structure' ? '关键差异点（语义）' : '关键差异点（结构）'">
                                {{ scope.row.instance_defference || '-' }}
                            </el-descriptions-item>
                        </el-descriptions>
                    </div>
                </template>
            </el-table-column>

            <el-table-column prop="subgraph_id" label="cluster_id" min-width="120" />
            <el-table-column prop="name" label="热点簇名称" min-width="220" show-overflow-tooltip />
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

    <el-dialog v-model="descriptionDialogVisible" title="语义描述" width="50%" class="text-dialog">
        <div class="description-content">{{ selectedDescription || '暂无语义描述' }}</div>
    </el-dialog>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { buildGraphOption } from '../../utils/graphOption'

const props = defineProps({
    structureClusters: {
        type: Array,
        default: () => []
    },
    semanticClusters: {
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
const descriptionDialogVisible = ref(false)
const selectedDescription = ref('')
let chartInstance = null

const rows = computed(() => (mode.value === 'structure' ? props.structureClusters : props.semanticClusters))

const ensureChart = () => {
    if (chartRef.value && !chartInstance) {
        chartInstance = echarts.init(chartRef.value)
    }
}

const firstVisualizationFromRows = (list) => list.find((row) => row.visualization)?.visualization || null

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

const openDescriptionDialog = (instance) => {
    selectedDescription.value = instance.description || ''
    descriptionDialogVisible.value = true
}

const renderDefaultChart = async () => {
    const first = firstVisualizationFromRows(rows.value)
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

.expand-wrap {
    width: 94%;
    margin: 6px auto 4px;
}

.instance-title {
    margin: 14px 0 8px;
    font-weight: 600;
    color: #334155;
}

.difference-box {
    margin-top: 12px;
}

.graph-canvas {
    width: 100%;
    height: 66vh;
    min-height: 420px;
}

.description-content {
    white-space: pre-wrap;
    line-height: 1.8;
    color: #334155;
}

.text-dialog :deep(.el-dialog) {
    border-radius: 10px;
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
