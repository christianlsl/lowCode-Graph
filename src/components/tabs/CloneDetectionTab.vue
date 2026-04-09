<template>
    <div class="clone-detection-tab">
        <el-card class="panel-card summary-card" shadow="hover">
            <template #header>
                <div class="card-header">JS 脚本相似函数概览</div>
            </template>

            <div class="summary-grid">
                <div v-for="item in summaryCards" :key="item.label" class="summary-item">
                    <div class="summary-label">{{ item.label }}</div>
                    <div class="summary-value">{{ item.value }}</div>
                </div>
            </div>
        </el-card>

        <el-card class="panel-card" shadow="hover">
            <template #header>
                <div class="card-header with-filter">
                    <span>克隆检测结果</span>
                    <el-input v-model="searchKeyword" clearable placeholder="搜索文件路径、代码片段、项目名或 cluster 信息"
                        class="search-input" />
                </div>
            </template>

            <el-table :data="filteredGroups" border max-height="38vh" row-key="group_key" highlight-current-row>
                <el-table-column label="组号" width="90" align="center">
                    <template #default="scope">
                        {{ scope.row.group_index }}
                    </template>
                </el-table-column>
                <el-table-column label="涉及工程" min-width="180">
                    <template #default="scope">
                        <div class="tag-list">
                            <el-tag v-for="project in scope.row.projects" :key="project" size="small" effect="plain">
                                {{ project }}
                            </el-tag>
                            <span v-if="!scope.row.projects.length">-</span>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column label="文件路径" min-width="260" show-overflow-tooltip>
                    <template #default="scope">
                        {{ scope.row.filePaths.length ? scope.row.filePaths.join(' / ') : '-' }}
                    </template>
                </el-table-column>
                <el-table-column label="相似度范围" width="140" align="center">
                    <template #default="scope">
                        {{ scope.row.similarityRange }}
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <section class="detail-section">
            <div class="section-title">克隆组详情</div>

            <el-card v-for="group in filteredGroups" :key="group.group_key" class="panel-card detail-card"
                shadow="hover">
                <template #header>
                    <div class="card-header detail-header">
                        <span>相似函数组 {{ group.group_index }}</span>
                        <el-tag type="info" effect="plain" round>
                            {{ group.func_group.length }} 个函数，{{ group.pair_similarity.length }} 个相似对
                        </el-tag>
                    </div>
                </template>

                <el-descriptions :column="1" border class="detail-descriptions">
                    <el-descriptions-item label="涉及工程">
                        <div class="tag-list">
                            <el-tag v-for="project in group.projects" :key="project" size="small" effect="plain">
                                {{ project }}
                            </el-tag>
                            <span v-if="!group.projects.length">-</span>
                        </div>
                    </el-descriptions-item>
                    <el-descriptions-item label="文件路径">
                        <div class="file-list">
                            <div v-for="filePath in group.filePaths" :key="filePath" class="file-item">{{ filePath }}
                            </div>
                            <span v-if="!group.filePaths.length">-</span>
                        </div>
                    </el-descriptions-item>
                    <el-descriptions-item label="相似度列表">
                        <div class="tag-list">
                            <el-tag v-for="similarity in group.pairSimilarityLabels" :key="similarity.key" size="small"
                                type="success">
                                {{ similarity.label }}
                            </el-tag>
                            <span v-if="!group.pairSimilarityLabels.length">-</span>
                        </div>
                    </el-descriptions-item>
                </el-descriptions>

                <div class="subsection-title">函数片段</div>
                <div class="function-list">
                    <el-card v-for="func in group.func_group" :key="func.record_key" class="function-card"
                        shadow="never">
                        <template #header>
                            <div class="function-header">
                                <span>{{ func.file_path }}</span>
                                <div class="function-header-actions">
                                    <el-tag size="small" type="info" effect="plain">
                                        {{ func.start_line }} - {{ func.end_line }}
                                    </el-tag>
                                    <el-button type="primary" link @click="toggleCode(func.record_key)">
                                        {{ isCodeExpanded(func.record_key) ? '收起' : '展开' }}
                                    </el-button>
                                </div>
                            </div>
                        </template>

                        <pre v-if="isCodeExpanded(func.record_key)" class="code-block"><code class="hljs language-javascript" v-html="func.highlighted_code"></code></pre>
                    </el-card>
                </div>

                <div class="subsection-title">相似对明细</div>
                <el-table :data="group.pair_similarity_parsed" border size="small" max-height="280">
                    <el-table-column type="index" label="序号" width="70" align="center" />
                    <el-table-column label="函数A文件路径" min-width="260" show-overflow-tooltip>
                        <template #default="scope">
                            <span>{{ scope.row.left.file_path || '-' }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="函数A行号" width="140" align="center">
                        <template #default="scope">
                            <span>{{ formatLineRange(scope.row.left.start_line, scope.row.left.end_line) }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="函数B文件路径" min-width="260" show-overflow-tooltip>
                        <template #default="scope">
                            <span>{{ scope.row.right.file_path || '-' }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="函数B行号" width="140" align="center">
                        <template #default="scope">
                            <span>{{ formatLineRange(scope.row.right.start_line, scope.row.right.end_line) }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="相似度" width="120" align="center">
                        <template #default="scope">
                            {{ formatSimilarity(scope.row.similarity) }}
                        </template>
                    </el-table-column>
                </el-table>
            </el-card>
        </section>

        <el-empty v-if="!filteredGroups.length" description="未找到匹配的 JS 脚本相似函数结果" />
    </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import cloneDetectionResult from '../../../data/clone_detection_result.json'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import 'highlight.js/styles/github-dark.css'

hljs.registerLanguage('javascript', javascript)

const searchKeyword = ref('')
const expandedCodeMap = ref({})

const normalizedGroups = computed(() => {
    return (Array.isArray(cloneDetectionResult) ? cloneDetectionResult : []).map((group, index) => {
        const funcGroup = Array.isArray(group.func_group) ? group.func_group : []
        const pairSimilarity = Array.isArray(group.pair_similarity) ? group.pair_similarity : []
        const projects = Array.isArray(group.relevent_projects) ? group.relevent_projects : []

        const normalizedFuncGroup = funcGroup.map((item, funcIndex) => ({
            ...item,
            record_key: `${index}-${funcIndex}-${item.file_path || 'unknown'}`,
            highlighted_code: highlightJsCode(item.code)
        }))

        const filePaths = normalizedFuncGroup.map((item) => item.file_path).filter(Boolean)
        const similarityValues = pairSimilarity
            .map((item) => Number(item?.similarity))
            .filter((value) => Number.isFinite(value))
        const pairSimilarityParsed = pairSimilarity.map((item, pairIndex) => {
            const leftRaw = Array.isArray(item?.index_pair) ? item.index_pair[0] : ''
            const rightRaw = Array.isArray(item?.index_pair) ? item.index_pair[1] : ''

            return {
                key: `${index}-${pairIndex}`,
                similarity: item?.similarity,
                left: parseIndexPairItem(leftRaw),
                right: parseIndexPairItem(rightRaw)
            }
        })

        return {
            ...group,
            group_index: index + 1,
            group_key: `clone-group-${index}`,
            func_group: normalizedFuncGroup,
            pair_similarity: pairSimilarity,
            pair_similarity_parsed: pairSimilarityParsed,
            projects,
            filePaths,
            pairSimilarityLabels: pairSimilarity.map((item, pairIndex) => ({
                key: `${index}-${pairIndex}-${item?.similarity ?? 'na'}`,
                label: formatSimilarity(item?.similarity)
            })),
            similarityRange: similarityValues.length
                ? `${formatSimilarity(Math.min(...similarityValues))} ~ ${formatSimilarity(Math.max(...similarityValues))}`
                : '-'
        }
    })
})

const filteredGroups = computed(() => {
    const keyword = searchKeyword.value.trim().toLowerCase()
    if (!keyword) return normalizedGroups.value

    return normalizedGroups.value.filter((group) => {
        const haystack = [
            group.projects.join(' '),
            group.filePaths.join(' '),
            group.func_group.map((item) => item.code || '').join(' '),
            group.pair_similarity.map((item) => item.index_pair?.join(' ') || '').join(' '),
            group.pair_similarity.map((item) => String(item?.similarity ?? '')).join(' ')
        ]
            .join(' ')
            .toLowerCase()

        return haystack.includes(keyword)
    })
})

const summaryCards = computed(() => {
    const totalGroups = normalizedGroups.value.length
    const uniqueProjects = new Set()

    for (const group of normalizedGroups.value) {
        for (const project of group.projects) {
            uniqueProjects.add(project)
        }
    }

    return [
        { label: '克隆组数量', value: totalGroups },
        { label: '涉及工程个数', value: uniqueProjects.size }
    ]
})

function parseIndexPairItem(value) {
    const text = String(value || '')
    const match = text.match(/^(.*)_(\d+)_(\d+)$/)

    if (!match) {
        return {
            raw: text,
            file_path: text,
            start_line: null,
            end_line: null
        }
    }

    return {
        raw: text,
        file_path: match[1],
        start_line: Number(match[2]),
        end_line: Number(match[3])
    }
}

function formatLineRange(startLine, endLine) {
    if (!Number.isFinite(startLine) || !Number.isFinite(endLine)) return '-'
    return `${startLine} - ${endLine}`
}

function isCodeExpanded(recordKey) {
    return !!expandedCodeMap.value[recordKey]
}

function toggleCode(recordKey) {
    expandedCodeMap.value = {
        ...expandedCodeMap.value,
        [recordKey]: !expandedCodeMap.value[recordKey]
    }
}

function highlightJsCode(code) {
    const source = String(code || '')
    if (!source) return ''

    return hljs.highlight(source, { language: 'javascript' }).value
}

function formatSimilarity(value) {
    const num = Number(value)
    if (!Number.isFinite(num)) return '-'
    return `${(num * 100).toFixed(2)}%`
}
</script>

<style scoped>
.clone-detection-tab {
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

.search-input {
    width: 340px;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.summary-item {
    padding: 16px;
    border-radius: 12px;
    background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%);
    border: 1px solid #dbeafe;
}

.summary-label {
    color: #64748b;
    font-size: 13px;
    margin-bottom: 8px;
}

.summary-value {
    color: #0f172a;
    font-size: 28px;
    font-weight: 800;
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

.detail-card {
    overflow: hidden;
}

.detail-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.detail-descriptions {
    margin-bottom: 16px;
}

.detail-descriptions :deep(.el-descriptions__label) {
    font-weight: 700;
}

.tag-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.file-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.file-item {
    color: #334155;
    word-break: break-all;
}

.subsection-title {
    margin: 12px 0 10px;
    color: #0f172a;
    font-size: 16px;
    font-weight: 700;
}

.function-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
}

.function-card {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}

.function-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    font-weight: 600;
    color: #0f172a;
}

.function-header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.code-block {
    margin: 0;
    padding: 14px;
    border-radius: 10px;
    background: #0f172a;
    color: #e2e8f0;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-x: auto;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    line-height: 1.5;
    font-size: 12px;
}

@media (max-width: 1200px) {
    .summary-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 992px) {
    .with-filter {
        flex-direction: column;
        align-items: flex-start;
    }

    .search-input {
        width: 100%;
    }

    .summary-grid {
        grid-template-columns: 1fr;
    }

    .detail-header,
    .function-header {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>