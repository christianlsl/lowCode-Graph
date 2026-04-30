<template>
    <div class="structure-hotspot-tab">
        <el-card class="panel-card" shadow="hover">
            <template #header>
                <div class="card-header with-filter">
                    <span>结构相似热点组件</span>
                    <div class="filter-actions">
                        <el-input v-model="searchKeyword" clearable placeholder="搜索热点簇名称/结构cluster_id/脚本函数组"
                            class="search-input" />
                        <el-select v-model="selectedType" class="type-select" placeholder="选择组件类型">
                            <el-option label="全部组件类型" value="all" />
                            <el-option v-for="type in componentTypeOptions" :key="type" :label="type" :value="type" />
                        </el-select>
                    </div>
                </div>
            </template>

            <el-table :data="paginatedTreeRows" border row-key="row_id" max-height="46vh" highlight-current-row
                :tree-props="{ children: 'children' }" @current-change="handleCurrentChange"
                :row-class-name="tableRowClassName" @sort-change="handleSortChange">
                <el-table-column label="簇类型" min-width="120">
                    <template #default="scope">
                        {{ getRowType(scope.row) }}
                    </template>
                </el-table-column>
                <el-table-column label="结构cluster_id" min-width="130">
                    <template #default="scope">
                        {{ scope.row._isParent ? scope.row.parent_cluster_id : scope.row.structure_cluster_id }}
                    </template>
                </el-table-column>
                <el-table-column label="热点簇名称" min-width="300" show-overflow-tooltip>
                    <template #default="scope">
                        {{ scope.row.name || '-' }}
                    </template>
                </el-table-column>
                <el-table-column label="组件大小" prop="size" min-width="100" sortable="custom">
                    <template #default="scope">
                        {{ formatDisplayValue(scope.row._isParent ? getRange(scope.row.children, 'size') :
                            scope.row.size) }}
                    </template>
                </el-table-column>
                <el-table-column label="复用次数" prop="support" min-width="110" sortable="custom">
                    <template #default="scope">
                        {{ formatDisplayValue(scope.row.support) }}
                    </template>
                </el-table-column>
                <el-table-column label="涉及工程个数" prop="relevent_projects_num" min-width="120" sortable="custom">
                    <template #default="scope">
                        {{ formatDisplayValue(scope.row.relevent_projects_num) }}
                    </template>
                </el-table-column>
                <el-table-column label="详情" min-width="220" fixed="right">
                    <template #default="scope">
                        <div v-if="scope.row._source === 'structure' && !scope.row._isParent"
                            class="action-buttons-group">
                            <el-button type="success" plain @click="selectStructureRow(scope.row)">
                                查看关系图
                            </el-button>
                            <el-button type="success" plain @click="openStructureChildDetail(scope.row)">
                                查看详情
                            </el-button>
                        </div>
                        <el-button v-else-if="getActionLabel(scope.row)"
                            :type="scope.row._source === 'clone' ? 'warning' : 'success'" plain
                            @click="handleDetailAction(scope.row)">
                            {{ getActionLabel(scope.row) }}
                        </el-button>
                        <span v-else>-</span>
                    </template>
                </el-table-column>
            </el-table>

            <div class="table-pagination">
                <el-pagination v-model:current-page="tableCurrentPage" v-model:page-size="tablePageSize"
                    :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" :total="treeRows.length" />
            </div>
        </el-card>

        <el-card class="panel-card chart-card" shadow="hover">
            <template #header>
                <div class="card-header with-action">
                    <span>{{ panelTitle }}</span>
                    <el-radio-group v-if="panelMode === 'graph'" v-model="graphMode" size="small">
                        <el-radio-button value="tree">树</el-radio-button>
                        <el-radio-button value="directed">有向图</el-radio-button>
                    </el-radio-group>
                </div>
            </template>

            <template v-if="panelMode === 'diff'">
                <div v-if="activeCloneGroup" class="diff-panel">
                    <div class="diff-selector-grid">
                        <div class="diff-selector-column">
                            <div class="selector-label">左侧函数组</div>
                            <div class="selector-list">
                                <el-button v-for="(group, index) in activeCloneGroup.type1_group"
                                    :key="`left-${group.detail_key}`"
                                    :type="leftDiffIndex === index ? 'primary' : 'default'" size="small"
                                    @click="leftDiffIndex = index">
                                    {{ group.group_name || `函数组 ${index + 1}` }}
                                </el-button>
                            </div>
                            <div class="selector-code-meta">
                                {{ getDiffGroupMeta(leftDiffGroup) }}
                            </div>
                        </div>
                        <div class="diff-selector-column">
                            <div class="selector-label">右侧函数组</div>
                            <div class="selector-list">
                                <el-button v-for="(group, index) in activeCloneGroup.type1_group"
                                    :key="`right-${group.detail_key}`"
                                    :type="rightDiffIndex === index ? 'primary' : 'default'" size="small"
                                    @click="rightDiffIndex = index">
                                    {{ group.group_name || `函数组 ${index + 1}` }}
                                </el-button>
                            </div>
                            <div class="selector-code-meta">
                                {{ getDiffGroupMeta(rightDiffGroup) }}
                            </div>
                        </div>
                    </div>

                    <div class="diff-view-wrap">
                        <CodeDiff :old-string="leftDiffCode" :new-string="rightDiffCode" language="javascript"
                            :context="20" output-format="side-by-side" diff-style="word" :hide-header="true"
                            :hide-stat="true" max-height="72vh" :filename="diffFileName" />
                    </div>
                </div>
                <el-empty v-else description="请选择脚本函数组查看代码差异" />
            </template>

            <template v-else>
                <div v-if="graphMode === 'tree'" class="tree-wrap">
                    <el-tree :data="treeData" node-key="id" :props="treeProps" default-expand-all class="graph-tree" />
                </div>
                <div v-else ref="chartRef" class="graph-canvas"></div>
            </template>
        </el-card>

        <section class="detail-section">
            <div class="section-title with-detail-search">
                <span>结构相似热点组件详情</span>
                <el-input v-model="detailSearchKeyword" clearable placeholder="搜索脚本函数组说明或结构实例语义"
                    class="detail-search-input" />
            </div>

            <el-empty v-if="!hasActiveDetailSelection" description="请在上方表格中点击查看详情" />

            <el-card v-for="group in detailFilteredCloneGroups" :key="group.group_key"
                :ref="(el) => setCloneDetailRef(group.group_key, el)"
                class="panel-card detail-item-card clone-detail-card" shadow="hover"
                :class="{ 'is-active-card': activeDetailGroupKey === group.group_key }">
                <template #header>
                    <div class="card-header detail-header">
                        <span>{{ group.summary.group_name || '未命名函数组' }}</span>
                        <el-tag type="warning" effect="plain" round>
                            结构cluster_id: {{ group.parent_cluster_id }}
                        </el-tag>
                    </div>
                </template>

                <el-descriptions :column="1" border class="detail-descriptions">
                    <el-descriptions-item label="函数组名称">
                        <div class="markdown-content" v-html="renderMarkdown(group.summary.group_name)"></div>
                    </el-descriptions-item>
                    <el-descriptions-item label="整体功能">
                        <div class="markdown-content" v-html="renderMarkdown(group.summary.overall_functionality)">
                        </div>
                    </el-descriptions-item>
                    <el-descriptions-item label="Type-1组差异">
                        <div class="markdown-content"
                            v-html="group.type1_group?.length === 1 ? '-' : renderMarkdown(group.summary.type1_group_differences)">
                        </div>
                    </el-descriptions-item>
                    <el-descriptions-item label="复用机会">
                        <div class="markdown-content" v-html="renderMarkdown(group.summary.reuse_opportunities)"></div>
                    </el-descriptions-item>
                    <el-descriptions-item label="涉及工程">
                        <div class="tag-list">
                            <el-tag v-for="project in group.relevent_projects" :key="project" size="small"
                                effect="plain">
                                {{ project }}
                            </el-tag>
                            <span v-if="!group.relevent_projects.length">-</span>
                        </div>
                    </el-descriptions-item>
                    <el-descriptions-item label="相似度范围">
                        {{ formatSimilarityRange(group.similarity_range) }}
                    </el-descriptions-item>
                </el-descriptions>

                <div class="subsection-title">完全一致函数组（Type-1）</div>
                <div class="function-list">
                    <el-card v-for="typeGroup in group.type1_group" :key="typeGroup.detail_key" class="function-card"
                        shadow="never">
                        <template #header>
                            <div class="function-header">
                                <div class="function-header-text">
                                    <div class="function-group-title markdown-content"
                                        v-html="renderMarkdown(typeGroup.group_name)"></div>
                                    <div class="function-group-desc markdown-content"
                                        v-html="renderMarkdown(typeGroup.functionality)"></div>
                                </div>
                                <el-button type="primary" link @click="toggleCloneTypeGroup(typeGroup.detail_key)">
                                    {{ isCloneTypeGroupExpanded(typeGroup.detail_key) ? '收起代码' : '展开代码' }}
                                </el-button>
                            </div>
                        </template>

                        <div v-if="isCloneTypeGroupExpanded(typeGroup.detail_key)" class="type-group-code-block">
                            <pre class="code-block"><code class="hljs language-javascript"
                            v-html="highlightJsCode(getTypeGroupCode(typeGroup))"></code></pre>
                            <div class="subsection-title file-path-title">包含此函数的所有文件路径</div>
                            <el-table :data="getTypeGroupFileRows(typeGroup)" border size="small"
                                class="file-path-table">
                                <el-table-column label="文件路径" prop="file_path" min-width="260" show-overflow-tooltip />
                                <el-table-column label="行号范围" prop="line_range" min-width="120" />
                            </el-table>
                        </div>

                        <!-- <div v-for="(func, index) in getVisibleTypeGroupFunctions(typeGroup)"
                            :key="`${typeGroup.detail_key}-${index}-${func.file_path || 'code'}`"
                            class="function-snippet">
                            <div class="function-meta">
                                <span>{{ func.file_path || '-' }}</span>
                                <el-tag size="small" type="info" effect="plain">
                                    {{ formatLineRange(func.start_line, func.end_line) }}
                                </el-tag>
                            </div>
                        </div> -->

                        <div v-if="typeGroup.functions?.length > 10" class="type-group-expand-actions">
                            <el-button type="primary" link @click="toggleTypeGroupFunctionList(typeGroup.detail_key)">
                                {{ isTypeGroupFunctionListExpanded(typeGroup.detail_key) ? '收起函数列表' : `展开全部函数
                                (${typeGroup.functions.length})` }}
                            </el-button>
                        </div>
                    </el-card>
                </div>
            </el-card>

            <el-card v-for="row in detailFilteredStructureRows" :key="row.structure_cluster_id"
                :ref="(el) => setStructureDetailRef(row.structure_cluster_id, el)" class="panel-card detail-item-card"
                shadow="hover" :class="{ 'is-active-card': activeStructureDetailId === row.structure_cluster_id }">
                <template #header>
                    <div class="card-header detail-header">
                        <span>{{ row.name || '未命名结构簇' }}</span>
                        <el-tag type="info" effect="plain" round>结构cluster_id: {{ row.structure_cluster_id }}</el-tag>
                    </div>
                </template>

                <el-descriptions :column="1" :border="false" class="detail-descriptions">
                    <el-descriptions-item label="组件类型">
                        <div class="markdown-content" v-html="renderMarkdown(getRowType(row))"></div>
                    </el-descriptions-item>
                    <el-descriptions-item label="摘要">
                        <div class="markdown-content" v-html="renderMarkdown(row.summary)"></div>
                    </el-descriptions-item>
                    <el-descriptions-item label="关键差异点（语义）">
                        <div class="markdown-content" v-html="renderMarkdown(row.instance_defference)"></div>
                    </el-descriptions-item>
                </el-descriptions>

                <div class="instance-title">实例列表</div>
                <el-table :data="row.instances || []" border size="small" max-height="36vh">
                    <el-table-column prop="instance_id" label="id" min-width="30" />
                    <el-table-column label="page_path" min-width="260" show-overflow-tooltip>
                        <template #default="scope">
                            {{ formatPagePath(scope.row.page_path) }}
                        </template>
                    </el-table-column>
                    <el-table-column prop="instance_summary" label="语义描述" min-width="180" show-overflow-tooltip />
                    <el-table-column label="包含组件" min-width="40" align="center">
                        <template #default="scope">
                            <el-button type="primary" link @click="openComponentListDialog(scope.row)">查看</el-button>
                        </template>
                    </el-table-column>
                </el-table>
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
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import { CodeDiff } from 'v-code-diff'
import { buildGraphOption } from '../../utils/graphOption'
import 'highlight.js/styles/github-dark.css'

