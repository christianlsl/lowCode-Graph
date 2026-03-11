<template>
    <div class="cards-container">
        <el-card class="panel-card" shadow="hover">
            <template #header>
                <div class="card-header">元信息</div>
            </template>
            <el-descriptions :column="1" border class="meta-descriptions">
                <el-descriptions-item label="报告日期">{{ meta.report_date || '-' }}</el-descriptions-item>
                <el-descriptions-item label="报告版本">{{ meta.report_version || '-' }}</el-descriptions-item>
                <el-descriptions-item label="生成工具版本">{{ meta.generator_tool_version || '-' }}</el-descriptions-item>
                <el-descriptions-item label="覆盖仓库">{{ coveredRepositories }}</el-descriptions-item>
            </el-descriptions>
        </el-card>

        <el-card class="panel-card" shadow="hover">
            <template #header>
                <div class="card-header">热点组件统计</div>
            </template>
            <el-table :data="overviewRows" border>
                <el-table-column prop="label" label="统计项" min-width="180" />
                <el-table-column prop="value" label="值" min-width="120" />
            </el-table>
        </el-card>
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    meta: {
        type: Object,
        default: () => ({})
    },
    stats: {
        type: Object,
        default: () => ({})
    }
})

const coveredRepositories = computed(() => {
    const value = props.meta.covered_repositories
    if (Array.isArray(value)) {
        return value.length ? value.join(', ') : '-'
    }
    return value || '-'
})

const overviewRows = computed(() => [
    { label: '识别热点簇', value: props.stats.hotspot_clusters ?? 0 },
    { label: '热点实例', value: props.stats.hotspot_instances ?? 0 },
    { label: '涉及工程个数', value: props.stats.projects_involved ?? 0 },
    { label: '涉及页面个数', value: props.stats.pages_involved ?? 0 },
    { label: '涉及组件个数', value: props.stats.components_involved ?? 0 },
    { label: '涉及服务个数', value: props.stats.services_involved ?? 0 },
    { label: '涉及模型个数', value: props.stats.models_involved ?? 0 }
])
</script>

<style scoped>
.cards-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 600px;
    margin: 0 auto;
}

.panel-card {
    border-radius: 12px;
}

.card-header {
    font-weight: 700;
    color: #0f172a;
}

.meta-descriptions {
    background: #f8fbff;
}
</style>
