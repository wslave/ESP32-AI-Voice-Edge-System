const { defineConfig } = require('@vue/cli-service');
const dotenv = require('dotenv');
const TerserPlugin = require('terser-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const { InjectManifest } = require('workbox-webpack-plugin');
const path = require('path');

dotenv.config();

const cdnResources = {
  css: [
    'https://unpkg.com/element-ui@2.15.14/lib/theme-chalk/index.css',
    'https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css'
  ],
  js: [
    'https://unpkg.com/vue@2.6.14/dist/vue.min.js',
    'https://unpkg.com/vue-router@3.6.5/dist/vue-router.min.js',
    'https://unpkg.com/vuex@3.6.2/dist/vuex.min.js',
    'https://unpkg.com/element-ui@2.15.14/lib/index.js',
    'https://unpkg.com/axios@0.27.2/dist/axios.min.js',
    'https://unpkg.com/opus-decoder@0.7.7/dist/opus-decoder.min.js'
  ]
};

const useCDN = process.env.VUE_APP_USE_CDN === 'true';

module.exports = defineConfig({
  productionSourceMap: process.env.NODE_ENV !== 'production',
  devServer: {
    port: 8001,
    proxy: {
      '/xiaozhi': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true
      }
    },
    client: {
      overlay: false
    }
  },
  publicPath: process.env.VUE_APP_PUBLIC_PATH || '/',
  chainWebpack: config => {
    config.plugin('html').tap(args => {
      if (process.env.NODE_ENV === 'production' && useCDN) {
        args[0].cdn = cdnResources;
      }
      return args;
    });

    config.optimization.splitChunks({
      chunks: 'all',
      minSize: 20000,
      maxSize: 250000,
      cacheGroups: {
        vendors: {
          name: 'chunk-vendors',
          test: /[\\/]node_modules[\\/]/,
          priority: -10,
          chunks: 'initial'
        },
        common: {
          name: 'chunk-common',
          minChunks: 2,
          priority: -20,
          chunks: 'initial',
          reuseExistingChunk: true
        }
      }
    });

    config.optimization.usedExports(true);
    config.optimization.concatenateModules(true);
    config.optimization.minimize(true);
  },
  configureWebpack: config => {
    if (process.env.NODE_ENV === 'production') {
      config.optimization = {
        minimize: true,
        minimizer: [
          new TerserPlugin({
            parallel: true,
            terserOptions: {
              compress: {
                drop_console: true,
                drop_debugger: true,
                pure_funcs: ['console.log']
              }
            }
          })
        ]
      };

      config.plugins.push(
        new CompressionPlugin({
          algorithm: 'gzip',
          test: /\.(js|css|html|svg)$/,
          threshold: 20480,
          minRatio: 0.8
        })
      );

      config.plugins.push(
        new InjectManifest({
          swSrc: path.resolve(__dirname, 'src/service-worker.js'),
          swDest: 'service-worker.js',
          exclude: [/\.map$/, /asset-manifest\.json$/],
          maximumFileSizeToCacheInBytes: 5 * 1024 * 1024,
          injectionPoint: 'self.__WB_MANIFEST',
          additionalManifestEntries: useCDN
            ? [{ url: 'cdn-mode', revision: 'enabled' }]
            : [{ url: 'cdn-mode', revision: 'disabled' }]
        })
      );

      config.externals = useCDN
        ? {
            vue: 'Vue',
            'vue-router': 'VueRouter',
            vuex: 'Vuex',
            'element-ui': 'ELEMENT',
            axios: 'axios',
            'opus-decoder': 'OpusDecoder'
          }
        : {};

      if (process.env.ANALYZE === 'true') {
        config.plugins.push(
          new BundleAnalyzerPlugin({
            analyzerMode: 'server',
            openAnalyzer: true,
            analyzerPort: 8888
          })
        );
      }

      config.cache = {
        type: 'filesystem',
        cacheDirectory: path.resolve(__dirname, '.webpack_cache'),
        allowCollectingMemory: true,
        compression: 'gzip',
        maxAge: 5184000000,
        buildDependencies: {
          config: [__filename]
        }
      };
    }
  },
  pwa: {
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true
    }
  }
});
