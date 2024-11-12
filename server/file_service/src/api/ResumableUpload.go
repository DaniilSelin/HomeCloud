/*
Возобновляемая загрузка (без метаданых пока)
*/
package api

import (
	"fmt"
	"net/http"
	"os"
	"io"
	"log"
	"sync"
	"encoding/json"
	"strconv"
	"crypto/sha256"
	"path/filepath"
	"regexp"

	"github.com/gorilla/mux"
	"github.com/google/uuid"
)

// ResumbleUploadRequest - структура запроса для инициализации загрузки с информацией о файле в формате json
type ResumbleUploadRequest struct {
    FilePath string `json:"filePath"`
    Size     uint64  `json:"size"`
    Sha256 string `json:"sha256"`
}

// parseRange - функция для извлечения начального и конечного байтов из заголовка Content-Range
// Ожидаемый формат заголовка: bytes {start}-{end}/{total}
func parseRange(rangeHeader string) (start, end uint64, err error) {
	matches := rangeRegex.FindStringSubmatch(rangeHeader)

	// Проверяем, что получили нужное количество частей
	if len(matches) < 3 {
		return 0, 0, fmt.Errorf("invalid Content-Range format")
	}

	start, err = strconv.ParseUint(matches[1], 10, 64)
	if err != nil {
		return 0, 0, fmt.Errorf("invalid start value: %v", err)
	}

	end, err = strconv.ParseUint(matches[2], 10, 64)
	if err != nil {
		return 0, 0, fmt.Errorf("invalid end value: %v", err)
	} 

	return start, end, nil
}

// session - структура для хранения данных сессии загрузки
type session struct {
	filePath string
	CountByte uint64
	sha256 string
	TimeOut uint64
} 

// Мьютекс для защиты SessionHashTable
var sessionMutex = sync.RWMutex{}
// SessionHashTable - хранилище сессий загрузки для восстановления при поступлении новых частей файла
var SessionHashTable = make(map[string]session, 1000)

// регулярное выражение для парсинга start и end из Content-Range
var rangeRegex = regexp.MustCompile(`bytes (\d+)-(\d+)/(\d+|\*)`)

// generateUniqueID - функция для генерации уникального идентификатора сессии загрузки
func generateUniqueID() string {
	id := uuid.New()
	return id.String()
}

// saveUploadSession - сохраняет информацию о сессии загрузки в глобальную хеш-таблицу
func saveUploadSession(id, filePath, sha256 string, SizeFile uint64) {
	sessionMutex.Lock()
	defer sessionMutex.Unlock()

	SessionHashTable[id] = session{filePath: filePath, CountByte: SizeFile, sha256: sha256}
}

// getUploadSession - получает сессию загрузки по sessionID
func getUploadSession(sessionID string) (session, error) {
	fsession, found := SessionHashTable[sessionID]

	if found {
		return fsession, nil
	} 

	return session{}, fmt.Errorf("Not found session wtih id=%v", sessionID)
}

// deleteUploadSession - удаляет сессию загрузки по sessionID после завершения загрузки
func deleteUploadSession(sessionID string) {
	sessionMutex.Lock()
	defer sessionMutex.Unlock()

	delete(SessionHashTable, sessionID)
}

// checkControlSum - проверяет SHA-256 контрольную сумму файла для проверки целостности
func checkControlSum(filePath, expectedSHA string) (bool, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return false, fmt.Errorf("error opening file: %v", err)
	}
	defer file.Close()

	hasher := sha256.New()
	if _, err := io.Copy(hasher, file); err != nil {
		return false, fmt.Errorf("error calculating SHA-256: %v", err)
	}

	actualSHA := fmt.Sprintf("%x", hasher.Sum(nil))

	return actualSHA == expectedSHA, nil
}

