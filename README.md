# AgroMetrics
### Описание 
AgroMetrics - аналитический подход к оценке засухи и заморозков.
Проект представляет собой веб-прототип системы для сельского хозяйства, которая помогает оценить выявить возможные агрометеорологические риски.
Пользователь может указать данные о своём поле, после чего система анализирует характеристики поля и погодные условия и формерует прогноз.
Основная задача проекта - помочь фермеру принимать решения на основе данных, а не только собственного опыта.

### Используемый стек
#### DataSet
Open-MetEeo = https://open-meteo.com/ , https://open-meteo.com/en/docs/historical-weather-api
#### Backend
Python

NodeJS ExpressJS
#### Frontend
ReactJS HTML CSS

### Инструкция запуска
клонировать проект __git clone https://github.com/Feitilator/AgroMetrics__ или скачать из репозитория
# Python(ML + API)
Открыть папку ml-model в Pycharm
Создать виртуальную среду для Python и написать в терминал __pip install -r requirements.txt__ для установки зависимостей
запустить сервер введя __uvicorn app:app --reload__ в терминал
# NodeJs Expressjs (Основной бэкенд)
Открыть папку backend в VScode
написать в терминал __npm i__ для установки зависимостей
запустить бэкенд командой __npm start__
# React(Frontend)
Открыть папку client в VScode
написать в терминал __npm i__ для установки зависимостей
запустить Frontend командой __npm run dev__
и открыть ссылку __http://localhost:5173/__ в браузере

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
