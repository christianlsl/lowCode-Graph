<template>
    <div class="definitions-container">
        <header class="page-header">
            <h2 class="main-title">热点组件挖掘定义与规范</h2>
            <p class="sub-subtitle">Hotspot Component Mining Definitions & Standards</p>
        </header>

        <div class="top-sections">
            <el-card v-for="section in definitionSections" :key="section.title" class="premium-card highlight-card">
                <div class="card-header-custom">
                    <el-icon class="header-icon">
                        <Collection />
                    </el-icon>
                    <span class="badge" :class="section.badgeType">{{ section.badge }}</span>
                    <span class="title">{{ section.title }}</span>
                </div>
                <div class="content-body" v-html="formatContent(section.content)"></div>
            </el-card>
        </div>

        <h3 class="group-label"><el-icon>
                <Operation />
            </el-icon> 相似性维度分析</h3>
        <div class="grid-layout">
            <el-card v-for="item in subSections" :key="item.title" class="premium-card sub-card" shadow="hover">
                <template #header>
                    <div class="sub-header">
                        <el-tag effect="plain" round size="small">{{ item.badge }}</el-tag>
                        <span class="sub-title">{{ item.title }}</span>
                    </div>
                </template>
                <div class="sub-content" v-html="formatContent(item.content)"></div>
            </el-card>
        </div>

        <div class="strategy-section">
            <el-card v-for="section in strategySections" :key="section.title" class="premium-card highlight-card">
                <div class="card-header-custom">
                    <el-icon class="header-icon">
                        <Collection />
                    </el-icon>
                    <span class="badge" :class="section.badgeType">{{ section.badge }}</span>
                    <span class="title">{{ section.title }}</span>
                </div>
                <div class="content-body" v-html="formatContent(section.content)"></div>
            </el-card>
        </div>

        <div class="rule-section">
            <el-card class="premium-card table-card">
                <template #header>
                    <div class="card-header-custom">
                        <el-icon class="header-icon">
                            <List />
                        </el-icon>
                        <span class="badge rule-badge">规则表</span>
                        <span class="title">最小支持度 - 组件粒度映射</span>
                    </div>
                </template>

                <el-table :data="thresholdRules" border stripe style="width: 100%"
                    header-cell-class-name="table-header">
                    <el-table-column type="index" label="序号" width="70" align="center" />
                    <el-table-column prop="type" label="组件类型" width="120" align="center">
                        <template #default="scope">
                            <el-tag size="small">{{ scope.row.type }}</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="size_range" label="组件大小 (粒度)" />
                    <el-table-column prop="min_support" label="最小支持度阈值" width="180">
                        <template #default="scope">
                            <div class="support-cell">
                                <el-progress :percentage="parseInt(scope.row.min_support)"
                                    :format="() => scope.row.min_support" :stroke-width="12"
                                    :color="getProgressColor(scope.row.min_support)" />
                            </div>
                        </template>
                    </el-table-column>
                </el-table>
            </el-card>
        </div>
    </div>
</template>
<script setup>
import { Collection, Operation, List } from '@element-plus/icons-vue'
import defsData from '../../assets/defs.json'

const { allSections, thresholdRules } = defsData

const definitionSections = allSections.filter(s => s.badge === '定义')
const strategySections = allSections.filter(s => s.badge === '策略')
const subSections = allSections.filter(s => !['定义', '策略'].includes(s.badge))

// 简单格式化：将换行符转为 HTML 或加粗重点
const formatContent = (text) => {
    return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

const getProgressColor = (val) => {
    const num = parseInt(val)
    if (num > 8) return '#409eff'
    if (num > 4) return '#67c23a'
    return '#e6a23c'
}
</script>
<style scoped>
.definitions-container {
    padding: 24px;
    background-color: #f4f7f9;
    min-height: 100vh;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

.page-header {
    margin-bottom: 30px;
    border-left: 5px solid #409eff;
    padding-left: 15px;
}

.main-title {
    font-size: 24px;
    color: #1f2f3d;
    margin: 0;
}

.sub-subtitle {
    color: #909399;
    font-size: 14px;
    margin-top: 5px;
}

/* 卡片通用样式 */
.premium-card {
    border: none;
    border-radius: 8px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.premium-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08) !important;
}

/* 顶部大卡片 */
.top-sections {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-bottom: 30px;
}

.strategy-section {
    margin-bottom: 30px;
}

.card-header-custom {
    display: flex;
    align-items: center;
    gap: 12px;
}

.header-icon {
    font-size: 20px;
    color: #409eff;
}

.badge {
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    color: #fff;
}

.type-def {
    background: #409eff;
}

.type-strat {
    background: #e6a23c;
}

.rule-badge {
    background: #67c23a;
}

.title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
}

.content-body {
    line-height: 1.8;
    color: #606266;
    font-size: 15px;
}

/* 网格布局 */
.group-label {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 30px 0 20px;
    color: #303133;
}

.grid-layout {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.sub-header {
    display: flex;
    align-items: center;
    gap: 10px;
}

.sub-title {
    font-weight: bold;
    color: #444;
}

.sub-content {
    font-size: 14px;
    color: #666;
    line-height: 1.6;
}

/* 表格定制化 */
.table-card :deep(.table-header) {
    background-color: #f5f7fa !important;
    color: #303133;
    font-weight: bold;
}

.support-cell {
    padding: 0 10px;
}
</style>