// ResumableUploadInitHandler - инициализация сессии возобновляемой загрузки
func ResumableUploadInitHandler(w http.ResponseWriter, r *http.Request) {
	// Логирование начала обработки запроса
	log.Println("Handling resumable upload initialization")

    var req ResumbleUploadRequest
    err := json.NewDecoder(r.Body).Decode(&req)
    if err != nil {
        http.Error(w, "Unable to decode request", http.StatusBadRequest)
        return
    }
    defer r.Body.Close()

	// Создаем уникальный идентификатор сессии
	sessionID := generateUniqueID()
	log.Printf("Generated session ID: %s", sessionID)

	// Получаем корневую директорию для загрузки
	homeDir, err := GetHomeDirHandle()
	if err != nil {
		log.Printf("Error getting home directory: %v\n", err)
		http.Error(w, "Unable to get HomeDir", http.StatusInternalServerError)
		return
	}
	
	// Проверка на корректность пути
	req.FilePath, err = validateFilePath(req.FilePath, homeDir)
	if err != nil {
		log.Println("Invalid file path:", err)
		http.Error(w, "Invalid file path", http.StatusBadRequest)
		return
	}

	// Создаем директорию, если она не существует
	err = os.MkdirAll(filepath.Dir(req.FilePath), 0755)
	if err != nil {
		log.Printf("Failed to create directories: %v\n", err)
		http.Error(w, "Unable to create directory", http.StatusInternalServerError)
		return
	}

	// Сохраняем сессию
	saveUploadSession(sessionID, req.FilePath, req.Sha256, req.Size)

	// Формируем ответ
	response := map[string]string{
		"upload_url": fmt.Sprintf("/resumable_upload/%s", sessionID),
		"sessionID": sessionID,
	}
	log.Printf("Session initialized for file: %s, size: %v, session ID: %s, sha256: %s", req.FilePath, req.Size, sessionID, req.Sha256)

	// Отправляем JSON-ответ
	if err := json.NewEncoder(w).Encode(response); err != nil {
	    log.Printf("Error encoding JSON response: %v", err)
	    http.Error(w, "Failed to send response", http.StatusInternalServerError)
	    return
	}
}

// ResumableUploadHandler - обработка части файла при возобновляемой загрузке
func ResumableUploadHandler(w http.ResponseWriter, r *http.Request) {
	// Логирование начала обработки чанк-загрузки
	log.Println("Handling chunk upload")

	// Извлекаем sessionID из параметров URL
	vars := mux.Vars(r)
	sessionID := vars["sessionID"]
	log.Printf("Received session ID: %s", sessionID)

	// Получаем данные сессии из хеш-таблицы
	session, err := getUploadSession(sessionID)
	if err != nil {
		log.Printf("Error fetching session: %v", err)
		http.Error(w, "Session not found", http.StatusNotFound)
		return
	}

	// Читаем заголовок Content-Range
	rangeHeader := r.Header.Get("Content-Range")

	if rangeHeader == "" {
	    http.Error(w, "Content-Range header missing", http.StatusBadRequest)
	    return
	}

	log.Printf("Content-Range header: %s", rangeHeader)
	start, end, err := parseRange(rangeHeader)

	if err != nil {
		log.Printf("Error parsing range: %v", err)
		http.Error(w, "Invalid Content-Range", http.StatusBadRequest)
		return
	}

	// Проверка флага окончания загрузки
	// Последний байт так же учитываем
	flagFinish := end + 1 >= session.CountByte
	log.Printf("Flag finish: %v", flagFinish)

	// Открытие файла для записи
	file, err := os.OpenFile(session.filePath, os.O_WRONLY|os.O_CREATE, 0666)
	if err != nil {
		log.Printf("Error opening file for writing: %v", err)
		http.Error(w, "Unable to upload chunk file", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	// Чтение данных из тела запроса
	chunkData, err := io.ReadAll(r.Body)
	if err != nil {
		log.Printf("Error reading file chunk: %v", err)
		http.Error(w, "Unable to read file chunk", http.StatusInternalServerError)
		return
	}

	// Запись данных в файл на нужной позиции
	_, err = file.WriteAt(chunkData, int64(start))
	if err != nil {
		log.Printf("Error writing file chunk: %v", err)
		http.Error(w, "Unable to write file chunk", http.StatusInternalServerError)
		return
	}

	// Завершение сессии, если файл загружен полностью
	if flagFinish {
		// Проверка, была ли предоставлена контрольная сумма
		if session.sha256 == "" {
			log.Println("Warning: Checksum not provided in session")
			w.WriteHeader(http.StatusBadRequest)
			fmt.Fprintln(w, "Warning: Checksum not provided in session")
			return
		}

		deleteUploadSession(sessionID)
		isValid, err := checkControlSum(session.filePath, session.sha256)
		if err != nil {
			log.Printf("Error checking checksum: %v", err)
			http.Error(w, "Failed to verify checksum", http.StatusInternalServerError)
			return
		}

		if isValid {
			log.Printf("File upload complete, checksum valid for session %s", sessionID)
			w.WriteHeader(http.StatusOK)
			fmt.Fprintln(w, "File uploaded successfully. Checksum is valid.")
		} else {
			log.Printf("File upload complete, checksum invalid for session %s", sessionID)
			w.WriteHeader(http.StatusBadRequest)
			fmt.Fprintln(w, "File uploaded but checksum is invalid.")
		}
		return
	}

	w.WriteHeader(http.StatusAccepted)
	fmt.Fprintln(w, "Chunk uploaded successfully")
}