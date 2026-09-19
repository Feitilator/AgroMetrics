const cors = require('cors')
const axios = require('axios')
const express = require('express')
const app = express()
require('dotenv').config()




app.use(express.json())

app.use(cors({
    origin:process.env.FRONTEND_URL
}))
const FEATURES = [
    "t_mean",
    "t_max",
    "t_min",

    "rh_mean",
    "rh_min",

    "vpd_mean",
    "vpd_max",

    "precip",
    "rain",
    "snowfall",

    "wind_mean",
    "wind_max",
    "wind_gust_max",

    "soil_moisture",
    "soil_temperature",

    "precip_7d",
    "precip_14d",
    "precip_30d",

    "dry_days_7d",
    "dry_days_14d",
    "dry_days_30d",

    "hot_days_7d",
    "hot_days_14d",
    "hot_days_30d",

    "sukhovei_days_7d",
    "sukhovei_days_14d",
    "sukhovei_days_30d",

    "wind_mean_7d",
    "wind_max_7d",

    "vpd_mean_7d",
    "vpd_max_7d",

    "soil_moisture_7d",
    "soil_moisture_14d",
    "soil_moisture_30d",

    "snowfall_7d",
    "snowfall_14d"
]

const mlApi = axios.create({
    baseURL: process.env.ML_API_URL,
    timeout: 30000,
    
    headers: {
        "Content-Type": "application/json"
    }
})

app.post(
    "/api/agro-risk/predict",
    async (req, res) => {

        try {

            const {
                field_id,
                latitude,
                longitude,
                date,
                features
            } = req.body 
            if (
                !features ||
                typeof features !== "object"||
                Array.isArray(features)
            ){
                return res.status(400).json({
                    success: false,
                    error: 
                    "features должен быть обЪектом"
                })
            }const missing = []

            for(const name of FEATURES) {
                if (
                    features[name] === undefined ||
                    features[name] === null
                ){
                    missing.push(name)

                }

                
            }
            if(missing.length > 0 ) {
                return res.status(400).json({
                    success: false,

                    error:
                    "Не хватает признаков",
                    missing,
                    expected_features:
                    FEATURES
                })
            }
            const invalid = []
            for (const name of FEATURES) {

                const value = 
                features[name]

                if (
                    typeof value !== "number" ||
                    !Number.isFinite(value)
                ){
                    invalid.push({
                        feature: name,
                        value
                    })
                }
            }
            if (invalid.length > 0){
                return res.status(400).json({
                    success: false,
                    error: "Некоторые признаки должны быть числами",
                    invalid
                })
            }
            const response = await mlApi.post(
                "/predict",
                {
                    field_id: field_id ?? null,
                    latitude: latitude ?? null,
                    longitude: longitude ?? null,
                    date: date ?? null,

                    ...features
                }
            )
            return res.json({
                success: true,
                field_id: field_id ?? null,
                prediction: response.data
            })

        }catch(error){
            console.log(
                "Prediction error:",
                error.message
            )
            if (error.response){
                return res.status(error.response.status).json({
                    success: false,
                    error: "Python ml Api вернул ошибку",
                    details: error.response.data
                })
            }
            if (error.code === "ECONNREFUSED") {

                return res.status(503).json({

                    success: false,

                    error:
                        "Python ML API недоступен",

                    details:
                        `Проверьте ${procces.env.ML_API_URL}`

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
                error:
                    "Ошибка при обработке запроса",

                details: error.message
            })
        }
    }
)



app.listen(process.env.PORT,"0.0.0.0",()=>{
    console.log(`http://localhost:${process.env.PORT}`)
})



