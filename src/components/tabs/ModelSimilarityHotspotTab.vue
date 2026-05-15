<template>
    <div class="model-similarity-hotspot-tab">
        <el-card class="panel-card" shadow="hover">
            <template #header>
                <div class="card-header with-filter">
                    <span>模型相似热点组件</span>
                    <div class="header-actions">
                        <el-input v-model="searchKeyword" clearable placeholder="搜索相似簇名称/介绍" class="search-input" />
                    </div>
                </div>
            </template>

            <el-table :data="paginatedRows" border max-height="46vh" @sort-change="handleSortChange">
                <el-table-column prop="name" label="相似簇名称" min-width="220" show-overflow-tooltip>
                    <template #default="scope">
                        {{ formatDisplayValue(scope.row.name) }}
                    </template>
                </el-table-column>
                <el-table-column prop="support" label="支持率" min-width="120" sortable="custom">
                    <template #default="scope">
                        {{ formatSupport(scope.row.support) }}
                    </template>
                </el-table-column>
                <el-table-column prop="support_count" label="模型支持度" min-width="120" sortable="custom">
                    <template #default="scope">
                        {{ formatDisplayValue(scope.row.support_count) }}
                    </template>
                </el-table-column>
                <!-- <el-table-column prop="total_trans" label="工程元素总数" min-width="120" sortable="custom">
                    <template #default="scope">
                        {{ formatDisplayValue(scope.row.total_trans) }}
                    </template>
                </el-table-column> -->
                <el-table-column label="详情" min-width="120" fixed="right">
                    <template #default="scope">
                        <el-button type="success" plain @click="openDetailForRow(scope.row)">
                            查看详情
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <div class="table-pagination">
                <el-pagination v-model:current-page="tableCurrentPage" v-model:page-size="tablePageSize"
                    :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" :total="filteredRows.length" />
            </div>
        </el-card>

        <section class="detail-section">
            <div class="section-title">模型相似热点组件详情</div>

            <el-empty v-if="!filteredRows.length" description="暂无 frequent_patterns 数据" />
            <el-empty v-else-if="!selectedDetailRow" description="请在上方表格中点击查看详情" />

            <el-card v-else ref="detailCardRef" :key="selectedDetailRow._rowId" class="panel-card detail-item-card"
                shadow="hover" :class="{ 'is-active-card': !!activeDetailKey }">
                <template #header>
                    <div class="card-header detail-header">
                        <span>{{ formatDisplayValue(selectedDetailRow.name) }}</span>
                        <el-tag type="success" effect="plain" round>
                            支持率: {{ formatSupport(selectedDetailRow.support) }}
                        </el-tag>
                    </div>
                </template>

                <el-descriptions :column="1" border class="detail-descriptions">
                    <el-descriptions-item label="相似字段组名称">
                        {{ formatDisplayValue(selectedDetailRow.name) }}
                    </el-descriptions-item>
                    <el-descriptions-item label="相似字段组介绍">
                        {{ formatDisplayValue(selectedDetailRow.description) }}
                    </el-descriptions-item>
                    <!-- <el-descriptions-item label="当前工程包含元素个数">
                        {{ formatDisplayValue(selectedDetailRow.total_trans) }} -->
                    <!-- </el-descriptions-item> -->
                    <el-descriptions-item label="模型支持度">
                        {{ formatDisplayValue(selectedDetailRow.support_count) }}
                    </el-descriptions-item>
                    <el-descriptions-item label="支持率">
                        {{ formatSupport(selectedDetailRow.support) }} ({{
                            formatDisplayValue(selectedDetailRow.support_count) }}
                        / {{
                            formatDisplayValue(selectedDetailRow.total_trans) }})
                    </el-descriptions-item>
                </el-descriptions>

                <div class="subsection-title">相似字段组包含的所有字段</div>
                <el-table :data="itemsetsTableData" border size="small" max-height="28vh" empty-text="-">
                    <el-table-column type="index" label="序号" width="70" align="center" />
                    <el-table-column prop="value" label="字段名称" min-width="260" show-overflow-tooltip />
                </el-table>

                <div class="subsection-title">当前相似字段组关联模型</div>
                <el-table :data="modelListTableData" border size="small" max-height="28vh" empty-text="-">
                    <el-table-column type="index" label="序号" width="70" align="center" />
                    <el-table-column prop="value" label="模型名称" min-width="260" show-overflow-tooltip />
                    <el-table-column label="查看模型" width="120" align="center">
                        <template #default="scope">
                            <el-button type="primary" link @click="viewModelFile(scope.$index)">
                                查看
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </el-card>
        </section>

        <el-dialog v-model="modelDialogVisible" :title="modelDialogTitle" width="60%" top="5vh">
            <el-scrollbar max-height="70vh">
                <pre class="model-json-content" v-html="highlightedJson"></pre>
            </el-scrollbar>
        </el-dialog>
    </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import hljs from 'highlight.js/lib/core'
