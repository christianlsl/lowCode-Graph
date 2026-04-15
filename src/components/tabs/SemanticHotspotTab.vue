<template>
    <div class="semantic-hotspot-tab">
        <el-card class="panel-card" shadow="hover">
            <template #header>
                <div class="card-header with-filter">
                    <span>语义相似热点组件</span>
                    <div class="filter-actions">
                        <el-input v-model="searchKeyword" clearable placeholder="搜索 cluster_id/技术功能/业务领域"
                            class="search-input" />
                        <el-select v-model="selectedType" class="type-select" placeholder="选择组件类型">
                            <el-option label="全部组件类型" value="all" />
                            <el-option v-for="type in componentTypeOptions" :key="type" :label="type" :value="type" />
                        </el-select>
                    </div>
                </div>
            </template>

            <el-table :data="filteredRows" border row-key="cluster_id" max-height="50vh" highlight-current-row
                @current-change="handleCurrentChange">
                <el-table-column prop="cluster_id" label="cluster_id" min-width="110" sortable />
                <el-table-column prop="structure_name" label="技术功能" min-width="220" show-overflow-tooltip />
                <el-table-column prop="domain_name" label="业务领域" min-width="180" show-overflow-tooltip />
                <el-table-column prop="type" label="类型" min-width="120" />
                <el-table-column prop="structure_variant_count" label="结构变体总数" min-width="130" sortable />
                <el-table-column prop="reuse_count" label="复用次数" min-width="110" sortable />
                <el-table-column prop="covered_projects_count" label="覆盖工程数" min-width="120" sortable />
                <el-table-column label="明细" min-width="120" fixed="right">
                    <template #default="scope">
                        <el-button type="success" plain @click="openDetail(scope.row)">查看明细</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <el-card ref="chartCardRef" class="panel-card chart-card" shadow="hover">
            <template #header>
                <div class="card-header with-action">
                    <span>{{ chartTitle }}</span>
                    <div class="chart-actions">
                        <el-select v-model="selectedStructureClusterId" size="small" class="cluster-select"
                            :disabled="!structureClusterOptions.length" placeholder="选择结构簇">
                            <el-option v-for="item in structureClusterOptions" :key="item.value" :label="item.label"
                                :value="item.value" />
                        </el-select>
                        <el-radio-group v-model="graphMode" size="small">
                            <el-radio-button value="tree">树</el-radio-button>
                            <el-radio-button value="directed">有向图</el-radio-button>
                        </el-radio-group>
                    </div>
                </div>
            </template>

            <div v-if="!selectedPayload" class="chart-empty">请选择有可视化结构簇的联合簇查看关系图。</div>
            <div v-else-if="graphMode === 'tree'" class="tree-wrap">
                <el-tree :data="treeData" node-key="id" :props="treeProps" default-expand-all class="graph-tree" />
            </div>
            <div v-else ref="chartRef" class="graph-canvas"></div>
        </el-card>

        <section class="detail-section">
            <div class="section-title with-detail-search">
                <span>语义相似热点组件详情</span>
                <el-input v-model="detailSearchKeyword" clearable placeholder="搜索技术功能/业务领域/实例语义描述"
                    class="detail-search-input" />
            </div>

            <el-card v-for="row in detailFilteredRows" :key="row.cluster_id" class="panel-card detail-item-card"
                shadow="hover">
                <template #header>
                    <div class="card-header detail-header">
                        <span>{{ row.structure_name || '未命名技术功能' }}</span>
                        <el-tag type="info" effect="plain" round>cluster_id: {{ row.cluster_id }}</el-tag>
                    </div>
                </template>

                <el-descriptions :column="1" :border="false" class="detail-descriptions">
                    <el-descriptions-item label="业务领域">{{ row.domain_name || '-' }}</el-descriptions-item>
                    <el-descriptions-item label="类型">{{ row.type || '-' }}</el-descriptions-item>
                    <el-descriptions-item label="结构变体总数">{{ row.structure_variant_count ?? 0 }}</el-descriptions-item>
                    <el-descriptions-item label="复用次数">{{ row.reuse_count ?? 0 }}</el-descriptions-item>
                    <el-descriptions-item label="覆盖工程数">{{ row.covered_projects_count ?? 0 }}</el-descriptions-item>
                </el-descriptions>

                <div v-if="!(row.items_display || []).length" class="empty-items">暂无明细项。</div>

                <div v-for="item in row.items_display || []" :key="`${row.cluster_id}-${item.structure_cluster_id}`"
                    class="item-block">
                    <div class="item-header">
                        <span>结构簇 {{ item.structure_cluster_id }}</span>
                        <div class="item-tags">
                            <el-tag size="small" type="success" effect="light">{{ item.structure_name || '-' }}</el-tag>
                            <el-tag size="small" type="info" effect="plain">复用: {{ item.reuse_count ?? 0 }}</el-tag>
                            <el-tag size="small" type="warning" effect="plain">覆盖工程: {{ item.covered_projects_count ?? 0
                            }}</el-tag>
                        </div>
                    </div>

                    <div class="instance-title">实例列表</div>
                    <el-table :data="item.instances || []" border size="small" max-height="32vh">
                        <el-table-column prop="instance_id" label="id" min-width="60" />
                        <el-table-column label="page_path" min-width="260" show-overflow-tooltip>
                            <template #default="scope">
                                {{ formatPagePath(scope.row.page_path) }}
                            </template>
                        </el-table-column>
                        <el-table-column prop="instance_summary" label="语义描述" min-width="220" show-overflow-tooltip />
                        <el-table-column label="包含组件" min-width="90" align="center">
                            <template #default="scope">
                                <el-button type="primary" link
                                    @click="openComponentListDialog(scope.row)">查看</el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
            </el-card>
        </section>

        <el-dialog v-model="componentListDialogVisible" title="包含组件" width="50%">
            <el-table :data="selectedComponentList" border size="small" max-height="50vh">
                <el-table-column type="index" label="序号" width="60" align="center" />
                <el-table-column label="组件ID" prop="id" />
            </el-table>
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
const chartCardRef = ref(null)
const graphMode = ref('tree')
const selectedRow = ref(null)
const selectedStructureClusterId = ref(null)
const searchKeyword = ref('')
const selectedType = ref('all')
const detailSearchKeyword = ref('')
const componentListDialogVisible = ref(false)
const selectedComponentList = ref([])
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

