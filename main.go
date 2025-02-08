package main

import (
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/fiber/v2/middleware/recover"
	"github.com/gofiber/template/django/v3"
)

func main () {
	engine := django.New("./views", ".django")
	app := fiber.New(fiber.Config{
		Prefork: true,
		Views: engine,
	})

	app.Use(recover.New())
	app.Use(logger.New())

	app.Get("/", func (c *fiber.Ctx) error {
		return c.SendString("Hello")
	})

	app.Listen(":8080")
}