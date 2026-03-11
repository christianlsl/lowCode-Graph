<template>
    <div class="structure-hotspot-tab">
        <el-card class="panel-card" shadow="hover">
            <template #header>
                <div class="card-header with-filter">
                    <span>结构相似热点组件</span>
                    <div class="filter-actions">
                        <el-input v-model="searchKeyword" clearable placeholder="搜索热点簇名称/结构cluster_id"
                            class="search-input" />
                        <el-select v-model="selectedType" class="type-select" placeholder="选择组件类型">
                            <el-option label="全部组件类型" value="all" />
                            <el-option v-for="type in componentTypeOptions" :key="type" :label="type" :value="type" />
                        </el-select>
                    </div>
                </div>
            </template>

            <el-table :data="filteredRows" border row-key="structure_cluster_id" max-height="46vh" highlight-current-row
                @current-change="handleCurrentChange">
                <el-table-column prop="type" label="组件类型" min-width="120" />
                <el-table-column prop="structure_cluster_id" label="结构cluster_id" min-width="130" />
                <el-table-column prop="name" label="热点簇名称" min-width="180" show-overflow-tooltip />
                <el-table-column prop="support" label="复用次数" min-width="100" />
                <el-table-column prop="size" label="组件大小" min-width="100" />
                <el-table-column prop="code_lines" label="复用代码量" min-width="110" />
                <el-table-column prop="relevent_projects_num" label="涉及工程个数" min-width="120" />
                <el-table-column label="关系图" min-width="120" fixed="right">
                    <template #default="scope">
                        <el-button type="success" plain @click="selectRow(scope.row)">查看关系图</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <el-card class="panel-card chart-card" shadow="hover">
            <template #header>
                <div class="card-header with-action">
                    <span>{{ chartTitle }}</span>
                    <el-radio-group v-model="graphMode" size="small">
                        <el-radio-button value="tree">树</el-radio-button>
                        <el-radio-button value="directed">有向图</el-radio-button>
                    </el-radio-group>
                </div>
            </template>

            <div v-if="graphMode === 'tree'" class="tree-wrap">
                <el-tree :data="treeData" node-key="id" :props="treeProps" default-expand-all class="graph-tree" />
            </div>
            <div v-else ref="chartRef" class="graph-canvas"></div>
            <!-- <div ref="chartRef" class="graph-canvas"></div> -->
        </el-card>

        <section class="detail-section">
            <div class="section-title with-detail-search">
                <span>结构相似热点组件详情</span>
                <el-input v-model="detailSearchKeyword" clearable placeholder="搜索语义描述关键词" class="detail-search-input" />
            </div>
            <el-card v-for="row in detailFilteredRows" :key="row.structure_cluster_id"
                class="panel-card detail-item-card" shadow="hover">
                <template #header>
                    <div class="card-header detail-header">
                        <span>{{ row.name || '未命名结构簇' }}</span>
                        <el-tag type="info" effect="plain" round>结构cluster_id: {{ row.structure_cluster_id }}</el-tag>
                    </div>
                </template>

                <el-descriptions :column="1" :border="false" class="detail-descriptions">
                    <el-descriptions-item label="组件类型">{{ row.type || '-' }}</el-descriptions-item>
                    <el-descriptions-item label="摘要">{{ row.summary || '-' }}</el-descriptions-item>
                    <el-descriptions-item label="关键差异点（语义）">{{ row.instance_defference || '-' }}</el-descriptions-item>
                </el-descriptions>

                <div class="instance-title">实例列表</div>
                <el-table :data="row.instances || []" border size="small" max-height="36vh">
                    <el-table-column prop="instance_id" label="id" min-width="80" />
                    <el-table-column prop="project_name" label="项目名" min-width="140" show-overflow-tooltip />
                    <el-table-column prop="module_name" label="模块名" min-width="140" show-overflow-tooltip />
                    <el-table-column prop="page_name" label="页面名" min-width="160" show-overflow-tooltip />
                    <el-table-column label="语义描述" min-width="120">
                        <template #default="scope">
                            <el-button type="primary" link @click="openSummaryDialog(scope.row)">查看</el-button>
                        </template>
                    </el-table-column>
                    <el-table-column label="包含组件" min-width="180" show-overflow-tooltip>
                        <template #default="scope">
                            {{ formatComponentList(scope.row.component_id_list) }}
                        </template>
                    </el-table-column>
                </el-table>
            </el-card>
        </section>

        <el-dialog v-model="summaryDialogVisible" title="语义描述" width="50%">
            <div class="dialog-content">{{ selectedSummary || '暂无语义描述' }}</div>
        </el-dialog>
    </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { buildGraphOption } from '../../utils/graphOption'

const props = defineProps({
    rows: {
        type: Array,
        default: () => []
    },
    charts: {
        type: Object,
        default: () => ({ subgraphs: {} })
    },
    isActive: {
        type: Boolean,
        default: false
    }
})

const chartRef = ref(null)
const graphMode = ref('tree')
const selectedRow = ref(null)
const searchKeyword = ref('')
const selectedType = ref('all')
const detailSearchKeyword = ref('')
const summaryDialogVisible = ref(false)
const selectedSummary = ref('')
const chartTitle = ref('请选择结构簇查看关系图')
const treeProps = { children: 'children', label: 'label' }
let chartInstance = null