hljs.registerLanguage('javascript', javascript)

const props = defineProps({
    rows: {
        type: Array,
        default: () => []
    },
    cloneRows: {
        type: Array,
        default: () => []
    },
    cloneGroups: {
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
const panelMode = ref('graph')
const selectedStructureRow = ref(null)
const selectedCloneParentId = ref(null)
const searchKeyword = ref('')
const selectedType = ref('all')
const detailSearchKeyword = ref('')
const componentListDialogVisible = ref(false)
const selectedComponentList = ref([])
const chartTitle = ref('请选择结构簇查看关系图')
const treeProps = { children: 'children', label: 'label' }
const tableCurrentPage = ref(1)
const tablePageSize = ref(10)
const sortState = ref({
    prop: '',
    order: null
})
const leftDiffIndex = ref(0)
const rightDiffIndex = ref(1)
const expandedCloneCodeMap = ref({})
const expandedTypeGroupFunctionMap = ref({})
const activeDetailGroupKey = ref('')
const activeStructureDetailId = ref(null)
const cloneDetailRefs = new Map()
const structureDetailRefs = new Map()
let chartInstance = null

const normalizedRows = computed(() => {
    const structureRows = props.rows.map((parentRow, parentIndex) => {
        const parentKey = parentRow?.parent_cluster_id ?? parentIndex
        return {
            ...parentRow,
            row_id: `structure-parent-${parentKey}`,
            _isParent: true,
            _source: 'structure',
            children: (Array.isArray(parentRow?.children) ? parentRow.children : []).map((child, childIndex) => ({
                ...child,
                row_id: `structure-child-${parentKey}-${child?.structure_cluster_id ?? childIndex}`,
                _isParent: false,
                _source: 'structure'
            }))
        }
    })

    const cloneRows = props.cloneRows.map((parentRow, parentIndex) => {
        const parentKey = parentRow?.parent_cluster_id ?? parentIndex
        return {
            ...parentRow,
            row_id: `clone-parent-${parentKey}`,
            _isParent: true,
            _source: 'clone',
            children: (Array.isArray(parentRow?.children) ? parentRow.children : []).map((child, childIndex) => ({
                ...child,
                parent_cluster_id: parentRow?.parent_cluster_id ?? null,
                row_id: `clone-child-${parentKey}-${child?.structure_cluster_id ?? childIndex}`,
                _isParent: false,
                _source: 'clone'
            }))
        }
    })

    return [...structureRows, ...cloneRows]
})

const componentTypeOptions = computed(() => {
    const typeSet = new Set()
    for (const parentRow of normalizedRows.value) {
        if (parentRow?._source === 'clone') {
            const cloneType = getRowType(parentRow)
            if (cloneType && cloneType !== '-') {
                typeSet.add(cloneType)
            }
            continue
        }
        for (const child of parentRow.children || []) {
            const childType = getRowType(child)
            if (childType && childType !== '-') {
                typeSet.add(childType)
            }
        }
    }
    return Array.from(typeSet)
})

const treeRows = computed(() => {
    const keyword = searchKeyword.value.trim().toLowerCase()

    const filteredRows = normalizedRows.value
        .map((parentRow) => {
            const parentNameText = String(parentRow?.name || '').toLowerCase()
            const parentClusterText = String(parentRow?.parent_cluster_id || '').toLowerCase()
            const parentMatchesKeyword = !!keyword
                && (parentNameText.includes(keyword) || parentClusterText.includes(keyword))

            const filteredChildren = (parentRow.children || []).filter((child) => {
                const childType = getRowType(child)
                const matchesType = selectedType.value === 'all' || childType === selectedType.value
                if (!matchesType) return false
                if (!keyword || parentMatchesKeyword) return true

                const childNameText = String(child?.name || '').toLowerCase()
                const clusterIdText = String(child?.structure_cluster_id || '').toLowerCase()
                return childNameText.includes(keyword) || clusterIdText.includes(keyword)
            })

            if (!filteredChildren.length) return null

            return {
                ...parentRow,
                children: filteredChildren
            }
        })
        .filter(Boolean)

    if (!sortState.value.prop || !sortState.value.order) {
        return filteredRows
    }

    return [...filteredRows].sort((a, b) => compareParentRows(a, b, sortState.value.prop, sortState.value.order))
})

const paginatedTreeRows = computed(() => {
    const start = (tableCurrentPage.value - 1) * tablePageSize.value
    const end = start + tablePageSize.value
    return treeRows.value.slice(start, end)
})

const flattenedStructureRows = computed(() => {
    const rows = []
    for (const parent of treeRows.value) {
        if (parent._source !== 'structure') continue
        for (const child of parent.children || []) {
            rows.push(child)
        }
    }
    return rows
})

const detailFilteredStructureRows = computed(() => {
    const selectedRow = selectedStructureRowForDetail.value
    if (!selectedRow) return []

    const keyword = detailSearchKeyword.value.trim().toLowerCase()
    if (!keyword) return [selectedRow]

    const instances = Array.isArray(selectedRow.instances)
        ? selectedRow.instances.filter((instance) =>
            String(instance?.instance_summary || '').toLowerCase().includes(keyword)
        )
        : []
    return [{ ...selectedRow, instances }]
})

const normalizedCloneGroups = computed(() => {
    return props.cloneGroups.map((group, groupIndex) => ({
        ...group,
        group_key: group.group_key || `clone-group-${groupIndex}`,
        summary: group?.summary && typeof group.summary === 'object' ? group.summary : {},
        relevent_projects: Array.isArray(group?.relevent_projects) ? group.relevent_projects : [],
        type1_group: Array.isArray(group?.type1_group) ? group.type1_group : []
    }))
})

const detailFilteredCloneGroups = computed(() => {
    const selectedGroup = selectedCloneGroupForDetail.value
    if (!selectedGroup) return []

    const keyword = detailSearchKeyword.value.trim().toLowerCase()
    if (!keyword) return [selectedGroup]

    const summaryValues = Object.values(selectedGroup.summary || {}).map((value) => String(value || '').toLowerCase())
    const summaryMatched = summaryValues.some((value) => value.includes(keyword))
    if (summaryMatched) return [selectedGroup]

    const typeGroupMatched = selectedGroup.type1_group.some((typeGroup) =>
        String(typeGroup.group_name || '').toLowerCase().includes(keyword)
        || String(typeGroup.functionality || '').toLowerCase().includes(keyword)
    )
    return typeGroupMatched ? [selectedGroup] : []
})

const selectedCloneGroupForDetail = computed(() => {
    if (!activeDetailGroupKey.value) return null

    return normalizedCloneGroups.value.find((group) => {
        if (group.group_key !== activeDetailGroupKey.value) return false
        return treeRows.value.some((row) => row._source === 'clone' && row.parent_cluster_id === group.parent_cluster_id)
    }) || null
})

const selectedStructureRowForDetail = computed(() => {
    if (activeStructureDetailId.value === null || activeStructureDetailId.value === undefined) return null
    return flattenedStructureRows.value.find((row) => row.structure_cluster_id === activeStructureDetailId.value) || null
})

const hasActiveDetailSelection = computed(() => {
    return !!selectedCloneGroupForDetail.value || !!selectedStructureRowForDetail.value
})

const selectedPayload = computed(() => {
    const visualization = selectedStructureRow.value?.visualization || null
    if (!visualization || visualization.kind !== 'subgraph') return null
    return props.charts.subgraphs?.[visualization.key] || null
})

const treeData = computed(() => selectedPayload.value?.tree || [])

const activeCloneGroup = computed(() => {
    return normalizedCloneGroups.value.find((group) => group.parent_cluster_id === selectedCloneParentId.value) || null
})

const leftDiffGroup = computed(() => activeCloneGroup.value?.type1_group?.[leftDiffIndex.value] || null)
const rightDiffGroup = computed(() => activeCloneGroup.value?.type1_group?.[rightDiffIndex.value] || null)
const leftDiffCode = computed(() => getTypeGroupCode(leftDiffGroup.value))
const rightDiffCode = computed(() => getTypeGroupCode(rightDiffGroup.value))
const diffFileName = computed(() => {
    const leftName = leftDiffGroup.value?.group_name || '左侧函数组'
    const rightName = rightDiffGroup.value?.group_name || '右侧函数组'
    return `${leftName} vs ${rightName}`
})

const panelTitle = computed(() => {
    if (panelMode.value === 'diff') {
        return '代码差异'
    }
    return chartTitle.value
})

const ensureChart = () => {
    if (chartRef.value && !chartInstance) {
        chartInstance = echarts.init(chartRef.value)
    }
}

const renderGraph = async () => {
    if (panelMode.value !== 'graph' || graphMode.value !== 'directed') return
    const payload = selectedPayload.value
    if (!payload) return

    await nextTick()
    ensureChart()
    if (!chartInstance) return

    chartTitle.value = payload.title || '关系图'
    chartInstance.setOption(buildGraphOption(payload), true)
}

const getRowType = (row) => {
    if (!row) return '-'
    if (row._source === 'clone') {
        const category = String(row.category || '').trim()
        return category ? `${category}脚本` : '脚本'
    }
    if (row._isParent) {
        return row.children?.length ? getRowType(row.children[0]) : '-'
    }
    return row.show_type || row.type || '-'
}

const formatDisplayValue = (value) => {
    if (value === null || value === undefined || value === '' || value === 'none') {
        return '-'
    }
    return value
}

const getActionLabel = (row) => {
    if (!row) return ''
    if (row._source === 'clone' && row._isParent) return '查看函数组对比'
    if (row._source === 'clone' && !row._isParent) return '查看函数组详情'
    return ''
}

const selectStructureRow = async (row) => {
    if (!row || row._isParent || row._source !== 'structure') return

    panelMode.value = 'graph'
    selectedStructureRow.value = row
    const payload = selectedPayload.value
    chartTitle.value = payload?.title || '关系图'

    if (graphMode.value === 'directed') {
        await renderGraph()
    }
}

const openCloneDiff = (row) => {
    selectedCloneParentId.value = row.parent_cluster_id
    panelMode.value = 'diff'
}

const setCloneDetailRef = (groupKey, element) => {
    if (element) {
        cloneDetailRefs.set(groupKey, element.$el || element)
    } else {
        cloneDetailRefs.delete(groupKey)
    }
}

const setStructureDetailRef = (clusterId, element) => {
    if (element) {
        structureDetailRefs.set(clusterId, element.$el || element)
    } else {
        structureDetailRefs.delete(clusterId)
    }
}

const openStructureChildDetail = async (row) => {
    if (!row || row._isParent || row._source !== 'structure') return
    const targetClusterId = row.structure_cluster_id
    if (targetClusterId === null || targetClusterId === undefined) return

    detailSearchKeyword.value = ''
    activeDetailGroupKey.value = ''
    activeStructureDetailId.value = targetClusterId
    await nextTick()

    const targetElement = structureDetailRefs.get(targetClusterId)

    targetElement?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    })
}

const openCloneDetail = async (row) => {
    const cloneGroup = normalizedCloneGroups.value.find((group) => group.parent_cluster_id === row.parent_cluster_id)
    if (!cloneGroup) return

    detailSearchKeyword.value = ''
    activeStructureDetailId.value = null
    activeDetailGroupKey.value = cloneGroup.group_key
    await nextTick()
    cloneDetailRefs.get(cloneGroup.group_key)?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    })
}

