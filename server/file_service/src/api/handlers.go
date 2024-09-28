package api

import (
	"fmt"
	"net/http"
	"os"
	"io"
	"github.com/gorilla/mux"
	"path/filepath"
)

func GetHomeDirHandle() (string, error) {
    serverRoot := "../../" 

    // Определяем путь до home_cloud_files
    homeDir := filepath.Join(serverRoot, "home_cloud_files")

    // Получаем абсолютный путь
    absoluteHomeDir, err := filepath.Abs(homeDir)
    if err != nil {
        fmt.Println("Error getting absolute path:", err)
        return "", err
    }

    return absoluteHomeDir, nil
}

func uploadFileHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Println(" 1 ")
	// Извлекаем путь и имя файла из url
	vars := mux.Vars(r)
	path := vars["path"]
	fileName := vars["fileName"]

	// Загрузка фалойв
	fmt.Println(" 2 ")
	homeDir, err := GetHomeDirHandle()
	if err != nil {
		http.Error(w, "Unable to get HomeDir", http.StatusInternalServerError)
		return
	}
	fmt.Println(" 3 ")
	filePath := filepath.Join(homeDir, path, fileName)

	uploadFile, err := os.Create(filePath)
	fmt.Println(filePath, uploadFile)
	if err != nil {
		fmt.Println(err)
		http.Error(w, "Unable to create file", http.StatusInternalServerError)
		return
	}
	defer uploadFile.Close()
	fmt.Println(" 4 ")
	_, err = io.Copy(uploadFile, r.Body)
	if err != nil {
		http.Error(w, "Unable to save file", http.StatusInternalServerError)
		return
	}
	fmt.Println(" 5 ")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "file uploading succesfull))))!!!!! %s", filePath)
}