const sortedRows = computed(() => {
    const list = Array.isArray(props.rows) ? [...props.rows] : []
    return list.sort((a, b) => {
        const domainCompare = String(a?.domain_name || '').localeCompare(String(b?.domain_name || ''), 'zh-Hans-CN')
        if (domainCompare !== 0) return domainCompare

        const reuseDiff = Number(b?.reuse_count || 0) - Number(a?.reuse_count || 0)
        if (reuseDiff !== 0) return reuseDiff

        const coveredDiff = Number(b?.covered_projects_count || 0) - Number(a?.covered_projects_count || 0)
        if (coveredDiff !== 0) return coveredDiff

        return Number(a?.cluster_id || 0) - Number(b?.cluster_id || 0)
    })
})

const filteredRows = computed(() => {
    const keyword = searchKeyword.value.trim().toLowerCase()
    return sortedRows.value.filter((row) => {
        const matchesType = selectedType.value === 'all' || row.type === selectedType.value
        if (!matchesType) return false

        if (!keyword) return true

        const clusterIdText = String(row.cluster_id || '').toLowerCase()
        const structureNameText = String(row.structure_name || '').toLowerCase()
        const domainNameText = String(row.domain_name || '').toLowerCase()
        const typeText = String(row.type || '').toLowerCase()
        return clusterIdText.includes(keyword)
            || structureNameText.includes(keyword)
            || domainNameText.includes(keyword)
            || typeText.includes(keyword)
    })
})

const structureClusterOptions = computed(() => {
    const row = selectedRow.value
    if (!row) return []

    const ids = Array.isArray(row.available_structure_cluster_ids) ? row.available_structure_cluster_ids : []
    const nameMap = new Map()
    for (const item of row.items_expanded || []) {
        nameMap.set(item.structure_cluster_id, item.structure_name || '')
    }

    return ids.map((id) => ({
        value: id,
        label: nameMap.get(id) ? `${id} - ${nameMap.get(id)}` : String(id),
    }))
})

const selectedPayload = computed(() => {
    const clusterId = selectedStructureClusterId.value
    if (clusterId === null || clusterId === undefined) return null
    return props.charts?.subgraphs?.[`structure:${clusterId}`] || null
})

const treeData = computed(() => selectedPayload.value?.tree || [])

const chartTitle = computed(() => {
    if (!selectedRow.value) {
        return '请选择联合簇查看关系图'
    }
    if (!selectedPayload.value) {
        return '当前联合簇无可用关系图'
    }
    return selectedPayload.value.title || '关系图'
})