const handleDetailAction = async (row) => {
    if (row._source === 'clone' && row._isParent) {
        openCloneDiff(row)
        return
    }
    if (row._source === 'clone') {
        await openCloneDetail(row)
        return
    }
}

const handleCurrentChange = async (row) => {
    if (row && !row._isParent && row._source === 'structure') {
        await selectStructureRow(row)
    }
}

const openComponentListDialog = (row) => {
    selectedComponentList.value = (row.component_id_list || []).map((id) => ({ id }))
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

const formatLineRange = (startLine, endLine) => {
    if (startLine && endLine) return `${startLine} - ${endLine}`
    if (startLine) return `${startLine}`
    return '-'
}

const highlightJsCode = (code) => {
    const source = String(code || '')
    if (!source.trim()) return ''
    return hljs.highlight(source, { language: 'javascript' }).value
}

const escapeHtml = (value) => String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const applyInlineMarkdown = (text) => {
    return text
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
}

const renderMarkdown = (value) => {
    const source = String(value || '').trim()
    if (!source) return '-'

    const escaped = escapeHtml(source)
    const lines = escaped.split('\n')
    const parts = []
    let listBuffer = []

    const flushList = () => {
        if (!listBuffer.length) return
        parts.push(`<ul>${listBuffer.map((item) => `<li>${applyInlineMarkdown(item)}</li>`).join('')}</ul>`)
        listBuffer = []
    }

    for (const rawLine of lines) {
        const line = rawLine.trim()
        if (!line) {
            flushList()
            continue
        }

        const unorderedMatch = line.match(/^[-*]\s+(.+)$/)
        if (unorderedMatch) {
            listBuffer.push(unorderedMatch[1])
            continue
        }

        flushList()
        parts.push(`<p>${applyInlineMarkdown(line)}</p>`)
    }

    flushList()
    return parts.join('') || '-'
}

const getRange = (children, key) => {
    if (!children || !children.length) return '-'
    const values = children
        .map((child) => child[key])
        .filter((value) => value !== undefined && value !== null && value !== 'none' && !Number.isNaN(Number(value)))
        .map((value) => Number(value))
    if (!values.length) return '-'
    const min = Math.min(...values)
    const max = Math.max(...values)
    return min === max ? `${min}` : `${min}~${max}`
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

    if (prop === 'size') {
        const childValues = getNumericValuesFromChildren(row.children, 'size')
        return childValues.length ? Math.min(...childValues) : null
    }

    const parentValue = toSortableNumber(row[prop])
    if (parentValue !== null) {
        return parentValue
    }

    const childValues = getNumericValuesFromChildren(row.children, prop)
    if (!childValues.length) return null

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
        order: order || null
    }
    tableCurrentPage.value = 1
}

