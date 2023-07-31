# MyFiastAPIproject2
FastApi project
# MyFastApiProject

Проект на FastAPI с использованием PostgreSQL в качестве БД. Реализация REST API по работе с меню ресторана. Для более удобного запуска используется docker-compose.

## Установка и запуск

Следуйте инструкциям ниже, чтобы установить и запустить проект на своем компьютере или сервере.

### Предварительные требования

Наличие:

- Docker
- Docker Compose

### Клонирование репозитория

```bash
git clone https://github.com/your_username/MyFastApiProject.git
cd MyFastApiProject
```

### Запуск проекта

- В Pycharm открыть File -> settings -> python interpreter, добавить New enviroment
- Перейти в коммандной строке Windows в директорию проекта и запустить команду:
  ```
  venv\Scripts\activate
  ```
- Далее выполнить следующую команду(docker должен быть установлен и запущен с правами администратора)
```
docker-compose up --build
```
- Теперь программа готова к тестированию

### Запуск тестирования
Для запуска тестов запустите следующую команду
```
docker-compose -f docker-compose-test.yml up
```
### Структура проекта

- app/ - директория с файлами приложения
- docker/ - директория с Docker-контейнерами и Docker-файлами
- requirements.txt - файл зависимостей для установки необходимых пакетов
