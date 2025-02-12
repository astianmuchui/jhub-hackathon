package main

import (
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/fiber/v2/middleware/recover"
	"github.com/gofiber/template/django/v3"
	"github.com/astianmuchui/jhub-hackathon/handlers"
)

func main() {
	engine := django.New("./views", ".html")

	app := fiber.New(fiber.Config{
		Views: engine,
	})

	app.Use(recover.New())
	app.Use(logger.New())

	app.Get("/", handlers.HomeHandler)
	app.Get("/upload", handlers.UploadHandler)

	app.Static("/assets", "./assets")
	app.Listen(":8080")
}