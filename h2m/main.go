package main

import (
	"log"
	"os"

	htmltomarkdown "github.com/JohannesKaufmann/html-to-markdown/v2"
)

func main() {

	f, err := os.Open("data/pages/html")
	if err != nil {
		log.Fatalf("Error when opening file: %v", err)
	}
	defer f.Close()
	dirEntries, err := f.ReadDir(0)
	if err != nil {
		log.Fatalf("Cannot read directory entries: %v", err)
	}

	for _, v := range dirEntries {

		title := v.Name()[:len(v.Name())-5]

		// 1. Read html
		htmlBytes, err := os.ReadFile("data/pages/html/" + title + ".html")
		if err != nil {
			log.Fatalf("Failed to read html file: %v", err)
		}

		// 2. HTML → Markdown
		markdown, err := htmltomarkdown.ConvertString(string(htmlBytes))
		if err != nil {
			log.Fatalf("Failed to convert: %v", err)
		}

		// 3. Write to .md
		if err := os.WriteFile("data/pages/md/"+title+".md", []byte(markdown), 0644); err != nil {
			log.Fatalf("Failed to write to markdown: %v", err)
		}

		log.Println("Conversion from html to md done, file saved as:", "data/pages/md/"+title+".md")
	}

}
