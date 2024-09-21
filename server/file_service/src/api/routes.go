package api

import (
	"net/http"
)

func ReisterRoutes() {
	http.HandleFunc("/", Handler)
}