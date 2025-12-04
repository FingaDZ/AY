import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts: ['hgd09pzcrcm.sn.mynetname.net', '192.168.20.53', 'localhost'],
  },
  preview: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts: ['hgd09pzcrcm.sn.mynetname.net', '192.168.20.53', 'localhost'],
  },
})
