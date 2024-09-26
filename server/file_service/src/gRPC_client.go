package main

import (
    "context"
    "fmt"
    "log"
    "os"
    "time"
    "path/filepath"
    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    pb "file_service/src/proto"
)

// GetHomeDir получает путь до директории home_cloud_files
func GetHomeDir() (string, error) {
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

// RunClient устанавливает соединение с gRPC сервером
// Затем создает при необходимости папки пользователям
func RunClient() error {
    startTime := time.Now()
    // Установите соединение с сервером gRPC
    conn, err := grpc.Dial("127.0.0.1:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatalf("Did not connect: %v", err)
    }
    defer conn.Close()

    // Создайте клиент для вашего сервиса
    client := pb.NewAuthServiceClient(conn)

    // Вызовите метод GetUsers
    response, err := client.GetUsers(context.Background(), &pb.Empty{})
    if err != nil {
        log.Fatalf("Error when calling GetUsers: %v", err)
    }

    LogGRPC(
        "GetUsers",      // Метод gRPC
        "{}", // Параметры запроса
        time.Since(startTime), // Время выполнения
        int(codes.OK),                  // Статус код
        "{message: 'GetUsers successful'}", // Тело ответа
    )

    // Обработайте ответ и создайте папки для пользователей
    homeDir, err := GetHomeDir()
    if err != nil {
        return err
    }

    fmt.Println(homeDir)

    for _, user := range response.Users {
        userFolder := filepath.Join(homeDir, user.Name) // Создаем путь к папке
        err := os.MkdirAll(userFolder, os.ModePerm)     // Создаем папку
        if err != nil {
            log.Printf("Failed to create folder for user %s: %v", user.Name, err)
        } else {
            log.Printf("Created folder for user: %s", user.Name)
        }
    }
    return nil // Возвращаем nil, если все прошло успешно
}