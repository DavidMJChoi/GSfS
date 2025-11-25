package main

import (
	"fmt"
	"log"
	"os"
)

// htmltomarkdown "github.com/JohannesKaufmann/html-to-markdown/v2"

func main() {

	f, err := os.Open("../data/pages/md")
	if err != nil {
		log.Fatalf("Error when opening file: %v", err)
	}
	defer f.Close()

	dirEntries, err := f.ReadDir(0)
	if err != nil {
		log.Fatalf("Cannot read directory entries: %v", err)
	}
	for _, v := range dirEntries {
		fmt.Println(v)
	}

	// title := "Human brains are preconfigured with instructions for understanding the world"
	// // 1. 读取 HTML 文件
	// htmlBytes, err := os.ReadFile("../data/pages/" + title + ".html")
	// if err != nil {
	// 	log.Fatalf("读取 HTML 文件失败: %v", err)
	// }

	// // 2. HTML → Markdown
	// markdown, err := htmltomarkdown.ConvertString(string(htmlBytes))
	// if err != nil {
	// 	log.Fatalf("转换失败: %v", err)
	// }

	// // 3. 写入 .md 文件
	// if err := os.WriteFile("../data/pages/md/"+title+".md", []byte(markdown), 0644); err != nil {
	// 	log.Fatalf("写入 Markdown 文件失败: %v", err)
	// }

	// log.Println("转换完成，结果已保存到 output.md")
}
