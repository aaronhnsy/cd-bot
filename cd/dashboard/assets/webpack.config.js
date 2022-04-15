const path = require("path");
const glob = require("glob");

const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");


module.exports = (env, options) => {

    const devMode = options.mode !== "production";

    return {
        optimization: {
            minimizer: [
                new TerserPlugin(),
                new CssMinimizerPlugin(),
            ],
        },

        entry: {
            app: "./js/app.js",
            websocket: "./js/websocket.js",
        },

        output: {
            path: path.resolve(__dirname, "../static/js"),
            filename: "[name].js",
            publicPath: "/js/",
        },

        devtool: devMode ? "eval-cheap-module-source-map" : undefined,

        module: {
            rules: [
                {
                    test: /\.m?js$/,
                    exclude: /node_modules/,
                    use: {
                        loader: "babel-loader",
                    },
                },
                {
                    test: /\.s?css$/i,
                    use: [
                        MiniCssExtractPlugin.loader,
                        "css-loader",
                        "sass-loader",
                    ],
                },
            ],
        },

        plugins: [
            new MiniCssExtractPlugin({
                filename: "../css/app.css",
            }),
            new CopyWebpackPlugin({
                patterns: [
                    {
                        from: "images/",
                        to: "../images",
                    },
                ],
            }),
        ],
    };
};
