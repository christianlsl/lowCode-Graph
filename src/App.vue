<template>
    <el-container class="page">
        <el-header class="header">低代码数字孪生关系图</el-header>
        <el-main>
            <el-card>
                <template #header>
                    <div class="card-header">ECharts Graph 示例</div>
                </template>
                <div ref="chartRef" class="graph-canvas"></div>
            </el-card>
        </el-main>
    </el-container>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null)
let chartInstance = null

const nodes = [
    { id: '1', name: '页面', category: 0, symbolSize: 68 },
    { id: '2', name: '组件', category: 1, symbolSize: 56 },
    { id: '3', name: '数据源', category: 2, symbolSize: 52 },
    { id: '4', name: 'API', category: 2, symbolSize: 48 },
    { id: '5', name: '权限', category: 3, symbolSize: 44 },
    { id: '6', name: '用户', category: 3, symbolSize: 46 }
]

const links = [
    { source: '1', target: '2' },
    { source: '2', target: '3' },
    { source: '3', target: '4' },
    { source: '1', target: '5' },
    { source: '5', target: '6' },
    { source: '6', target: '1' }
]

const categories = [
    { name: 'UI' },
    { name: '组件层' },
    { name: '数据层' },
    { name: '安全层' }
]

const renderChart = () => {
    if (!chartRef.value) return
    chartInstance = echarts.init(chartRef.value)

    chartInstance.setOption({
        tooltip: {},
        legend: [{ data: categories.map((c) => c.name) }],
        series: [
            {
                type: 'graph',
                layout: 'force',
                roam: true,
                draggable: true,
                label: {
                    show: true,
                    position: 'right'
                },
                edgeSymbol: ['none', 'arrow'],
                edgeSymbolSize: [4, 10],
                force: {
                    repulsion: 220,
                    edgeLength: [70, 130]
                },
                lineStyle: {
                    opacity: 0.8,
                    width: 2,
                    curveness: 0.2
                },
                categories,
                data: nodes,
                links
            }
        ]
    })
}

const handleResize = () => {
    if (chartInstance) chartInstance.resize()
}

onMounted(() => {
    renderChart()
    window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
    if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
    }
})
</script>

<style scoped>
.page {
    min-height: 100vh;
    background: linear-gradient(180deg, #f3f8ff 0%, #eef3f9 100%);
}

.header {
    display: flex;
    align-items: center;
    font-size: 20px;
    font-weight: 600;
}

.card-header {
    font-weight: 600;
}

.graph-canvas {
    width: 100%;
    height: 68vh;
}
</style>