const detailFilteredRows = computed(() => {
    const keyword = detailSearchKeyword.value.trim().toLowerCase()
    if (!keyword) {
        return filteredRows.value.map((row) => ({
            ...row,
            items_display: Array.isArray(row.items_expanded) ? row.items_expanded : [],
        }))
    }

    const result = []
    for (const row of filteredRows.value) {
        const rowMatches = String(row.structure_name || '').toLowerCase().includes(keyword)
            || String(row.domain_name || '').toLowerCase().includes(keyword)
            || String(row.type || '').toLowerCase().includes(keyword)
            || String(row.cluster_id || '').toLowerCase().includes(keyword)

        const items = Array.isArray(row.items_expanded) ? row.items_expanded : []
        const matchedItems = items
            .map((item) => {
                const instanceMatches = (item.instances || []).filter((instance) => {
                    const summary = String(instance?.instance_summary || '').toLowerCase()
                    const pagePath = formatPagePath(instance?.page_path).toLowerCase()
                    const instanceId = String(instance?.instance_id || '').toLowerCase()
                    return summary.includes(keyword) || pagePath.includes(keyword) || instanceId.includes(keyword)
                })

                const itemMatches = String(item.structure_name || '').toLowerCase().includes(keyword)
                    || String(item.structure_cluster_id || '').toLowerCase().includes(keyword)

                if (itemMatches && !instanceMatches.length) {
                    return {
                        ...item,
                        instances: item.instances || [],
                    }
                }

                if (instanceMatches.length) {
                    return {
                        ...item,
                        instances: instanceMatches,
                    }
                }

                return null
            })
            .filter(Boolean)

        if (rowMatches || matchedItems.length) {
            result.push({
                ...row,
                items_display: rowMatches && !matchedItems.length ? items : matchedItems,
            })
        }
    }

    return result
})

const ensureChart = () => {
    if (chartRef.value && !chartInstance) {
        chartInstance = echarts.init(chartRef.value)
    }
}

const renderGraph = async () => {
    if (graphMode.value !== 'directed') return
    if (!selectedPayload.value) return

    await nextTick()
    ensureChart()
    if (!chartInstance) return

    chartInstance.setOption(buildGraphOption(selectedPayload.value), true)
}

const selectRow = async (row, scrollToChart = false) => {
    if (!row) return
    selectedRow.value = row

    const availableIds = Array.isArray(row.available_structure_cluster_ids) ? row.available_structure_cluster_ids : []
    if (!availableIds.length) {
        selectedStructureClusterId.value = null
    } else if (!availableIds.includes(selectedStructureClusterId.value)) {
        selectedStructureClusterId.value = availableIds[0]
    }

    if (scrollToChart) {
        await nextTick()
        chartCardRef.value?.$el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }

    if (graphMode.value === 'directed' && props.isActive) {
        await renderGraph()
    }
}

const openDetail = async (row) => {
    await selectRow(row, true)
}

const handleCurrentChange = (row) => {
    if (row) {
        selectRow(row)
    }
}

const openComponentListDialog = (row) => {
    selectedComponentList.value = (row.component_id_list || []).map(id => ({ id }))
    componentListDialogVisible.value = true
}

const formatPagePath = (pagePath) => {
    if (Array.isArray(pagePath)) {
        return pagePath.join('; ')
    }
    if (typeof pagePath === 'string') {
        return pagePath
    }
    return '-'
}

watch(
    filteredRows,
    async () => {
        if (!filteredRows.value.length) {
            selectedRow.value = null
            selectedStructureClusterId.value = null
            return
        }

        const currentId = selectedRow.value?.cluster_id
        const matched = filteredRows.value.find((row) => row.cluster_id === currentId)
        await selectRow(matched || filteredRows.value[0])
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

watch(selectedStructureClusterId, async () => {
    if (graphMode.value === 'directed' && props.isActive) {
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
.semantic-hotspot-tab {
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

.chart-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.cluster-select {
    width: 260px;
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

.chart-empty {
    min-height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    border: 1px dashed #cbd5e1;
    border-radius: 10px;
    background: #f8fafc;
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

.detail-descriptions {
    margin-bottom: 8px;
}

.detail-descriptions :deep(.el-descriptions__label) {
    font-weight: 700;
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

.item-block {
    margin-top: 14px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px;
    background: #fcfdff;
}

.item-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 8px;
    color: #0f172a;
    font-weight: 600;
}

.item-tags {
    display: flex;
    align-items: center;
    gap: 8px;
}

.instance-title {
    margin: 8px 0;
    font-weight: 600;
    color: #334155;
}

.empty-items {
    color: #64748b;
}

.detail-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

@media (max-width: 992px) {
    .with-action {
        flex-direction: column;
        align-items: flex-start;
    }

    .chart-actions {
        width: 100%;
        flex-direction: column;
        align-items: stretch;
    }

    .cluster-select {
        width: 100%;
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

    .with-detail-search {
        flex-direction: column;
        align-items: flex-start;
    }

    .detail-search-input {
        width: 100%;
    }

    .detail-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .item-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .item-tags {
        flex-wrap: wrap;
    }
}
</style>
