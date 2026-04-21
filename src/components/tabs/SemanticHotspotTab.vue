<template>
    <div class="semantic-hotspot-tab">
        <el-card class="panel-card" shadow="hover">
            <template #header>
                <div class="card-header with-filter">
                    <span>语义相似热点组件</span>
                    <div class="filter-actions">
                        <el-input v-model="searchKeyword" clearable placeholder="搜索 cluster_id/技术功能/业务领域"
                            class="search-input" />
                        <el-select v-model="selectedStructureName" class="structure-select" placeholder="选择技术功能">
                            <el-option label="全部技术功能" value="all" />
                            <el-option v-for="name in structureNameOptions" :key="name" :label="name" :value="name" />
                        </el-select>
                        <el-select v-model="selectedDomainName" class="domain-select" placeholder="选择业务领域">
                            <el-option label="全部业务领域" value="all" />
                            <el-option v-for="name in domainNameOptions" :key="name" :label="name" :value="name" />
                        </el-select>
                        <el-select v-model="selectedType" class="type-select" placeholder="选择组件类型">
                            <el-option label="全部组件类型" value="all" />
                            <el-option v-for="type in componentTypeOptions" :key="type" :label="type" :value="type" />
                        </el-select>
                    </div>
                </div>
            </template>

            <el-table :data="paginatedTreeRows" border row-key="row_id" max-height="50vh" highlight-current-row
                :tree-props="{ children: 'children' }" :row-class-name="tableRowClassName"
                @current-change="handleCurrentChange" @sort-change="handleSortChange">
                <el-table-column label="cluster_id" min-width="110">
                    <template #default="scope">
                        {{ scope.row._isParent ? scope.row.cluster_id : scope.row.structure_cluster_id }}
                    </template>
                </el-table-column>
                <el-table-column prop="domain_name" label="业务领域" min-width="180" show-overflow-tooltip />
                <el-table-column prop="structure_name" label="技术功能" min-width="220" show-overflow-tooltip />
                <el-table-column label="类型" min-width="120">
                    <template #default="scope">
                        {{ getDisplayType(scope.row) }}
                    </template>
                </el-table-column>
                <el-table-column label="结构变体总数" prop="structure_variant_count" min-width="130" sortable="custom">
                    <template #default="scope">
                        {{ formatDisplayValue(scope.row._isParent ? scope.row.structure_variant_count : '-') }}
                    </template>
                </el-table-column>
                <el-table-column label="复用次数" prop="reuse_count" min-width="110" sortable="custom">
                    <template #default="scope">
                        {{ formatDisplayValue(scope.row.reuse_count) }}
                    </template>
                </el-table-column>
                <el-table-column label="覆盖工程数" prop="covered_projects_count" min-width="120" sortable="custom">
                    <template #default="scope">
                        {{ formatDisplayValue(scope.row.covered_projects_count) }}
                    </template>
                </el-table-column>
                <el-table-column label="明细" min-width="220" fixed="right">
                    <template #default="scope">
                        <div v-if="!scope.row._isParent" class="action-buttons-group">
                            <el-button type="success" plain @click="selectRow(scope.row, true)">查看关系图</el-button>
                            <el-button type="success" plain @click="openDetailForRow(scope.row)">查看明细</el-button>
                        </div>
                        <span v-else>-</span>
                    </template>
                </el-table-column>
            </el-table>

            <div class="table-pagination">
                <el-pagination v-model:current-page="tableCurrentPage" v-model:page-size="tablePageSize"
                    :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" :total="treeRows.length" />
            </div>
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

            <el-card v-for="row in detailFilteredRows" :key="row.row_id" :ref="(el) => setDetailCardRef(row.row_id, el)"
                class="panel-card detail-item-card" shadow="hover">
                <template #header>
                    <div class="card-header detail-header">
                        <span>{{ row.structure_name || '未命名技术功能' }}</span>
                        <el-tag type="info" effect="plain" round>cluster_id: {{ row.cluster_id }}</el-tag>
                    </div>
                </template>

                <el-descriptions :column="1" :border="false" class="detail-descriptions">
                    <el-descriptions-item label="业务领域">{{ row.domain_name || '-' }}</el-descriptions-item>
                    <el-descriptions-item label="类型">{{ getDisplayType(row) }}</el-descriptions-item>
                    <!-- <el-descriptions-item label="结构变体总数">{{ row.structure_variant_count ?? 0 }}</el-descriptions-item>
                    <el-descriptions-item label="复用次数">{{ row.reuse_count ?? 0 }}</el-descriptions-item>
                    <el-descriptions-item label="覆盖工程数">{{ row.covered_projects_count ?? 0 }}</el-descriptions-item> -->
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
const selectedStructureName = ref('all')
const selectedDomainName = ref('all')
const selectedType = ref('all')
const detailSearchKeyword = ref('')
const activeDetailRowId = ref('')
const tableCurrentPage = ref(1)
const tablePageSize = ref(10)
const sortState = ref({
    prop: '',
    order: null
})
const componentListDialogVisible = ref(false)
const selectedComponentList = ref([])
const treeProps = { children: 'children', label: 'label' }
const detailCardRefs = new Map()
let chartInstance = null

