const path = require("path");
const webpack = require("webpack");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");

const config = {
  entry: __dirname + "/ledfx/frontend/index.jsx",
  module: {
    rules: [
      {
        test: /\.jsx?/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: ["@babel/preset-env"],
              plugins: [
                "@babel/plugin-proposal-class-properties",
                "@babel/plugin-transform-react-jsx",
                ["@babel/plugin-transform-spread", {
                  "loose": true
                }]
              ]
            }
          }
        ]
      },
      {
        test: /\.css$/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader
          },
          "css-loader"
        ]
      },
      {
        test: /\.(png|jpg|gif)$/,
        use: [
          {
            loader: "file-loader",
            options: {}
          }
        ]
      }
    ]
  },
  output: {
    path: __dirname + "/ledfx_frontend",
    publicPath: "/static/",
    filename: "bundle.js"
  },
  resolve: {
    extensions: [".js", ".jsx", ".css"],
    modules: [path.resolve("./ledfx"), path.resolve("./node_modules"), "node_modules"]
  },
  plugins: [
    new CopyWebpackPlugin([
      {from: 'ledfx/frontend/dist', to: __dirname + "/ledfx_frontend"}
    ]),
    new MiniCssExtractPlugin({
      filename: "style.css",
    })
  ]
};

module.exports = config;
