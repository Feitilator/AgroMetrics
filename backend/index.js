const cors = require("cors")
const axios = require("axios")
const express = require("express")
require("dotenv").config()

const app = express()
app.use(express.urlencoded({extended: true}))
app.use(express.json())

app.use(
    cors({
        origin: process.env.FRONTEND_URL
    })
)


const FEATURES = [
    "temperature_mean",
    "temperature_max",
    "temperature_min",
    "precipitation",
    "snowfall",
    "wind_speed_max",
    "wind_gusts_max",
    "et0",
    "dew_point",
    "humidity_mean",
    "humidity_min",
    "soil_moisture_0_7",
    "soil_moisture_7_28",
    "soil_moisture_28_100",
    "soil_temperature_0_7",
    "soil_temperature_7_28",
    "soil_temperature_28_100",
    "solar_radiation",
    "cloud_cover",
    "pressure",
    "month"
]


const mlApi = axios.create({
    baseURL: process.env.ML_API_URL,
    timeout: process.env.ML_TIMEOUT,

    headers: {
        "Content-Type": "application/json"
    }
})


app.post("/api/agro-risk/predict", async (req, res) => {
    try {
        const data = req.body
        if (
            !data ||
            typeof data !== "object" ||
            Array.isArray(data)
        ) {
            return res.status(400).json({
                success: false,
                error: "Тело запроса должно быть объектом"
            })
        }

        const missing = []

        for (const name of FEATURES) {

            if (
                data[name] === undefined ||
                data[name] === null
            ) {
                missing.push(name)
            }

        }

        if (missing.length > 0) {

            return res.status(400).json({
                success: false,
                error: "Не хватает признаков",
                missing,
                expected_features: FEATURES
            })

        }

        const invalid = []

        for (const name of FEATURES) {

            const value = data[name]

            if (
                typeof value !== "number" ||
                !Number.isFinite(value)
            ) {
                invalid.push({
                    feature: name,
                    value
                })
            }

        }

        if (invalid.length > 0) {

            return res.status(400).json({
                success: false,
                error: "Некоторые признаки должны быть числами",
                invalid
            })

        }

        const response = await mlApi.post(
            "/risk",
            data
        )

        return res.json({
            success: true,
            prediction: response.data
        })

    } catch (error) {
        console.log(
            "Prediction error:",
            error.message
        )
        if (error.response) {

            return res.status(error.response.status).json({
                success: false,
                error: "Python ML API вернул ошибку",
                details: error.response.data
            })

        }
        if (error.code === "ECONNREFUSED") {

            return res.status(503).json({
                success: false,
                error: "Python ML API недоступен",
                details:
                    `Проверьте ${process.env.ML_API_URL}`
            })

        }

        if (error.code === "ECONNABORTED") {

            return res.status(504).json({
                success: false,
                error: "Python ML API не ответил вовремя"
            })

        }

        return res.status(500).json({
            success: false,
            error: "Ошибка при обработке запроса",
            details: error.message
        })
    }
})


app.listen(process.env.PORT, "0.0.0.0", () => {
        console.log(`Express запущен: http://localhost:${process.env.PORT}`)
    }
)