const normalizedRows = computed(() => {
    return (Array.isArray(props.rows) ? props.rows : []).map((parentRow, parentIndex) => {
        const parentKey = parentRow?.cluster_id ?? parentIndex
        const availableIds = Array.isArray(parentRow?.available_structure_cluster_ids)
            ? parentRow.available_structure_cluster_ids
            : []

        return {
            ...parentRow,
            row_id: `semantic-parent-${parentKey}`,
            _isParent: true,
            _source: 'semantic',
            children: (Array.isArray(parentRow?.items_expanded) ? parentRow.items_expanded : []).map((child, childIndex) => ({
                ...child,
                row_id: `semantic-child-${parentKey}-${child?.structure_cluster_id ?? childIndex}`,
                _isParent: false,
                _source: 'semantic',
                cluster_id: parentRow?.cluster_id,
                domain_name: parentRow?.domain_name,
                available_structure_cluster_ids: availableIds.length
                    ? availableIds
                    : (child?.structure_cluster_id === null || child?.structure_cluster_id === undefined
                        ? []
                        : [child.structure_cluster_id]),
            }))
        }
    })
})

const componentTypeOptions = computed(() => {
    const typeSet = new Set()
    for (const row of normalizedRows.value) {
        for (const child of row.children || []) {
            const displayType = getDisplayType(child)
            if (displayType && displayType !== '-') {
                typeSet.add(displayType)
            }
        }
    }
    return Array.from(typeSet)
})

const getDisplayType = (row) => {
    if (!row) return '-'
    return row.show_type || row.type || '-'
}

const structureNameOptions = computed(() => {
    const nameSet = new Set()
    for (const row of normalizedRows.value) {
        for (const child of row.children || []) {
            if (child?.structure_name) {
                nameSet.add(child.structure_name)
            }
        }
    }
    return Array.from(nameSet).sort((a, b) => String(a).localeCompare(String(b), 'zh-Hans-CN'))
})

const domainNameOptions = computed(() => {
    const nameSet = new Set()
    for (const row of normalizedRows.value) {
        if (row?.domain_name) {
            nameSet.add(row.domain_name)
        }
    }
    return Array.from(nameSet).sort((a, b) => String(a).localeCompare(String(b), 'zh-Hans-CN'))
})

