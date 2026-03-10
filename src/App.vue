<template>
    <el-container class="page">
        <el-header class="header">
            <div class="header-title">低代码热点组件分析报告</div>
        </el-header>

        <el-main class="main">
            <el-tabs v-model="activeTab" class="main-tabs">
                <el-tab-pane label="分析概览" name="overview">
                    <OverviewTab :meta="meta" :stats="stats" />
                </el-tab-pane>

                <el-tab-pane label="相关定义" name="definitions">
                    <DefinitionsTab />
                </el-tab-pane>

                <el-tab-pane label="Top热点组件" name="top-hotspot">
                    <TopHotspotTab :structure-rows="topHotspot.structure_rows || []"
                        :semantic-rows="topHotspot.semantic_rows || []" :charts="charts"
                        :is-active="activeTab === 'top-hotspot'" />
                </el-tab-pane>

                <el-tab-pane label="热点组件详情" name="details">
                    <HotspotDetailsTab :structure-clusters="hotspotDetails.structure_clusters || []"
                        :semantic-clusters="hotspotDetails.semantic_clusters || []" :charts="charts"
                        :is-active="activeTab === 'details'" />
                </el-tab-pane>
            </el-tabs>
        </el-main>
    </el-container>
</template>

<script setup>
import { ref } from 'vue'
import processedData from './assets/graph_table_data.json'
import OverviewTab from './components/tabs/OverviewTab.vue'
import DefinitionsTab from './components/tabs/DefinitionsTab.vue'
import TopHotspotTab from './components/tabs/TopHotspotTab.vue'
import HotspotDetailsTab from './components/tabs/HotspotDetailsTab.vue'

const activeTab = ref('overview')

const meta = processedData.meta || {}
const stats = processedData.overview_stats || {}
const topHotspot = processedData.top_hotspot || {}
const hotspotDetails = processedData.hotspot_details || {}
const charts = processedData.charts || { subgraphs: {}, instances: {} }
</script>

<style scoped>
.page {
    min-height: 100vh;
    background:
        radial-gradient(circle at 15% 0%, #d8f3ff 0%, transparent 34%),
        radial-gradient(circle at 92% 4%, #ffe9cc 0%, transparent 30%),
        linear-gradient(180deg, #f1f8ff 0%, #f8fbff 100%);
}

.header {
    display: flex;
    align-items: center;
    height: 64px;
    color: #0f172a;
}

.header-title {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.3px;
}

.main {
    padding-top: 6px;
}

.main-tabs {
    --el-tabs-header-height: 48px;
}
</style>
