# HomeCloud
<p align="center">
  <img style="float:left" src="https://github.com/DaniilSelin/HomeCloud/blob/main/logo.jpg" alt="HomeCloud Logo" width="200" />
 HomeCloud — решение для превращения компьютера в облачное хранилище.
</p>

# Состояние проекта
 Идет работа над серверной частью!
 Переписал docker-compose.yml, чтобы он брал образ из моего рерозитория на DockerHub.
 Настроена автоматическая сборка докер-образов и их пуш на DockerHub через GitAction. Написал тесты для сервиса авторизации (GitActin: run test).
 
 Стадия разработки сервисов: 
- сервис авторизации - 80% (Python)
- файловый сервис - 1% (Go)
- сервис метаданных - 0% (Go)