const treeRows = computed(() => {
    const keyword = searchKeyword.value.trim().toLowerCase()
    const rows = normalizedRows.value
        .map((parentRow) => {
            const matchesDomainName = selectedDomainName.value === 'all' || parentRow.domain_name === selectedDomainName.value
            if (!matchesDomainName) return null

            const parentClusterText = String(parentRow.cluster_id || '').toLowerCase()
            const parentStructureNameText = String(parentRow.structure_name || '').toLowerCase()
            const parentDomainText = String(parentRow.domain_name || '').toLowerCase()
            const parentTypeText = String(getDisplayType(parentRow) || '').toLowerCase()
            const parentMatchesKeyword = !!keyword
                && (parentClusterText.includes(keyword)
                    || parentStructureNameText.includes(keyword)
                    || parentDomainText.includes(keyword)
                    || parentTypeText.includes(keyword))

            const filteredChildren = (parentRow.children || []).filter((child) => {
                const matchesType = selectedType.value === 'all' || getDisplayType(child) === selectedType.value
                const matchesStructureName = selectedStructureName.value === 'all' || child.structure_name === selectedStructureName.value
                if (!matchesType || !matchesStructureName) return false

                if (!keyword || parentMatchesKeyword) return true

                const childClusterText = String(child.structure_cluster_id || '').toLowerCase()
                const childStructureNameText = String(child.structure_name || '').toLowerCase()
                const childTypeText = String(getDisplayType(child) || '').toLowerCase()
                return childClusterText.includes(keyword)
                    || childStructureNameText.includes(keyword)
                    || childTypeText.includes(keyword)
            })

            if (!filteredChildren.length) return null

            return {
                ...parentRow,
                children: filteredChildren,
            }
        })
        .filter(Boolean)

    const defaultSortedRows = [...rows].sort((a, b) => {
        const domainCompare = String(a?.domain_name || '').localeCompare(String(b?.domain_name || ''), 'zh-Hans-CN')
        if (domainCompare !== 0) return domainCompare

        const reuseDiff = Number(b?.reuse_count || 0) - Number(a?.reuse_count || 0)
        if (reuseDiff !== 0) return reuseDiff

        const coveredDiff = Number(b?.covered_projects_count || 0) - Number(a?.covered_projects_count || 0)
        if (coveredDiff !== 0) return coveredDiff

        return Number(a?.cluster_id || 0) - Number(b?.cluster_id || 0)
    })

    if (!sortState.value.prop || !sortState.value.order) {
        return defaultSortedRows
    }

    return [...defaultSortedRows].sort((a, b) => compareParentRows(a, b, sortState.value.prop, sortState.value.order))
})

const paginatedTreeRows = computed(() => {
    const start = (tableCurrentPage.value - 1) * tablePageSize.value
    const end = start + tablePageSize.value
    return treeRows.value.slice(start, end)
})

const flattenedChildRows = computed(() => {
    const rows = []
    for (const parentRow of treeRows.value) {
        for (const child of parentRow.children || []) {
            rows.push(child)
        }
    }
    return rows
})

const structureClusterOptions = computed(() => {
    const row = selectedRow.value
    if (!row) return []

    const ids = Array.isArray(row.available_structure_cluster_ids) ? row.available_structure_cluster_ids : []
    const nameMap = new Map([[row.structure_cluster_id, row.structure_name || '']])

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
        return '请选择结构簇查看关系图'
    }
    if (!selectedPayload.value) {
        return '当前结构簇无可用关系图'
    }
    return selectedPayload.value.title || '关系图'
})

const selectedDetailRow = computed(() => {
    if (!activeDetailRowId.value) return null
    return flattenedChildRows.value.find((row) => row.row_id === activeDetailRowId.value) || null
})

