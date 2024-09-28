package api

import (
	"github.com/gorilla/mux"
)

func RegisterRoutes() *mux.Router {
	// Инициализация маршрутизатора
	router := mux.NewRouter()

	router.HandleFunc("/upload/{path}/{fileName}", uploadFileHandler).Methods("POST")

	return router
}