const formatSimilarity = (value) => {
    const numeric = Number(value)
    return Number.isFinite(numeric) ? numeric.toFixed(4) : '-'
}

const formatSimilarityRange = (range) => {
    if (!range || range.min === null || range.max === null || range.min === undefined || range.max === undefined) {
        return '-'
    }
    return `${formatSimilarity(range.min)} ~ ${formatSimilarity(range.max)}`
}

const getTypeGroupCode = (group) => {
    if (!group || !Array.isArray(group.functions) || !group.functions.length) {
        return ''
    }
    return String(group.functions[0]?.code || '')
}

const getDiffGroupMeta = (group) => {
    if (!group || !Array.isArray(group.functions) || !group.functions.length) {
        return '未找到可对比代码'
    }
    const func = group.functions[0]
    return `${func.file_path || '-'} · ${formatLineRange(func.start_line, func.end_line)}`
}

const tableRowClassName = ({ row }) => {
    if (row._isParent && row._source === 'clone') {
        return 'clone-parent-row'
    }
    if (row._isParent) {
        return 'parent-cluster-row'
    }
    return ''
}

const toggleCloneTypeGroup = (detailKey) => {
    expandedCloneCodeMap.value = {
        ...expandedCloneCodeMap.value,
        [detailKey]: !expandedCloneCodeMap.value[detailKey]
    }
}

