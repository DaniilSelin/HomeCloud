package api

import (
	"github.com/gorilla/mux"
)

func RegisterRoutes() *mux.Router {
	// Инициализация маршрутизатора
	router := mux.NewRouter()

	// Группируем все маршруты для загрузки
	uploadRouter := router.PathPrefix("/upload").Subrouter()
	uploadRouter.HandleFunc("/{path}/{fileName}", uploadHandler).Methods("POST")

	resumableUploadRouter := router.PathPrefix("/resumable_upload").Subrouter()
	resumableUploadRouter.HandleFunc("", ResumableUploadInitHandler).Methods("POST")
	resumableUploadRouter.HandleFunc("/{sessionID}", ResumableUploadHandler).Methods("POST")

	return router
}