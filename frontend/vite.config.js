import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api/, ''),
				configure: (proxy, _options) => {
					proxy.on('error', (err, _req, _res) => {
						console.log('proxy error', err);
					});
					proxy.on('proxyReq', (proxyReq, req, _res) => {
						console.log('Enviando requisição para:', req.url);
					});
					proxy.on('proxyRes', (proxyRes, req, _res) => {
						console.log('Recebida resposta de:', req.url, 'status:', proxyRes.statusCode);
					});
				}
			},
			'/upload-api': {
				target: 'http://localhost:8001',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/upload-api/, ''),
				configure: (proxy, _options) => {
					proxy.on('error', (err, _req, _res) => {
						console.log('proxy error', err);
					});
				}
			}
		}
	}
});
