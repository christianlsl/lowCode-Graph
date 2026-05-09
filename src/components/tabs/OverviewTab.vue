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
                <div class="card-header">结构簇统计</div>
            </template>
            <el-table :data="stats" border>
                <el-table-column prop="show_type" label="展示类型" min-width="180" />
                <el-table-column prop="cluster_count" label="簇数量" min-width="120" />
                <el-table-column prop="instance_count" label="实例数量" min-width="120" />
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
        type: Array,
        default: () => []
    }
})

const coveredRepositories = computed(() => {
    const value = props.meta.covered_repositories
    if (Array.isArray(value)) {
        return value.length ? value.join(', ') : '-'
    }
    return value || '-'
})
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
