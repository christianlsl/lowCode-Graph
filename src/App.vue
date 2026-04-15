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

                <el-tab-pane label="结构相似热点组件" name="structure-hotspot">
                    <StructureHotspotTab :rows="structureHotspot.rows || []" :charts="charts"
                        :clone-rows="cloneDetection.rows || []" :clone-groups="cloneDetection.groups || []"
                        :is-active="activeTab === 'structure-hotspot'" />
                </el-tab-pane>

                <el-tab-pane label="语义相似热点组件" name="semantic-hotspot">
                    <SemanticHotspotTab :rows="semanticHotspot.rows || []" />
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
import StructureHotspotTab from './components/tabs/StructureHotspotTab.vue'
import SemanticHotspotTab from './components/tabs/SemanticHotspotTab.vue'

const activeTab = ref('overview')

const meta = processedData.meta || {}
const stats = processedData.overview_stats || {}
const structureHotspot = processedData.structure_hotspot || {}
const cloneDetection = processedData.clone_detection || {}
const semanticHotspot = processedData.semantic_hotspot || {}
const charts = processedData.charts || { subgraphs: {} }
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
