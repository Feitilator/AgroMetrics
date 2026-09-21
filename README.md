# AgroMetrics
### Описание 
AgroMetrics - аналитический подход к оценке засухи и заморозков.
Проект представляет собой веб-прототип системы для сельского хозяйства, которая помогает оценить выявить возможные агрометеорологические риски.
Пользователь может указать данные о своём поле, после чего система анализирует характеристики поля и погодные условия и формерует прогноз.
Основная задача проекта - помочь фермеру принимать решения на основе данных, а не только собственного опыта.

### Используемый стек
#### DataSet
Open-MetEeo =
https://open-meteo.com/ , https://open-meteo.com/en/docs/historical-weather-api
#### Backend
Python

NodeJS - ExpressJS
#### Frontend
React HTML CSS

### Инструкция запуска
# Python(ML + API)
Открыть папку ml-model в Pycharm
написать в терминал pip install -r requirements.txt для установки зависимостей
запустить сервер введя uvicorn app:app --reload в терминал
# NodeJs Expressjs (Основной бэкенд)
Открыть папку backend в VScode
написать в терминал npm i для установки зависимостей
запустить бэкенд командой npm start
# React(Frontend)
Открыть папку client в VScode
написать в терминал npm i для установки зависимостей
запустить Frontend командой npm run dev
и открыть ссылку http://localhost:5173/ в браузере

### Источники данных
Open-Meteo = https://open-meteo.com/ , https://open-meteo.com/en/docs/historical-weather-api

### Состав команды
Григорьев Антон
Курскиев Гилани
Волков Вячеслав
Назаров Жаслан

### Что было разработано
Frontend на React как панель для ввода данных
Backend на NodeJs ExpressJs как основной Backend
ML-Model Api на Python как api для бэкенда и ml-model для прогноза
