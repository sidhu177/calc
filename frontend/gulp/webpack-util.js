const path = require('path');
const webpackStream = require('webpack-stream');
const webpack = require('webpack');

const USE_POLLING = 'USE_POLLING' in process.env;

exports.scriptSources = ({ bundles, rootDir }) =>
  Object.keys(bundles).map((name) => {
    const options = bundles[name];
    const dirName = options.dirName || name;
    return path.join(rootDir, dirName, 'index.js');
  });

exports.getLastFolderName = (file) => {
  // All of our bundle entry files are of the form  "/some/path/index.js".
  // We'll use the last folder name to generate the file name of the
  // bundles (ie, "path.js") so that they're not all called "index.js".
  const parts = file.path.split(path.sep);
  const lastFolderName = parts[parts.length - 2];

  return lastFolderName;
};

exports.webpackify = ({ isWatching, isProd }) => {
  const plugins = [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': isProd ? '"production"' : '""',
    }),
  ];

  if (isProd) {
    plugins.push(new webpack.optimize.UglifyJsPlugin({
      sourceMap: true,
    }));
  }

  return webpackStream({
    watch: isWatching,
    watchOptions: USE_POLLING ? {
      aggregateTimeout: 300,
      poll: 500,
    } : {},
    resolve: {
      extensions: ['.js', '.jsx'],
    },
    context: path.normalize(path.join(__dirname, '..', '..')),
    node: {
      __filename: true,
    },
    devtool: isProd ? 'source-map' : 'eval-source-map',
    module: {
      rules: [
        {
          test: /\.jsx?$/,
          exclude: /node_modules/,
          loader: 'babel-loader',
          options: {
            presets: ['es2015', 'react'],
            cacheDirectory: true,
          },
        },
      ],
    },
    plugins,
  }, webpack);
};