import json from 'highlight.js/lib/languages/json'
import 'highlight.js/styles/github.css'

hljs.registerLanguage('json', json)

const props = defineProps({
    rows: {
        type: Array,
        default: () => []
    },
    isActive: {
        type: Boolean,
        default: false
    },
    folderFiles: {
        type: Map,
        default: () => new Map()
    }
})

const searchKeyword = ref('')
const tableCurrentPage = ref(1)
const tablePageSize = ref(10)
const sortState = ref({
    prop: '',
    order: null,
})
const activeDetailKey = ref('')
const detailCardRef = ref(null)
const modelDialogVisible = ref(false)
const modelDialogContent = ref('')
const modelDialogTitle = ref('')

const normalizedRows = computed(() => {
    return (Array.isArray(props.rows) ? props.rows : []).map((row, index) => ({
        ...row,
        _rowId: getRowKey(row, index),
    }))
})

const filteredRows = computed(() => {
    const keyword = searchKeyword.value.trim().toLowerCase()
    const sourceRows = normalizedRows.value.filter((row) => {
        if (!keyword) return true

        const name = String(row?.name || '').toLowerCase()
        const description = String(row?.description || '').toLowerCase()
        return name.includes(keyword) || description.includes(keyword)
    })

    const defaultSortedRows = [...sourceRows].sort((a, b) => {
        const supportDiff = toSortableNumber(b?.support) - toSortableNumber(a?.support)
        if (supportDiff !== 0) return supportDiff

        const supportCountDiff = toSortableNumber(b?.support_count) - toSortableNumber(a?.support_count)
        if (supportCountDiff !== 0) return supportCountDiff

        return String(a?.name || '').localeCompare(String(b?.name || ''), 'zh-Hans-CN')
    })

    if (!sortState.value.prop || !sortState.value.order) {
        return defaultSortedRows
    }

    return [...defaultSortedRows].sort((a, b) => compareRows(a, b, sortState.value.prop, sortState.value.order))
})

const paginatedRows = computed(() => {
    const start = (tableCurrentPage.value - 1) * tablePageSize.value
    const end = start + tablePageSize.value
    return filteredRows.value.slice(start, end)
})

const selectedDetailRow = computed(() => {
    if (!activeDetailKey.value) return null
    return filteredRows.value.find((row) => row._rowId === activeDetailKey.value) || null
})

const itemsetsTableData = computed(() => {
    return toStringArray(selectedDetailRow.value?.itemsets).map((value) => ({ value }))
})

const modelListTableData = computed(() => {
    const names = toStringArray(selectedDetailRow.value?.model_list)
    const paths = toStringArray(selectedDetailRow.value?.model_path_list)
    return names.map((value, i) => ({ value, path: paths[i] || '' }))
})

const getRowKey = (row, index) => {
    const support = row?.support ?? 'na'
    const supportCount = row?.support_count ?? 'na'
    const total = row?.total_trans ?? 'na'
    return `${row?.name || 'model-similarity'}-${support}-${supportCount}-${total}-${index}`
}

