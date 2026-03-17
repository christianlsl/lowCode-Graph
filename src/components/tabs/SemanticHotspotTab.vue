<template>
    <div class="semantic-hotspot-tab">
        <el-card class="panel-card" shadow="hover">
            <template #header>
                <div class="card-header with-filter">
                    <span>语义相似热点组件</span>
                    <div class="filter-actions">
                        <el-input v-model="searchKeyword" clearable placeholder="搜索语义簇名称/语义cluster_id"
                            class="search-input" />
                        <el-select v-model="selectedType" class="type-select" placeholder="选择组件类型">
                            <el-option label="全部组件类型" value="all" />
                            <el-option v-for="type in componentTypeOptions" :key="type" :label="type" :value="type" />
                        </el-select>
                    </div>
                </div>
            </template>

            <el-table :data="filteredRows" border row-key="semantic_similar_cluster_id" max-height="50vh"
                highlight-current-row @current-change="handleCurrentChange">
                <el-table-column prop="type" label="组件类型" min-width="120" />
                <el-table-column prop="semantic_similar_cluster_id" label="语义cluster_id" min-width="130" />
                <el-table-column prop="name" label="语义簇名称" min-width="180" show-overflow-tooltip />
                <el-table-column prop="struc_cluster_num" label="包含的结构cluster_id个数" min-width="180" sortable />
                <el-table-column prop="relevent_projects_num" label="涉及工程个数" min-width="120" sortable />
            </el-table>
        </el-card>

        <section class="detail-section">
            <div class="section-title with-detail-search">
                <span>语义相似热点组件详情</span>
                <el-input v-model="detailSearchKeyword" clearable placeholder="搜索语义相似点关键词"
                    class="detail-search-input" />
            </div>
            <el-card v-for="row in detailFilteredRows" :key="row.semantic_similar_cluster_id"
                class="panel-card detail-item-card" shadow="hover">
                <template #header>
                    <div class="card-header detail-header">
                        <span>{{ row.name || '未命名语义簇' }}</span>
                        <el-tag type="info" effect="plain" round>语义cluster_id: {{ row.semantic_similar_cluster_id
                            }}</el-tag>
                    </div>
                </template>

                <el-descriptions :column="1" :border="false" class="detail-descriptions">
                    <el-descriptions-item label="组件类型">{{ row.type || '-' }}</el-descriptions-item>
                    <el-descriptions-item label="语义相似点">{{ row.description || '-' }}</el-descriptions-item>
                    <el-descriptions-item label="包含的结构簇">
                        <div v-if="Array.isArray(row.structure_clusters) && row.structure_clusters.length"
                            class="cluster-list">
                            <div v-for="cluster in row.structure_clusters" :key="cluster.id" class="cluster-list-item">
                                <el-tag size="small" type="success" effect="light">{{ cluster.id }}</el-tag>
                                <span class="cluster-name">{{ cluster.name || '-' }}</span>
                            </div>
                        </div>
                        <span v-else>-</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="关键差异点（结构）">
                        {{ row.instance_defference || '-' }}
                    </el-descriptions-item>
                </el-descriptions>
            </el-card>
        </section>
    </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
    rows: {
        type: Array,
        default: () => []
    }
})

const selectedRow = ref(null)
const searchKeyword = ref('')
const selectedType = ref('all')
const detailSearchKeyword = ref('')

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
        const clusterIdText = String(row.semantic_similar_cluster_id || '').toLowerCase()
        return nameText.includes(keyword) || clusterIdText.includes(keyword)
    })
})

const detailFilteredRows = computed(() => {
    const keyword = detailSearchKeyword.value.trim().toLowerCase()
    if (!keyword) return filteredRows.value

    return filteredRows.value.filter((row) =>
        String(row.description || '').toLowerCase().includes(keyword)
    )
})

const handleCurrentChange = (row) => {
    if (row) {
        selectedRow.value = row
    }
}

watch(
    filteredRows,
    () => {
        if (!filteredRows.value.length) {
            selectedRow.value = null
            return
        }

        const currentId = selectedRow.value?.semantic_similar_cluster_id
        const matched = filteredRows.value.find((row) => row.semantic_similar_cluster_id === currentId)
        selectedRow.value = matched || filteredRows.value[0]
    },
    { immediate: true }
)
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

.detail-descriptions {
    min-height: 160px;
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

.detail-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.cluster-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.cluster-list-item {
    display: flex;
    gap: 8px;
    align-items: center;
}

.cluster-name {
    color: #334155;
}

@media (max-width: 992px) {
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
}
</style>
