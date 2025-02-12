package handlers

import (
	"bytes"
	"fmt"
	"github.com/gofiber/fiber/v2"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"github.com/gofiber/fiber/v2/middleware/session"
	"encoding/json"
)

var Store = session.New()

func HomeHandler(c *fiber.Ctx) error {
	return c.Render("home", fiber.Map{
	})
}

func UploadHandler(c *fiber.Ctx) error {
	sess, err := Store.Get(c)
	if err != nil {
		return err
	}
	responseStr, exists := sess.Get("response").(string)
	if !exists {
		return c.Render("upload", fiber.Map{
			"response": nil,
		})
	}
	var responseMap map[string]interface{}
	if err := json.Unmarshal([]byte(responseStr), &responseMap); err != nil {
		return err
	}
	sess.Delete("response")
	sess.Save()
	return c.Render("upload", fiber.Map{
		"response": responseMap,
		"responseExists": true,
	})
}

func FileUploadHandler(c *fiber.Ctx) error {
	file, err := c.FormFile("image")
	if err != nil {
		return err
	}
	if err := c.SaveFile(file, fmt.Sprintf("./uploads/%s", file.Filename)); err != nil {
		return err
	} else {
		url := "http://20.164.17.182/predict"
		method := "POST"

		payload := &bytes.Buffer{}
		writer := multipart.NewWriter(payload)
		uploadedFile, errFile1 := os.Open(fmt.Sprintf("./uploads/%s", file.Filename))
		defer uploadedFile.Close()
		part1, errFile1 := writer.CreateFormFile("file", filepath.Base(fmt.Sprintf("./uploads/%s", file.Filename)))
		_, errFile1 = io.Copy(part1, uploadedFile)
		if errFile1 != nil {
			fmt.Println(errFile1)
			return errFile1
		}
		err := writer.Close()
		if err != nil {
			fmt.Println(err)
			return err
		}

		client := &http.Client{}
		req, err := http.NewRequest(method, url, payload)

		if err != nil {
			fmt.Println(err)
			return err
		}
		req.Header.Set("Content-Type", writer.FormDataContentType())
		res, err := client.Do(req)
		if err != nil {
			fmt.Println(err)
			return err
		}
		defer res.Body.Close()

		body, err := io.ReadAll(res.Body)
		if err != nil {
			fmt.Println(err)
			return err
		}
		fmt.Println(string(body))
		sess, err := Store.Get(c)
		if err != nil {
			return err
		}
		sess.Set("response", string(body))
		if err := sess.Save(); err != nil {
			return err
		}
	}

	return c.Redirect("/upload")
}
