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

## 更新 API client 的方法


1. 產 openapi.yaml

自己 build docker

```bash
git clone https://github.com/Mermade/oas-kit
cd oas-kit/packages/swagger2openapi
docker build -t swagger2openapi . --no-cache
```

執行

```bash
docker run --rm -v ${PWD}:/usr/src/app swagger2openapi swagger2openapi --yaml --outfile openapi.yaml https://tst-apolloxe.mayohr.com/backend/platform-bff/swagger/v1/swagger.json
```

用現成的(不建議，版本舊且很慢)

```bash
docker run --rm -v ${PWD}:/usr/src/app mermade/swagger2openapi swagger2openapi --yaml --outfile openapi.yaml https://tst-apolloxe.mayohr.com/backend/platform-bff/swagger/v1/swagger.json
```

2. 用 openapi.yaml 產 code

```bash
uv tool run openapi-python-client generate --path ./openapi.yaml --overwrite --config openapi-python-client.yaml
```

## go to production todo list

服務外圍資源
postgres db
redis db
langsmith
