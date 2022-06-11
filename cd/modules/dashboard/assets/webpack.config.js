const path = require("path");

const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CopyPlugin = require("copy-webpack-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");


module.exports = (env, options) => {

    const isDevMode = options.mode === "development"

    return {
        entry: {
            app: "./js/app.js",
            websocket: "./js/websocket.js"
        },

        module: {
            rules: [
                {
                    test: /\.m?js$/,
                    exclude: /node_modules/,
                    use: {
                        loader: "babel-loader",
                    }
                },
                {
                    test: /\.(sa|sc|c)ss$/,
                    use: [
                        isDevMode ? "style-loader" : MiniCssExtractPlugin.loader,
                        "css-loader",
                        "postcss-loader",
                        "sass-loader"
                    ]
                }
            ]
        },

        output: {
            filename: `[name].${isDevMode ? "" : "[contenthash]."}bundle.js`,
            path: path.resolve(__dirname, "../static/js"),
            publicPath: "/js/"
        },

        plugins: [
            new CopyPlugin({
                    patterns: [
                        {
                            from: "images/",
                            to: "../images"
                        },
                    ]
                }
            ),
            ...(isDevMode ? [] : [new MiniCssExtractPlugin()])
        ],


        optimization: {
            minimizer: [
                new CssMinimizerPlugin()
            ]
        },

    }
}
