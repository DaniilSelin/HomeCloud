package api

import (
	"fmt"
	"net/http"
	"os"
	"io"
	"json"
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
	// Простейшая загрузка
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
	_, err = io.Copy(uploadFile, r.Body)
	if err != nil {
		http.Error(w, "Unable to save file", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "file uploading succesfull %s", filePath)
}

// ДОДЕЛАТЬ !!!
/// КАК ЖЕ НАДО СМАЧНО ВСЕ ЭТО ДОДЕЛАТЬ ПОСЛЕ СЕРВИСА МЕТАДАННЫХ КАК ЖЕ НАДО
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

func ResumableUploadInitHandler(w http.ResponseWriter, r *http.Request) {
	// Возобновляемая загрузка
	vars := mux.Vars(r)
	path := vars["path"]
	fileName := vars["fileName"]
	size := vars["size"]
	// metadata := vars["metadata"]

	// Создаем уникальный идентификатор сессии на агрузку
	sessionID := generateUniqueID()

	// ПОмещаем пока в срез сессию
	saveUploadSession(sessionID, uploadInfo)

	response := map[string]string{
		"upload_url": fmt.Sprintf("/upload/resume/%s", sessionID),
		"sessionID": sessionID,
		"filePath": 
	}
	json.NewEncoder(w).Encode(response)
}


func ResumableUploadHandler(w http.ResponseWriter, r *http.Request) {
	// Принимаем чанк фалйа
	vars := mux.Vars(r)
	sessionID := vars["sessionID"]

	// Получаем данные сессии из базы/кэша
    session, filePath, err := getUploadSession(sessionID)
    if err != nil {
        http.Error(w, "Session not found", http.StatusNotFound)
        return
    }

    // Определяем куда пихать полученный чанк 
    rangeHeader := Header.Get("Content-Range")
    start, end := parseRange(rangeHeader)

    // Записываем чанк в файл
    file, err := os.Open(filePath)
    if err != nil {
		fmt.Println(err)
		http.Error(w, "Unable to upload chank file", http.StatusInternalServerError)
		return
	}
	defer uploadFile.Close()

	// Пишем данные по нужному смещению
    _, err = file.WriteAt(r.Body, int64(start))
    if err != nil {
        http.Error(w, "Unable to write file chunk", http.StatusInternalServerError)
        return
    }

    // Обновляем прогресс сессии
    session.Progress += (end - start + 1)
    saveUploadSession(sessionID, session)

    w.WriteHeader(http.StatusOK)
    fmt.Fprintln(w, "Chunk uploaded successfully")
}


func ResumableUploadFinishHandler(w http.ResponseWriter, r *http.Request) {
	// Принимаем чанк фалйа
	vars := mux.Vars(r)
	sessionID := vars["sessionID"]

	// Получаем данные сессии
    session, filePath, err := getUploadSession(sessionID)
    if err != nil {
        http.Error(w, "Session not found", http.StatusNotFound)
        return
    }

	// Проверяем, загружен ли весь файл
    if session.Progress < session.FileSize {
        http.Error(w, "File upload not complete", http.StatusBadRequest)
        return
    }

    // Проверяем контрольную сумму
    if !checkIntegrity(session.TempFilePath, session.ExpectedChecksum) {
        http.Error(w, "File checksum mismatch", http.StatusInternalServerError)
        return
    }

    // Если все хорошо, перемещаем файл в постоянное хранилище
    finalizeFileUpload(session)

    w.WriteHeader(http.StatusOK)
    fmt.Fprintln(w, "File uploaded and verified successfully")
}
