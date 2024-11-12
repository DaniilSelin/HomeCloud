package api

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"log"
)

// UploadRequest - структура запроса для инициализации загрузки с информацией о файле в формате json
type UploadRequest struct {
	FilePath string `json:"filePath"`
}

// GetHomeDirHandle возвращает абсолютный путь к директории хранения файлов
func GetHomeDirHandle() (string, error) {
	serverRoot := "../../"
	homeDir := filepath.Join(serverRoot, "home_cloud_files")

	absoluteHomeDir, err := filepath.Abs(homeDir)
	if err != nil {
		log.Println("Error getting absolute path:", err)
		return "", err
	}

	return absoluteHomeDir, nil
}

// validateFilePath проверяет, что путь файла корректен и не выходит за пределы разрешенной директории
func validateFilePath(filePath, homeDir string) (string, error) {
	// Объединяем корневую директорию и путь к файлу
	uploadFilePath := filepath.Join(homeDir, filePath)

	// Нормализуем путь
	uploadFilePath = filepath.Clean(uploadFilePath)

	// Проверяем, не пытается ли пользователь выйти за пределы разрешенной директории
	if !filepath.HasPrefix(uploadFilePath, homeDir) {
		log.Println("Attempt to upload file outside allowed directory")
		return "", fmt.Errorf("invalid file path")
	}

	return uploadFilePath, nil
}

// uploadHandler обрабатывает запросы на загрузку файла
func uploadHandler(w http.ResponseWriter, r *http.Request) {
	// Сначала сразу закрываем тело запроса после всех действий с ним
	defer r.Body.Close()

	// Декодируем JSON-запрос для получения пути к файлу
	var req UploadRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		log.Printf("Failed to decode request: %v\n", err)
		http.Error(w, "Unable to decode request", http.StatusBadRequest)
		return
	}

	// Валидация пути файла
	if req.FilePath == "" {
		log.Println("File path is empty")
		http.Error(w, "File path cannot be empty", http.StatusBadRequest)
		return
	}

	// Получаем корневую директорию для загрузки
	homeDir, err := GetHomeDirHandle()
	if err != nil {
		log.Printf("Error getting home directory: %v\n", err)
		http.Error(w, "Unable to get HomeDir", http.StatusInternalServerError)
		return
	}

	// Проверка на корректность пути
	uploadFilePath, err := validateFilePath(req.FilePath, homeDir)
	if err != nil {
		log.Println("Invalid file path:", err)
		http.Error(w, "Invalid file path", http.StatusBadRequest)
		return
	}

	// Создаем директорию, если она не существует
	err = os.MkdirAll(filepath.Dir(uploadFilePath), 0755)
	if err != nil {
		log.Printf("Failed to create directories: %v\n", err)
		http.Error(w, "Unable to create directory", http.StatusInternalServerError)
		return
	}

	// Создаем и открываем файл для записи
	uploadFile, err := os.Create(uploadFilePath)
	if err != nil {
		log.Printf("Failed to create file: %v\n", err)
		http.Error(w, "Unable to create file", http.StatusInternalServerError)
		return
	}
	defer uploadFile.Close()

	// Копируем содержимое тела запроса в файл
	_, err = io.Copy(uploadFile, r.Body)
	if err != nil {
		log.Printf("Failed to save file: %v\n", err)
		http.Error(w, "Unable to save file", http.StatusInternalServerError)
		return
	}

	// Отправляем успешный ответ
	w.WriteHeader(http.StatusOK)
	log.Printf("File uploaded successfully to %s\n", uploadFilePath)
	fmt.Fprintf(w, "File uploaded successfully to %s", uploadFilePath)
}
