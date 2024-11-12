package main

import (
	"fmt"
	"net/http"
	"file_service/src/api"
    "log"
)

func init() {
	// Инициализируем логгеры
    err := GetLogger()
    if err != nil {
        log.Fatalf("Failed to initialize loggers: %v", err)
    }

    // G_RPC муть потом разберемся с ней
	// создаем папки для пользователей
	//err = RunClient()
	//if err != nil {
	//	fmt.Println("НЕ ПОЛУЧИЛАСЬ")
	//	log.Fatalf("Error thet creating workdir: %v", err)
	//}
}

func main() {
	// Регистрируем маршруты
	router := api.RegisterRoutes()

	// Запускаем сервер
	fmt.Println("Start server on port 8000")
	err := http.ListenAndServe(":8000", router)
	if err != nil {
		fmt.Println("ERROR - ", err)
	}
}