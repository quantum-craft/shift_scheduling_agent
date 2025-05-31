# Readme

## 編譯方法 

### 方法一

```bash
uv run langgraph build -t shift_scheduling_agent
```

### 方法二


1. 安裝 langgraph-cli


```bash
pip install langgraph-cli[inmem] 
```

*note: 可以考慮用 uv 幫助環境建置*

```bash
uv pip install langgraph-cli[inmem] 
```

2. 編譯 container image

```bash
langgraph build -t shift_scheduling_agent:latest
```

## 本機測試

### 前置作業

1. 增加 .env 檔
   1. langsmith 相關參數是必要參數
   2. 按需填上 LLM API Key

### 啟動服務

-- docker compose up

docker compose --env-file .env.tstxe up

## 本機執行

uv run langgraph dev # 直接 run

uv run langgraph up # 會 build docker image

localhost:3000/docs 可以看文件

## go to production todo list

服務本身
/health api endpoint for AKS

服務外圍資源
postgres db
redis db
langsmith