const isCloneTypeGroupExpanded = (detailKey) => !!expandedCloneCodeMap.value[detailKey]

const toggleTypeGroupFunctionList = (detailKey) => {
    expandedTypeGroupFunctionMap.value = {
        ...expandedTypeGroupFunctionMap.value,
        [detailKey]: !expandedTypeGroupFunctionMap.value[detailKey]
    }
}

const isTypeGroupFunctionListExpanded = (detailKey) => !!expandedTypeGroupFunctionMap.value[detailKey]

const getVisibleTypeGroupFunctions = (typeGroup) => {
    const functions = Array.isArray(typeGroup?.functions) ? typeGroup.functions : []
    if (isTypeGroupFunctionListExpanded(typeGroup?.detail_key)) {
        return functions
    }
    return functions.slice(0, 10)
}

const getTypeGroupFileRows = (typeGroup) => {
    const functions = Array.isArray(typeGroup?.functions) ? typeGroup.functions : []
    const rows = []
    const seen = new Set()

    for (const func of functions) {
        const filePath = func?.file_path || '-'
        if (seen.has(filePath)) continue
        seen.add(filePath)
        rows.push({
            file_path: filePath,
            line_range: formatLineRange(func?.start_line, func?.end_line)
        })
    }

    return rows
}

const initSelection = async () => {
    if (!flattenedStructureRows.value.length) {
        selectedStructureRow.value = null
        chartTitle.value = '请选择结构簇查看关系图'
        return
    }

    const currentId = selectedStructureRow.value?.structure_cluster_id
    const matched = flattenedStructureRows.value.find((row) => row.structure_cluster_id === currentId)
    selectedStructureRow.value = matched || flattenedStructureRows.value[0]

    const payload = selectedPayload.value
    chartTitle.value = payload?.title || '关系图'

    if (panelMode.value === 'graph' && graphMode.value === 'directed' && props.isActive) {
        await renderGraph()
    }
}

