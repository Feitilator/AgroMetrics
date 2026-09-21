import { useState } from "react";
import "./App.css"
import axios from "axios";
  
function App() {
  let hazard = ''
  const [data, setData] = useState({ 
    temperature_mean: "", 
    temperature_max: "", 
    temperature_min: "", 
    precipitation: "", 
    snowfall: "", 
    wind_speed_max: "", 
    wind_gusts_max: "", 
    et0: "", 
    dew_point: "", 
    humidity_mean: "", 
    humidity_min: "", 
    soil_moisture_0_7: "", 
    soil_moisture_7_28: "", 
    soil_moisture_28_100: "", 
    soil_temperature_0_7: "", 
    soil_temperature_7_28: "", 
    soil_temperature_28_100: "", 
    solar_radiation: "", 
    cloud_cover: "", 
    pressure: "", 
    month: "" 
  })

  const [alert, setAlert] = useState(false)

  const [prediciton, setPrediction] = useState({
    drought: "",
    sukhovey: "",
    early_snow: "",
    overall:""
  })

  const getRiskClass = (percent) => {
    if (percent >= 75) {
        return "risk-high"
    }

    if (percent >= 45) {
        return "risk-medium"
    }

    return "risk-low"
 }

  const handleChange = (event) =>{
    const {name, value} = event.target

    setData((prev) =>({
      ...prev,
      [name]: value
    }))
  }


  const handleSend = async (event) =>{
    event.preventDefault()

    try {

      const requestData = { 
        temperature_mean: Number(data.temperature_mean), 
        temperature_max: Number(data.temperature_max), 
        temperature_min: Number(data.temperature_min), 
        precipitation: Number(data.precipitation), 
        snowfall: Number(data.snowfall), 
        wind_speed_max: Number(data.wind_speed_max),
        wind_gusts_max: Number(data.wind_gusts_max), 
        et0: Number(data.et0), 
        dew_point: Number(data.dew_point), 
        humidity_mean: Number(data.humidity_mean), 
        humidity_min: Number(data.humidity_min), 
        soil_moisture_0_7: Number(data.soil_moisture_0_7), 
        soil_moisture_7_28: Number(data.soil_moisture_7_28), 
        soil_moisture_28_100: Number(data.soil_moisture_28_100), 
        soil_temperature_0_7: Number(data.soil_temperature_0_7), 
        soil_temperature_7_28: Number(data.soil_temperature_7_28), 
        soil_temperature_28_100: Number(data.soil_temperature_28_100), 
        solar_radiation: Number(data.solar_radiation), 
        cloud_cover: Number(data.cloud_cover), 
        pressure: Number(data.pressure), 
        month: Number(data.month) 
      }

      console.log("Отправляем:", requestData)
      const response = await axios.post("/api/agro-risk/predict",
        requestData,
      {
        headers: {
          "Content-Type": "application/json"
        }}
      )
      const result = response.data
      console.log("Ответ:", result)
      if(result.prediction.overall.hazard == "drought"){
        hazard = "Засуха"
      }
      setPrediction({
        drought: result.prediction.risk.drought,
        sukhovey: result.prediction.risk.sukhovey,
        early_snow: result.prediction.risk.early_snow,
        overall: hazard
      })
      setAlert(true)
    }catch(error){
      console.log("Ошибка", error)
      if (error.response) {
        console.log(
          `Ошибка сервера: ${
            error.response.data.error || "Неизвестная ошибка"
          }`
        )

      } else if (error.request) {
        console.log(
          "Не удалось подключиться к Node.js серверу"
        )
      } else {
        console.log(
          `Ошибка: ${error.message}`
        )
      }

    }
  }
      


  return (
    <div className="wrapper">
      <header className="header">
          <h1>AgroMetrics</h1>
      </header>
      <main>
        <section className="prediction">
          <form className="prediction__form" onSubmit={handleSend} >
            <div className="global__container">
              <div className="container1">
                <input type="number" placeholder="Средняя температура, °C." name="temperature_mean" value={data.temperature_mean} onChange={handleChange} required min={-40} max={45} />
                <input type="number" placeholder="Максимальная температура, °C." name="temperature_max" value={data.temperature_max} onChange={handleChange} required  min={-40} max={50} />
                <input type="number" placeholder="Минимальная температура, °C." name="temperature_min" value={data.temperature_min} onChange={handleChange} required  min={-50} max={40} />
                <input type="number" placeholder="Осадки, мм" name="precipitation" value={data.precipitation} onChange={handleChange} required  min={0} max={100} />
                <input type="number" placeholder="Снегопад, см" name="snowfall" value={data.snowfall} onChange={handleChange} required  min={0} max={50} />
                <input type="number" placeholder="Максимальная скорость ветра, км/ч" name="wind_speed_max" value={data.wind_speed_max} onChange={handleChange} required  min={0} max={150} />
                <input type="number" placeholder="Максимальные порывы ветра, км/ч" name="wind_gusts_max" value={data.wind_gusts_max} onChange={handleChange} required  min={0} max={200} />
                
              </div>
              <div className="container2">
                <input type="number" placeholder="ET0, мм" name="et0" value={data.et0} onChange={handleChange} required   min={0} max={15} />
                <input type="number" placeholder="Точка росы, °C" name="dew_point" value={data.dew_point} onChange={handleChange} required   min={-50} max={35} />
                <input type="number" placeholder="Средняя влажность, %" name="humidity_min" value={data.humidity_min} onChange={handleChange} required   min={0} max={100} />
                <input type="number" placeholder="Минимальная влажность, %." name="soil_moisture" value={data.soil_moisture} onChange={handleChange} required min={0} max={100} />
                <input type="number" placeholder="Влажность почвы 0–7 см" name="soil_moisture_0_7" value={data.soil_moisture_0_7} onChange={handleChange} required  min={0} max={1} step={0.001}/>
                <input type="number" placeholder="Влажность почвы 7–28 см" name="soil_moisture_7_28" value={data.soil_moisture_7_28} onChange={handleChange} required  min={0} max={1} step={0.001}/>
                <input type="number" placeholder="Влажность почвы 28–100 см" name="soil_moisture_28_100" value={data.soil_moisture_28_100} onChange={handleChange} required min={0} max={1} step={0.001}/>
              </div> 
              <div className="container3">
                <input type="number" placeholder="Температура почвы 0–7 см, °C" name="soil_temperature_0_7" value={data.soil_temperature_0_7} onChange={handleChange} required  min={-40} max={50} />
                <input type="number" placeholder="Температура почвы 7–28 см, °C" name="soil_temperature_7_28" value={data.soil_temperature_7_28} onChange={handleChange} required  min={-40} max={50} />
                <input type="number" placeholder="Температура почвы 28–100 см, °C" name="soil_temperature_28_100" value={data.soil_temperature_28_100} onChange={handleChange} required  min={-20} max={40} />
                <input type="number" placeholder="Солнечная радиация, MJ/m²" name="ssolar_radiation" value={data.ssolar_radiation} onChange={handleChange} required  min={0} max={40} />
                <input type="number" placeholder="Облачность, %" name="cloud_cover" value={data.cloud_cover} onChange={handleChange} required min={0} max={100} />
                <input type="number" placeholder="Давление, hPa" name="pressure" value={data.pressure} onChange={handleChange} required  min={850} max={1100} />
                <input type="number" placeholder="Месяц (1–12)" name="month" value={data.month} onChange={handleChange} required  min={1} max={12} />
               
              </div>
            </div>
            <button className="btn" type="submit">Отправить</button>
          </form>
        </section>
        {alert &&  
          <table>
              <thead>
                <tr>
                    <th>Опасность</th>
                    <th>Вероятность</th>
                    <th>Риск</th>
                </tr>
              </thead>  
            <tbody>
            <tr className={getRiskClass(prediciton.drought.probability_percent)}>
                <td>Засуха</td>
                <td>{prediciton.drought.probability_percent}%</td>
                <td>{prediciton.drought.risk}</td>
            </tr>

            <tr className={getRiskClass(prediciton.sukhovey.probability_percent)}>
                <td>Суховей</td>
                <td>{prediciton.sukhovey.probability_percent}%</td>
                <td>{prediciton.sukhovey.risk}</td>
            </tr>

            <tr className={getRiskClass(prediciton.early_snow.probability_percent)}>
                <td>Ранний снег</td>
                <td>{prediciton.early_snow.probability_percent}%</td>
                <td>{prediciton.early_snow.risk}</td>
            </tr>
          </tbody>
        </table>
      }
      </main>
    </div>
  )
}

export default App