const componentTypeOptions = computed(() => {
    const typeSet = new Set()
    for (const row of props.rows) {
        if (row?.type) {
            typeSet.add(row.type)
        }
    }
    return Array.from(typeSet)
})

const filteredRows = computed(() => {
    const keyword = searchKeyword.value.trim().toLowerCase()
    return props.rows.filter((row) => {
        const matchesType = selectedType.value === 'all' || row.type === selectedType.value
        if (!matchesType) return false

        if (!keyword) return true
        const nameText = String(row.name || '').toLowerCase()
        const clusterIdText = String(row.structure_cluster_id || '').toLowerCase()
        return nameText.includes(keyword) || clusterIdText.includes(keyword)
    })
})

const detailFilteredRows = computed(() => {
    const keyword = detailSearchKeyword.value.trim().toLowerCase()
    if (!keyword) return filteredRows.value

    return filteredRows.value
        .map((row) => {
            const instances = Array.isArray(row.instances)
                ? row.instances.filter((instance) =>
                    String(instance?.instance_summary || '').toLowerCase().includes(keyword)
                )
                : []
            return { ...row, instances }
        })
        .filter((row) => row.instances.length > 0)
})

const selectedVisualization = computed(() => selectedRow.value?.visualization || null)

const selectedPayload = computed(() => {
    const visualization = selectedVisualization.value
    if (!visualization || visualization.kind !== 'subgraph') return null
    return props.charts.subgraphs?.[visualization.key] || null
})

const treeData = computed(() => selectedPayload.value?.tree || [])

const ensureChart = () => {
    if (chartRef.value && !chartInstance) {
        chartInstance = echarts.init(chartRef.value)
    }
}

const renderGraph = async () => {

    if (graphMode.value !== 'directed') return
    const payload = selectedPayload.value
    if (!payload) return
    // console.log('Rendering graph with payload:', selectedPayload.value)
    await nextTick()
    ensureChart()
    if (!chartInstance) return

    chartTitle.value = payload.title || '关系图'
    chartInstance.setOption(buildGraphOption(payload), true)
}

const selectRow = (row) => {
    selectedRow.value = row
    const payload = selectedPayload.value
    chartTitle.value = payload?.title || '关系图'
    if (graphMode.value === 'directed') {
        renderGraph()
    }
}

const handleCurrentChange = (row) => {
    if (row) {
        selectRow(row)
    }
}

const openSummaryDialog = (instance) => {
    selectedSummary.value = instance.instance_summary || ''
    summaryDialogVisible.value = true
}

const formatComponentList = (componentList) => {
    if (!Array.isArray(componentList) || componentList.length === 0) return '-'
    return componentList.join(', ')
}

const initSelection = async () => {
    if (!filteredRows.value.length) {
        selectedRow.value = null
        chartTitle.value = '请选择结构簇查看关系图'
        return
    }

    const currentId = selectedRow.value?.structure_cluster_id
    const matched = filteredRows.value.find((row) => row.structure_cluster_id === currentId)
    selectedRow.value = matched || filteredRows.value[0]

    const payload = selectedPayload.value
    chartTitle.value = payload?.title || '关系图'

    if (graphMode.value === 'directed' && props.isActive) {
        await renderGraph()
    }
}

watch(
    filteredRows,
    async () => {
        await initSelection()
    },
    { immediate: true }
)

watch(graphMode, async (value) => {
    if (value !== 'directed') {
        if (chartInstance) {
            chartInstance.dispose()
            chartInstance = null
        }
        return
    }
    if (props.isActive) {
        await renderGraph()
    }
}, { flush: 'post' })

watch(
    () => props.isActive,
    async (value) => {
        if (value && graphMode.value === 'directed') {
            await renderGraph()
        }
    },
    { flush: 'post' }
)

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
.structure-hotspot-tab {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.panel-card {
    border-radius: 12px;
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

.with-filter {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.filter-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.search-input {
    width: 260px;
}

.type-select {
    width: 180px;
}

.tree-wrap {
    width: 100%;
    min-height: 280px;
    max-height: 58vh;
    overflow: auto;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px;
    background: #f8fbff;
}

.graph-tree {
    background: transparent;
}

.graph-canvas {
    width: 100%;
    height: 58vh;
    min-height: 360px;
}

.instance-title {
    margin: 12px 0 8px;
    font-weight: 600;
    color: #334155;
}

.detail-descriptions {
    margin-bottom: 8px;
}

.difference-box {
    margin-top: 10px;
}

.detail-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.section-title {
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
}

.with-detail-search {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.detail-search-input {
    width: 260px;
}

.detail-item-card {
    overflow: hidden;
}

.detail-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.dialog-content {
    white-space: pre-wrap;
    line-height: 1.7;
    color: #334155;
}

.detail-descriptions :deep(.el-descriptions__label) {
    font-weight: 700;
}

@media (max-width: 992px) {
    .with-action {
        flex-direction: column;
        align-items: flex-start;
    }

    .with-filter {
        flex-direction: column;
        align-items: flex-start;
    }

    .filter-actions {
        width: 100%;
        flex-direction: column;
        align-items: stretch;
    }

    .search-input,
    .type-select {
        width: 100%;
    }

    .detail-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .with-detail-search {
        flex-direction: column;
        align-items: flex-start;
    }

    .detail-search-input {
        width: 100%;
    }

    .graph-canvas {
        height: 52vh;
        min-height: 320px;
    }
}
</style>