watch(
    flattenedStructureRows,
    async () => {
        await initSelection()
    },
    { immediate: true }
)

watch([treeRows, tablePageSize], () => {
    const maxPage = Math.max(1, Math.ceil(treeRows.value.length / tablePageSize.value))
    if (tableCurrentPage.value > maxPage) {
        tableCurrentPage.value = maxPage
    }
})

watch([searchKeyword, selectedType], () => {
    tableCurrentPage.value = 1
})

watch([selectedCloneGroupForDetail, selectedStructureRowForDetail], ([cloneGroup, structureRow]) => {
    if (!cloneGroup && activeDetailGroupKey.value) {
        activeDetailGroupKey.value = ''
    }
    if (!structureRow && activeStructureDetailId.value !== null) {
        activeStructureDetailId.value = null
    }
})

watch(activeCloneGroup, (group) => {
    if (!group) return
    leftDiffIndex.value = 0
    rightDiffIndex.value = group.type1_group.length > 1 ? 1 : 0
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

watch(
    () => props.isActive,
    async (value) => {
        if (value && panelMode.value === 'graph' && graphMode.value === 'directed') {
            await renderGraph()
        }
    },
    { flush: 'post' }
)

watch(panelMode, async (value) => {
    if (value !== 'graph' && chartInstance) {
        chartInstance.dispose()
        chartInstance = null
        return
    }
    if (value === 'graph' && graphMode.value === 'directed' && props.isActive) {
        await renderGraph()
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
    width: 320px;
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

.graph-tree {
    background: transparent;
}

.graph-canvas {
    width: 100%;
    height: 58vh;
    min-height: 360px;
}

.diff-panel {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.diff-selector-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.diff-selector-column {
    padding: 14px;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
}

.selector-label {
    margin-bottom: 10px;
    font-weight: 700;
    color: #0f172a;
}

.selector-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.selector-code-meta {
    margin-top: 10px;
    font-size: 12px;
    color: #64748b;
}

.diff-view-wrap {
    overflow: auto;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background: #ffffff;
    padding: 8px;
}

.instance-title,
.subsection-title {
    margin: 12px 0 8px;
    font-weight: 600;
    color: #334155;
}

.detail-descriptions {
    margin-bottom: 8px;
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
    width: 280px;
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

.clone-detail-card {
    scroll-margin-top: 20px;
}

.is-active-card {
    box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.22);
}

.multiline-text {
    white-space: pre-wrap;
    line-height: 1.7;
}

.markdown-content {
    line-height: 1.7;
    color: #334155;
}

.markdown-content :deep(p) {
    margin: 0;
}

.markdown-content :deep(p + p) {
    margin-top: 8px;
}

.markdown-content :deep(ul) {
    margin: 8px 0 0;
    padding-left: 20px;
}

.markdown-content :deep(li + li) {
    margin-top: 4px;
}

.markdown-content :deep(code) {
    padding: 2px 6px;
    border-radius: 6px;
    background: #e2e8f0;
    color: #0f172a;
    font-size: 12px;
}

.markdown-content :deep(strong) {
    color: #0f172a;
    font-weight: 700;
}

.tag-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.function-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.function-card {
    border-radius: 10px;
    background: #fbfdff;
}

.function-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
}

.function-header-text {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.function-group-title {
    font-weight: 700;
    color: #0f172a;
}

.function-group-desc {
    color: #475569;
    line-height: 1.6;
}

.function-snippet+.function-snippet {
    margin-top: 12px;
}

.type-group-code-block {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 12px;
}

.file-path-title {
    margin-top: 2px;
}

.file-path-table {
    border-radius: 8px;
}

.type-group-expand-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 8px;
}

.function-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 8px;
    color: #334155;
}

.code-block {
    margin: 0;
    padding: 14px;
    overflow: auto;
    border-radius: 10px;
    background: #0f172a;
    max-height: 72vh;
    min-height: 240px;
}

.detail-descriptions :deep(.el-descriptions__label) {
    font-weight: 700;
}

:deep(.parent-cluster-row) {
    background-color: #f0f9ff !important;
}

:deep(.clone-parent-row) {
    background-color: #fffbeb !important;
}

:deep(.v-code-diff) {
    font-size: 13px;
}

:deep(.v-code-diff pre) {
    max-height: 72vh;
}

:deep(.v-code-diff .file-diff) {
    margin-bottom: 0;
}

@media (max-width: 992px) {

    .with-action,
    .with-filter,
    .with-detail-search {
        flex-direction: column;
        align-items: flex-start;
    }

    .filter-actions {
        width: 100%;
        flex-direction: column;
    }

    .search-input,
    .type-select,
    .detail-search-input {
        width: 100%;
    }

    .diff-selector-grid {
        grid-template-columns: 1fr;
    }
}
</style>
