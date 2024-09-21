package main

import (
	"fmt"
	"net/http"
	"file_service/src/api"
)

func main() {
	// Регистрируем маршруты
	api.ReisterRoutes()

	// Запускаем сервер
	fmt.Println("Start server on port 8000")
	err := http.ListenAndServe(":8000", nil)
	if err != nil {
		fmt.Println("ERROR - ", err)
	}
}