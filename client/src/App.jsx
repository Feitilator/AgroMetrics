import { useState } from "react";
import "./App.css"
import axios from "axios";

function App() {
  const [data, setData] = useState({
    latitude: "",
    longitude: "",
    date: "",

    t_mean: "",
    t_max: "",
    t_min: "",

    rh_mean: "",
    rh_min: "",

    vpd_mean: "",
    vpd_max: "",

    precip: "",
    rain: "",
    snowfall: "",

    wind_mean: "",
    wind_max: "",
    wind_gust_max: "",

    soil_moisture: "",
    soil_temperature: "",

    precip_7d: "",
    precip_14d: "",
    precip_30d: "",

    dry_days_7d: "",
    dry_days_14d: "",
    dry_days_30d: "",

    hot_days_7d: "",
    hot_days_14d: "",
    hot_days_30d: "",

    sukhovei_days_7d: "",
    sukhovei_days_14d: "",
    sukhovei_days_30d: "",

    wind_mean_7d: "",
    wind_max_7d: "",

    vpd_mean_7d: "",
    vpd_max_7d: "",

    soil_moisture_7d: "",
    soil_moisture_14d: "",
    soil_moisture_30d: "",

    snowfall_7d: "",
    snowfall_14d: ""
  })

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
        field_id: "react-field-001",

        latitude: Number(data.latitude),
        longitude: Number(data.longitude),

        date: data.date,

        features: {

          t_mean: Number(data.t_mean),
          t_max: Number(data.t_max),
          t_min: Number(data.t_min),

          rh_mean: Number(data.rh_mean),
          rh_min: Number(data.rh_min),

          vpd_mean: Number(data.vpd_mean),
          vpd_max: Number(data.vpd_max),

          precip: Number(data.precip),
          rain: Number(data.rain),
          snowfall: Number(data.snowfall),

          wind_mean: Number(data.wind_mean),
          wind_max: Number(data.wind_max),
          wind_gust_max: Number(data.wind_gust_max),

          soil_moisture: Number(data.soil_moisture),
          soil_temperature: Number(data.soil_temperature),

          precip_7d: Number(data.precip_7d),
          precip_14d: Number(data.precip_14d),
          precip_30d: Number(data.precip_30d),

          dry_days_7d: Number(data.dry_days_7d),
          dry_days_14d: Number(data.dry_days_14d),
          dry_days_30d: Number(data.dry_days_30d),

          hot_days_7d: Number(data.hot_days_7d),
          hot_days_14d: Number(data.hot_days_14d),
          hot_days_30d: Number(data.hot_days_30d),

          sukhovei_days_7d: Number(data.sukhovei_days_7d),
          sukhovei_days_14d: Number(data.sukhovei_days_14d),
          sukhovei_days_30d: Number(data.sukhovei_days_30d),

          wind_mean_7d: Number(data.wind_mean_7d),
          wind_max_7d: Number(data.wind_max_7d),

          vpd_mean_7d: Number(data.vpd_mean_7d),
          vpd_max_7d: Number(data.vpd_max_7d),

          soil_moisture_7d: Number(data.soil_moisture_7d),
          soil_moisture_14d: Number(data.soil_moisture_14d),
          soil_moisture_30d: Number(data.soil_moisture_30d),

          snowfall_7d: Number(data.snowfall_7d),
          snowfall_14d: Number(data.snowfall_14d)

        }

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
      alert(
      `Засуха: ${result.prediction.results.drought.risk.label}\n` +
      `Суховей: ${result.prediction.results.sukhovei.risk.label}\n` +
      `Ранний снег: ${result.prediction.results.early_snow.risk.label}`
      )
    }catch(error){
      console.log("Ошибка", error)
      if (error.response) {
        alert(
          `Ошибка сервера: ${
            error.response.data.error || "Неизвестная ошибка"
          }`
        )

      } else if (error.request) {
        alert(
          "Не удалось подключиться к Node.js серверу"
        )
      } else {
        alert(
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
                <input type="number" placeholder="Географическая широта поля"  name="latitude" value={data.latitude} onChange={handleChange} required/>
                <input type="number" placeholder="Географическая долгота поля" name="longitude" value={data.longitude}  onChange={handleChange} required/>
                <input type="text" placeholder="Дата, для которой рассчитывается риск." name="date" value={data.date} onChange={handleChange} required/>
                <input type="number" placeholder="Средняя температура воздуха, °C." name="t_mean" value={data.t_mean} onChange={handleChange} required  min = '-30' max = '35' step = '0.1' />
                <input type="number" placeholder="Максимальная температура, °C." name="t_max" value={data.t_max} onChange={handleChange} required min = '-30' max = '45' step = '0.1' />
                <input type="number" placeholder="Минимальная температура, °C." name="t_min" value={data.t_min} onChange={handleChange} required min = '-40' max = '35' step = '0.1' />
                <input type="number" placeholder="Средняя относительная влажность воздуха, %." name="rh_mean" value={data.rh_mean} onChange={handleChange} required min = '20' max = '100' step = '0.1' />
                <input type="number" placeholder="Минимальная относительная влажность воздуха, %." name="rh_min" value={data.rh_min} onChange={handleChange} required min = '10' max = '100' step = '0.1' />
                <input type="number" placeholder="Средний VPD." name="vpd_mean" value={data.vpd_mean} onChange={handleChange} required min = '0' max = '4' step = '0.1' />
                <input type="number" placeholder="Максимальный VPD." name="vpd_max" value={data.vpd_max} onChange={handleChange} required min = '0' max = '6' step = '0.1' />
                <input type="number" placeholder="Количество осадков за текущий период, мм." name="precip" value={data.precip} onChange={handleChange} required min = '0' max = '80' step = '0.1' />
                <input type="number" placeholder="Количество именно дождевых осадков, мм." name="rain" value={data.rain} onChange={handleChange} required min = '0' max = '80' step = '0.1' />
                <input type="number" placeholder="Количество снега, мм." name="snowfall" value={data.snowfall} onChange={handleChange} required min = '0' max = '50' step = '0.1' />
              </div>
              <div className="container2">
                <input type="number" placeholder="Средняя скорость ветра, м/c." name="wind_mean" value={data.wind_mean} onChange={handleChange} required min = '0' max = '12' step = '0.1' />
                <input type="number" placeholder="Максимальная скорость ветра, м/c." name="wind_max" value={data.wind_max} onChange={handleChange} required min = '0' max = '20' step = '0.1' />
                <input type="number" placeholder="Максимальная скорость порывов ветра, м/c." name="wind_gust_max" value={data.wind_gust_max} onChange={handleChange} required min = '0' max = '30' step = '0.1' />
                <input type="number" placeholder="Влажность почвы, %." name="soil_moisture" value={data.soil_moisture} onChange={handleChange} required min = '0.05' max = '0.5' step = '0.01' />
                <input type="number" placeholder="Температура почвы, °C." name="soil_temperature" value={data.soil_temperature} onChange={handleChange} required min = '-10' max = '40' step = '0.1' />
                <input type="number" placeholder="Осадки за последние 7 дней, мм." name="precip_7d" value={data.precip_7d} onChange={handleChange} required min = '0' max = '150' step = '0.1' />
                <input type="number" placeholder="Осадки за последние 14 дней, мм." name="precip_14d" value={data.precip_14d} onChange={handleChange} required min = '0' max = '250' step = '0.1' />
                <input type="number" placeholder="Осадки за последние 30 дней, мм." name="precip_30d" value={data.precip_30d} onChange={handleChange} required min = '0' max = '400' step = '0.1' />
                <input type="number" placeholder="Количество сухих дней за последние 7 дней, д." name="dry_days_7d" value={data.dry_days_7d} onChange={handleChange} required min = '0' max = '7'/>
                <input type="number" placeholder="Количество сухих дней за последние 14 дней, д." name="dry_days_14d" value={data.dry_days_14d} onChange={handleChange} required min = '0' max = '14'/>
                <input type="number" placeholder="Сухих дней за последние 30 дней, д." name="dry_days_30d" value={data.dry_days_30d} onChange={handleChange} required min = '0' max = '30'/>
                <input type="number" placeholder="Жарких дней за последние 7 дней, д." name="hot_days_7d" value={data.hot_days_7d} onChange={handleChange} required min = '0' max = '7' />
                <input type="number" placeholder="Жарких дней за последние 14 дней, д." name="hot_days_14d" value={data.hot_days_14d} onChange={handleChange} required min = '0' max = '14'/>
              </div>
              <div className="container3">
                <input type="number" placeholder="Жарких дней за последние 30 дней, д." name="hot_days_30d" value={data.hot_days_30d} onChange={handleChange} required min = '0' max = '30'/>
                <input type="number" placeholder="Суховеев за последние 7 дней, д." name="sukhovei_days_7d" value={data.sukhovei_days_7d} onChange={handleChange} required min = '0' max = '7' />
                <input type="number" placeholder="Суховеев за последние 14 дней, д." name="sukhovei_days_14d" value={data.sukhovei_days_14d} onChange={handleChange} required min = '0' max = '14' />
                <input type="number" placeholder="Суховеев за последние 30 дней, д." name="sukhovei_days_30d" value={data.sukhovei_days_30d} onChange={handleChange} requiredmin = '0' max = '30' />
                <input type="number" placeholder="Средняя скорость ветра за последние 7 дней, м/c." name="wind_mean_7d" value={data.wind_mean_7d} onChange={handleChange} required min = '0' max = '12' step = '0.1' />
                <input type="number" placeholder="Максимальная скорость ветра за последние 7 дней, м/c." name="wind_max_7d" value={data.wind_max_7d} onChange={handleChange} required min = '0' max = '20' step = '0.1' />
                <input type="number" placeholder="Средний VPD за последние 7 дней." name="vpd_mean_7d" value={data.vpd_mean_7d} onChange={handleChange} required min = '0' max = '4' step = '0.1' />
                <input type="number" placeholder="Максимальный VPD за последние 7 дней." name="vpd_max_7d" value={data.vpd_max_7d} onChange={handleChange} required min = '0' max = '6' step = '0.1' />
                <input type="number" placeholder="Влажность почвы за последние 7 дней, %." name="soil_moisture_7d" value={data.soil_moisture_7d} onChange={handleChange} required min = '0.05' max = '0.5' step = '0.01' />
                <input type="number" placeholder="Влажность почвы за последние 14 дней, %" name="soil_moisture_14d" value={data.soil_moisture_14d} onChange={handleChange} required min = '0.05' max = '0.5' step = '0.01' />
                <input type="number" placeholder="Влажность почвы за последние 30 дней, %." name="soil_moisture_30d" value={data.soil_moisture_30d} onChange={handleChange} requiredmin = '0.05' max = '0.5' step = '0.01' />
                <input type="number" placeholder="Снега за последние 7 дней, д." name="snowfall_7d" value={data.snowfall_7d} onChange={handleChange} required min = '0' max = '50' step = '0.1' />
                <input type="number" placeholder="Снега за последние 14 дней, д" name="snowfall_14d" value={data.snowfall_14d} onChange={handleChange} required min = '0' max = '100' step = '0.1' />
              </div>
            </div>
            <button className="btn" type="submit">Отправить</button>
          </form>
        </section>
        <table>
          <tr>
            <th>Засуха:aaaaa</th>
          </tr>
          <tr>
            <th>Суховей:aaaaa</th>
          </tr>
          <tr>
            <th>Ранний снег:aaaaa</th>
          </tr>
        </table>
      </main>
      <footer>
        <h1 className="foottext">AgroMetrics</h1>
      </footer>
    </div>
  )
}

export default App