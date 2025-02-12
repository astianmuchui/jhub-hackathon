package handlers

import (
	"github.com/gofiber/fiber/v2"
)

func HomeHandler(c *fiber.Ctx) error {
	return c.Render("home", fiber.Map{})
}

func UploadHandler(c *fiber.Ctx) error {
	return c.Render("upload", fiber.Map{})
}