const detailFilteredRows = computed(() => {
    const targetRow = selectedDetailRow.value
    if (!targetRow) return []

    const keyword = detailSearchKeyword.value.trim().toLowerCase()

    const allInstances = Array.isArray(targetRow.instances) ? targetRow.instances : []
    const instanceMatches = allInstances.filter((instance) => {
        const summary = String(instance?.instance_summary || '').toLowerCase()
        const pagePath = formatPagePath(instance?.page_path).toLowerCase()
        const instanceId = String(instance?.instance_id || '').toLowerCase()
        return summary.includes(keyword) || pagePath.includes(keyword) || instanceId.includes(keyword)
    })

    const rowMatches = String(targetRow.structure_name || '').toLowerCase().includes(keyword)
        || String(targetRow.domain_name || '').toLowerCase().includes(keyword)
        || String(getDisplayType(targetRow) || '').toLowerCase().includes(keyword)
        || String(targetRow.cluster_id || '').toLowerCase().includes(keyword)
        || String(targetRow.structure_cluster_id || '').toLowerCase().includes(keyword)

    if (keyword && !rowMatches && !instanceMatches.length) {
        return []
    }

    return [{
        row_id: targetRow.row_id,
        cluster_id: targetRow.cluster_id,
        domain_name: targetRow.domain_name,
        type: targetRow.type,
        show_type: targetRow.show_type,
        structure_name: targetRow.structure_name,
        items_display: [{
            structure_cluster_id: targetRow.structure_cluster_id,
            structure_name: targetRow.structure_name,
            reuse_count: targetRow.reuse_count,
            covered_projects_count: targetRow.covered_projects_count,
            instances: rowMatches || !keyword ? allInstances : instanceMatches,
        }],
    }]
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
    if (!row || row._isParent) return
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

const openDetailForRow = async (row) => {
    if (!row || row._isParent) return

    activeDetailRowId.value = row.row_id
    await selectRow(row)
    await nextTick()
    const targetDetailCard = detailCardRefs.get(row.row_id)
    if (targetDetailCard) {
        targetDetailCard.scrollIntoView({ behavior: 'smooth', block: 'start' })
        return
    }
    document.querySelector('.detail-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const handleCurrentChange = (row) => {
    if (row && !row._isParent) {
        selectRow(row)
    }
}

const tableRowClassName = ({ row }) => {
    if (row?._isParent) {
        return 'semantic-parent-row'
    }
    return ''
}

const setDetailCardRef = (rowId, element) => {
    if (element) {
        detailCardRefs.set(rowId, element.$el || element)
    } else {
        detailCardRefs.delete(rowId)
    }
}

const toSortableNumber = (value) => {
    if (value === null || value === undefined || value === '' || value === 'none') return null
    const numeric = Number(value)
    return Number.isFinite(numeric) ? numeric : null
}

const getNumericValuesFromChildren = (children, key) => {
    if (!Array.isArray(children) || !children.length) return []
    return children
        .map((child) => toSortableNumber(child?.[key]))
        .filter((value) => value !== null)
}

const getParentSortValue = (row, prop) => {
    if (!row || row._isParent === false) return null

    const parentValue = toSortableNumber(row[prop])
    if (parentValue !== null) {
        return parentValue
    }

    const childValues = getNumericValuesFromChildren(row.children, prop)
    if (!childValues.length) return null

    if (prop === 'structure_variant_count') {
        return Math.max(...childValues)
    }

    return childValues.reduce((sum, current) => sum + current, 0)
}

const compareParentRows = (a, b, prop, order) => {
    const aValue = getParentSortValue(a, prop)
    const bValue = getParentSortValue(b, prop)
    const aMissing = aValue === null
    const bMissing = bValue === null

    if (aMissing && bMissing) return 0
    if (aMissing) return 1
    if (bMissing) return -1

    return order === 'ascending' ? aValue - bValue : bValue - aValue
}

const handleSortChange = ({ prop, order }) => {
    sortState.value = {
        prop: prop || '',
        order: order || null,
    }
    tableCurrentPage.value = 1
}

const formatDisplayValue = (value) => {
    if (value === null || value === undefined || value === '' || value === 'none') {
        return '-'
    }
    return value
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
    flattenedChildRows,
    async () => {
        if (!flattenedChildRows.value.length) {
            selectedRow.value = null
            selectedStructureClusterId.value = null
            activeDetailRowId.value = ''
            return
        }

        const currentId = selectedRow.value?.row_id
        const matched = flattenedChildRows.value.find((row) => row.row_id === currentId)
        await selectRow(matched || flattenedChildRows.value[0])

        if (activeDetailRowId.value) {
            const detailMatched = flattenedChildRows.value.some((row) => row.row_id === activeDetailRowId.value)
            if (!detailMatched) {
                detailCardRefs.delete(activeDetailRowId.value)
                activeDetailRowId.value = ''
            }
        }
    },
    { immediate: true }
)

watch([searchKeyword, selectedStructureName, selectedDomainName, selectedType], () => {
    tableCurrentPage.value = 1
})

watch([treeRows, tablePageSize], () => {
    const maxPage = Math.max(1, Math.ceil(treeRows.value.length / tablePageSize.value))
    if (tableCurrentPage.value > maxPage) {
        tableCurrentPage.value = maxPage
    }
})

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

.table-pagination {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
}

.action-buttons-group {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.search-input {
    width: 260px;
}

.type-select {
    width: 180px;
}

.structure-select,
.domain-select {
    width: 220px;
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

:deep(.semantic-parent-row) {
    background-color: #f0f9ff !important;
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
    .structure-select,
    .domain-select,
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
