<template>
    <el-container class="page">
        <el-header class="header">
            <div class="header-title">低代码热点组件分析报告</div>
            <div class="header-actions">
                <span v-if="folderLoaded" class="folder-path">{{ folderPath }}</span>
                <el-button type="primary" plain @click="folderInputRef.click()">
                    {{ folderLoaded ? '重新选择' : '选择文件夹' }}
                </el-button>
                <input ref="folderInputRef" type="file" webkitdirectory @change="handleFolderChange"
                    style="display: none;" />
            </div>
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
                        :is-active="activeTab === 'structure-hotspot'" :folder-files="folderFiles" />
                </el-tab-pane>

                <el-tab-pane label="语义相似热点组件" name="semantic-hotspot">
                    <SemanticHotspotTab :rows="semanticHotspot.rows || []" :charts="charts"
                        :is-active="activeTab === 'semantic-hotspot'" :folder-files="folderFiles" />
                </el-tab-pane>

                <el-tab-pane label="模型相似热点组件" name="model-similarity-hotspot">
                    <ModelSimilarityHotspotTab :rows="modelSimilarityHotspotRows"
                        :is-active="activeTab === 'model-similarity-hotspot'" :folder-files="folderFiles" />
                </el-tab-pane>
            </el-tabs>
        </el-main>
    </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import processedData from './assets/graph_table_data.json'
import modelResultData from '../data/model_result.json'
import OverviewTab from './components/tabs/OverviewTab.vue'
import DefinitionsTab from './components/tabs/DefinitionsTab.vue'
import StructureHotspotTab from './components/tabs/StructureHotspotTab.vue'
import SemanticHotspotTab from './components/tabs/SemanticHotspotTab.vue'
import ModelSimilarityHotspotTab from './components/tabs/ModelSimilarityHotspotTab.vue'

const activeTab = ref('overview')
const folderInputRef = ref(null)
const folderFiles = ref(new Map())
const folderPath = ref('')
const folderLoaded = computed(() => folderFiles.value.size > 0)

const handleFolderChange = (event) => {
    const files = event.target.files
    const map = new Map()
    for (const file of files) {
        const relativePath = file.webkitRelativePath || file.name
        map.set(relativePath, file)
    }
    folderFiles.value = map
    if (files.length > 0) {
        const firstPath = files[0].webkitRelativePath || ''
        folderPath.value = firstPath.split('/')[0] || ''
    } else {
        folderPath.value = ''
    }
}

const meta = processedData.meta || {}
const stats = processedData.overview_stats || {}
const structureHotspot = processedData.structure_hotspot || {}
const cloneDetection = processedData.clone_detection || {}
const semanticHotspot = processedData.semantic_hotspot || {}
const charts = processedData.charts || { subgraphs: {} }
const modelSimilarityHotspotRows = Array.isArray(modelResultData?.frequent_patterns)
    ? modelResultData.frequent_patterns
    : []
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
    justify-content: space-between;
    height: 64px;
    color: #0f172a;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.folder-path {
    font-size: 13px;
    color: #16a34a;
    font-weight: 600;
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
