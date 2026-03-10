const palette = [
    '#2563eb', '#10b981', '#f59e0b', '#7c3aed', '#ef4444',
    '#06b6d4', '#ec4899', '#84cc16', '#6366f1', '#f97316',
    '#0ea5e9', '#f43f5e', '#34d399', '#a855f7', '#eab308',
    '#1e40af', '#065f46', '#9a3412', '#9d174d', '#334155',
    '#60a5fa', '#fb7185', '#4ade80', '#c084fc', '#d97706'
]

const hashString = (value) => {
    let hash = 0
    for (let index = 0; index < value.length; index += 1) {
        hash = (hash << 5) - hash + value.charCodeAt(index)
        hash |= 0
    }
    return Math.abs(hash)
}

const createTypeVisualMap = (categories) => {
    const map = new Map()
    categories.forEach((item, index) => {
        const hash = hashString(item.name)
        map.set(item.name, {
            color: palette[hash % palette.length],
            size: 46 + ((hash + index) % 7) * 4
        })
    })
    return map
}

export const buildGraphOption = (payload) => {
    const categories = (payload.categories || []).map((name) => ({ name }))
    const typeVisualMap = createTypeVisualMap(categories)

    categories.forEach((category) => {
        category.itemStyle = {
            color: typeVisualMap.get(category.name)?.color || '#334155'
        }
    })

    const data = (payload.nodes || []).map((node) => ({
        id: String(node.id),
        name: node.display_name,
        category: categories.findIndex((item) => item.name === node.type_name),
        symbolSize: typeVisualMap.get(node.type_name)?.size || 48,
        itemStyle: {
            color: typeVisualMap.get(node.type_name)?.color || '#334155'
        },
        value: node.tooltip || []
    }))

    const links = (payload.edges || []).map((edge) => ({
        source: String(edge.source),
        target: String(edge.target),
        value: edge.tooltip || [],
        lineStyle: {
            width: edge.relation === 'ser_invoke' ? 3 : 2,
            opacity: 0.86,
            curveness: 0.18
        },
        label: {
            show: true,
            formatter: edge.relation,
            color: '#475569',
            fontSize: 11
        }
    }))

    return {
        animationDuration: 600,
        tooltip: {
            confine: true,
            formatter(params) {
                const lines = Array.isArray(params.data?.value) ? params.data.value : []
                return lines.length ? lines.join('<br/>') : (params.name || '')
            }
        },
        legend: [{ type: 'scroll', orient: 'horizontal', top: 8, data: categories.map((item) => item.name) }],
        series: [{
            type: 'graph',
            layout: 'force',
            roam: true,
            draggable: true,
            categories,
            data,
            links,
            edgeSymbol: ['none', 'arrow'],
            edgeSymbolSize: [4, 10],
            label: { show: true, position: 'top', fontSize: 12, color: '#0f172a' },
            force: { repulsion: 280, edgeLength: [90, 180], gravity: 0.08 }
        }]
    }
}
