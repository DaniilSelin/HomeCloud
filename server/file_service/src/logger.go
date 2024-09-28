package main

import (
    "fmt"
    "path/filepath"
    "log"
    "time"
    "gopkg.in/natefinch/lumberjack.v2"
)

var (
	grpcLogger *log.Logger	
	requestLogger *log.Logger
	errorLogger *log.Logger
)

func GetLogFile() (string, error) {
	serverRoot := "../../" 

    // Определяем путь до home_cloud_files
    logDir := filepath.Join(serverRoot, "log/")

    // Получаем абсолютный путь
    absoluteLogDir, err := filepath.Abs(logDir)
    if err != nil {
        fmt.Println("Error getting absolute path:", err)
        return "", err
    }

    return absoluteLogDir, nil
}

func GetLogger() error {
	logDir, err := GetLogFile()
    if err != nil {
        return fmt.Errorf("failed to get log directory: %v", err)
    }

	grpcLogger = log.New(&lumberjack.Logger{
		Filename: filepath.Join(logDir, "gRPC/gRPC.log"),
		MaxSize: 10,
		MaxBackups: 5,
	}, "gRPC: ", log.Ldate|log.Ltime|log.Lshortfile)

	requestLogger = log.New(&lumberjack.Logger{
		Filename: filepath.Join(logDir, "request/request.log"),
		MaxSize: 10,
		MaxBackups: 5,
	}, "REQUEST: ", log.Ldate|log.Ltime|log.Lshortfile)

	errorLogger = log.New(&lumberjack.Logger{
		Filename: filepath.Join(logDir, "error/error.log"),
		MaxSize: 10,
		MaxBackups: 5,
	}, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile)

	return nil
}

// LogGRPCRequest логирует запросы gRPC с форматированием
func LogGRPC(method, params string, duration time.Duration ,statusCode int, responseBody string) {
    // Форматируем сообщение для логгера
	logMessage := fmt.Sprintf(
        " - gRPC_service - INFO - method=%s - params=%s - duration=%v ms - status_code=%d - response_body=%s \n - ",
        method, params, duration.Milliseconds(), statusCode, responseBody,
    )

    grpcLogger.Println(logMessage)
}