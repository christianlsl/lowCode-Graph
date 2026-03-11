<template>
    <div class="semantic-hotspot-tab">
        <el-card class="panel-card" shadow="hover">
            <template #header>
                <div class="card-header">语义相似热点组件</div>
            </template>

            <el-table :data="rows" border row-key="semantic_similar_cluster_id" max-height="50vh" highlight-current-row
                @current-change="handleCurrentChange">
                <el-table-column prop="type" label="组件类型" min-width="120" />
                <el-table-column prop="semantic_similar_cluster_id" label="语义cluster_id" min-width="130" />
                <el-table-column prop="name" label="语义簇名称" min-width="180" show-overflow-tooltip />
                <el-table-column prop="struc_cluster_num" label="包含的结构cluster_id个数" min-width="180" />
                <el-table-column prop="relevent_projects_num" label="涉及工程个数" min-width="120" />
            </el-table>
        </el-card>

        <section class="detail-section">
            <div class="section-title">语义相似热点组件详情</div>
            <el-card v-for="row in rows" :key="row.semantic_similar_cluster_id" class="panel-card detail-item-card"
                shadow="hover">
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
import { ref, watch } from 'vue'

const props = defineProps({
    rows: {
        type: Array,
        default: () => []
    }
})

const selectedRow = ref(null)
const handleCurrentChange = (row) => {
    if (row) {
        selectedRow.value = row
    }
}

watch(
    () => props.rows,
    () => {
        if (!props.rows.length) {
            selectedRow.value = null
            return
        }

        const currentId = selectedRow.value?.semantic_similar_cluster_id
        const matched = props.rows.find((row) => row.semantic_similar_cluster_id === currentId)
        selectedRow.value = matched || props.rows[0]
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
    .detail-header {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>
