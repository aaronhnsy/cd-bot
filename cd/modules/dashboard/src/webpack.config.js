const path = require("path");

const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CopyPlugin = require("copy-webpack-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");


module.exports = {

    entry: {
        app: "./js/app.js",
        websocket: "./js/websocket.js"
    },

    output: {
        filename: "[name].bundle.js",
        path: path.resolve(__dirname, "../static"),
    },

    module: {
        rules: [
            {
                test: /\.m?js$/,
                exclude: /node_modules/,
                use: [
                    "babel-loader",
                ]
            },
            {
                test: /\.(sa|sc|c)ss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    "css-loader",
                    "postcss-loader",
                    "sass-loader",
                ]
            }
        ]
    },

    plugins: [
        new CopyPlugin({
                patterns: [
                    {from: "images/", to: "images/"},
                ]
            }
        ),
        new MiniCssExtractPlugin(),
    ],

    optimization: {
        minimizer: [
            `...`,
            new CssMinimizerPlugin()
        ]
    },

}