const openDetailForRow = async (row) => {
    activeDetailKey.value = row._rowId

    await nextTick()
    const targetCard = detailCardRef.value?.$el || detailCardRef.value
    if (targetCard) {
        targetCard.scrollIntoView({ behavior: 'smooth', block: 'start' })
        return
    }

    document.querySelector('.detail-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const toStringArray = (value) => {
    if (!Array.isArray(value)) return []
    return value.map((item) => String(item)).filter((item) => item)
}

const toSortableNumber = (value) => {
    const numeric = Number(value)
    return Number.isFinite(numeric) ? numeric : -1
}

const compareRows = (a, b, prop, order) => {
    const direction = order === 'ascending' ? 1 : -1
    const aValue = a?.[prop]
    const bValue = b?.[prop]

    if (prop === 'name') {
        return String(aValue || '').localeCompare(String(bValue || ''), 'zh-Hans-CN') * direction
    }

    return (toSortableNumber(aValue) - toSortableNumber(bValue)) * direction
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

const formatSupport = (value) => {
    const numeric = Number(value)
    if (!Number.isFinite(numeric)) return '-'
    return `${(numeric * 100).toFixed(2)}%`
}

const highlightedJson = computed(() => {
    if (!modelDialogContent.value) return ''
    try {
        return hljs.highlight(modelDialogContent.value, { language: 'json' }).value
    } catch {
        return modelDialogContent.value
    }
})

const normalizeModelPath = (path) => {
    return path.replace(/^\/+/, '').replace(/\\/g, '/')
}

const viewModelFile = async (index) => {
    const rawPath = modelListTableData.value[index]?.path
    if (!rawPath) {
        modelDialogContent.value = '无模型文件路径'
        modelDialogTitle.value = '模型文件'
        modelDialogVisible.value = true
        return
    }

    if (!props.folderFiles.size) {
        modelDialogContent.value = '请先选择模型文件夹'
        modelDialogTitle.value = '模型文件'
        modelDialogVisible.value = true
        return
    }

    const normalized = normalizeModelPath(rawPath)
    const fileName = normalized.split('/').pop()

    let matchedFile = props.folderFiles.get(normalized)
    if (!matchedFile) {
        for (const [key, file] of props.folderFiles) {
            if (key.endsWith('/' + normalized) || key === normalized) {
                matchedFile = file
                break
            }
        }
    }
    if (!matchedFile) {
        for (const [key, file] of props.folderFiles) {
            if (key.endsWith('/' + fileName)) {
                matchedFile = file
                break
            }
        }
    }

    if (!matchedFile) {
        modelDialogContent.value = `未找到文件: ${normalized}`
        modelDialogTitle.value = fileName || '模型文件'
        modelDialogVisible.value = true
        return
    }

    try {
        const text = await matchedFile.text()
        const json = JSON.parse(text)
        modelDialogContent.value = JSON.stringify(json, null, 2)
        modelDialogTitle.value = fileName || '模型文件'
    } catch (e) {
        modelDialogContent.value = `读取文件失败: ${e.message}`
        modelDialogTitle.value = fileName || '模型文件'
    }
    modelDialogVisible.value = true
}

watch([searchKeyword, tablePageSize], () => {
    tableCurrentPage.value = 1
})

watch(filteredRows, () => {
    const maxPage = Math.max(1, Math.ceil(filteredRows.value.length / tablePageSize.value))
    if (tableCurrentPage.value > maxPage) {
        tableCurrentPage.value = maxPage
    }

    if (activeDetailKey.value) {
        const exists = filteredRows.value.some((row) => row._rowId === activeDetailKey.value)
        if (!exists) {
            activeDetailKey.value = ''
        }
    }
}, { immediate: true })
</script>

<style scoped>
.model-similarity-hotspot-tab {
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

.with-filter {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.model-json-content {
    margin: 0;
    padding: 16px;
    font-size: 13px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
    background: #f6f8fa;
    border-radius: 6px;
    color: #24292f;
}

.search-input {
    width: 280px;
}

.table-pagination {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
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

.detail-item-card {
    border: 1px solid #e2e8f0;
}

.is-active-card {
    border-color: #16a34a;
    box-shadow: 0 0 0 2px rgba(22, 163, 74, 0.12);
}

.detail-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.detail-descriptions :deep(.el-descriptions__label) {
    font-weight: 700;
}

.subsection-title {
    margin-top: 14px;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 700;
    color: #334155;
}

@media (max-width: 992px) {
    .with-filter {
        flex-direction: column;
        align-items: flex-start;
    }

    .header-actions {
        flex-direction: column;
        align-items: flex-start;
        width: 100%;
    }

    .search-input {
        width: 100%;
    }

    .detail-header {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>
