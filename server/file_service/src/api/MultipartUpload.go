// ДОДЕЛАТЬ !!!
/// КАК ЖЕ НАДО СМАЧНО ВСЕ ЭТО ДОДЕЛАТЬ ПОСЛЕ СЕРВИСА МЕТАДАННЫХ КАК ЖЕ НАДО
package api

import (
	"fmt"
	"net/http"
	"os"
	"io"
	"github.com/gorilla/mux"
	"path/filepath"
)

func multipartUploadHandler(w http.ResponseWriter, r *http.Request) {
	// Многокомпонентная загрузка
	// ЗАБЕЙ ДО СОЗДАНИЯ СЕРИВСА МЕТАДАННЫХ
	// Извлекаем путь и имя файла из url
	vars := mux.Vars(r)
	path := vars["path"]
	fileName := vars["fileName"]

	// Загрузка фалойв
	
	// Директория для загрузки
	homeDir, err := GetHomeDirHandle()
	if err != nil {
		http.Error(w, "Unable to get HomeDir", http.StatusInternalServerError)
		return
	}
	filePath := filepath.Join(homeDir, path, fileName)

	uploadFile, err := os.Create(filePath)
	if err != nil {
		fmt.Println(err)
		http.Error(w, "Unable to create file", http.StatusInternalServerError)
		return
	}
	defer uploadFile.Close()

	// Записываем данные в файл
	_, err = io.Copy(uploadFile, r.Body)
	if err != nil {
		http.Error(w, "Unable to save file", http.StatusInternalServerError)
		return
	}

	// извлекаем метаданные
	//metadata := vars["metadata"]

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "file uploading succesfull %s", filePath)
}