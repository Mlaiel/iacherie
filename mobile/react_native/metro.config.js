/**
 * Metro configuration for React Native
 * Ainflue Professional Content Creation Platform
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

const {getDefaultConfig, mergeConfig} = require('@react-native/metro-config');

const defaultConfig = getDefaultConfig(__dirname);

const config = {
  transformer: {
    babelTransformerPath: require.resolve('react-native-svg-transformer'),
    getTransformOptions: async () => ({
      transform: {
        experimentalImportSupport: false,
        inlineRequires: true,
      },
    }),
  },
  resolver: {
    assetExts: defaultConfig.resolver.assetExts.filter(ext => ext !== 'svg'),
    sourceExts: [...defaultConfig.resolver.sourceExts, 'svg'],
    alias: {
      '@': './src',
      '@components': './src/components',
      '@services': './src/services',
      '@utils': './src/utils',
      '@assets': './src/assets',
      '@types': './src/types',
    },
  },
};

module.exports = mergeConfig(defaultConfig, config);