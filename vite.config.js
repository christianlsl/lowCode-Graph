import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { realpathSync } from 'node:fs'
import legacy from '@vitejs/plugin-legacy';

const rootDir = realpathSync(process.cwd())

export default defineConfig({
    root: rootDir,
    plugins: [
        vue(),
        legacy({
            targets: ['ie>=11'], // 支持旧版浏览器
            additionalLegacyPolyfills: ['regenerator-runtime/runtime']
        })
    ],
    base: './'
})
