# ESP32 本地 AI 语音交互控制系统

本仓库对应毕业论文《基于 ESP32 与本地 AI 上位机的语音交互控制系统的设计与实现》，实现形态为 `ESP32 语音终端 + 本地 AI 上位机 + Web 控制台`。代码由 C++ 固件、Python 实时语音服务、Java 管理后端和 Vue 前端组成，目标是完成局域网内的语音采集、识别、语义处理、设备管理、状态监控和测试联调。

## 项目组成

### ESP32 语音终端

- 目录：`hardware/`
- 入口：`hardware/main/main.cc`
- 关键模块：
  - `hardware/main/audio/`：I2S 采样、音频编解码、VAD 前处理
  - `hardware/main/protocols/`：WebSocket / MQTT 协议传输
  - `hardware/main/display/`：屏幕状态显示
  - `hardware/main/led/`：LED 状态反馈
  - `hardware/main/settings.*`：NVS 参数管理

### 本地 AI 上位机

- 目录：`backend/`
- 组成：
  - `backend/xiaozhi-server/`：Python 实时语音服务，负责音频接入、VAD、ASR、LLM、TTS、意图处理和 WebSocket/HTTP 接口
  - `backend/manager-api/`：Spring Boot 管理后端，负责用户、设备、参数、知识库、模型、OTA 和配置管理

### Web 控制台

- 目录：`frontend/`
- 技术栈：Vue 2、Vue Router、Vuex、Element UI
- 页面模块：
  - 设备管理
  - 参数管理
  - 服务端管理
  - 模型配置
  - 知识库管理
  - OTA 管理
  - 声纹与音色资源管理

## 代码架构

```text
ESP32-AI-Voice-Edge-System
├─ frontend/
│  ├─ src/views/                    控制台页面
│  ├─ src/components/               复用组件
│  ├─ src/apis/                     前端接口封装
│  ├─ src/router/                   路由配置
│  └─ vue.config.js                 开发端口与代理配置
├─ backend/
│  ├─ manager-api/
│  │  ├─ src/main/java/xiaozhi/modules/device/      设备与 OTA
│  │  ├─ src/main/java/xiaozhi/modules/config/      参数配置
│  │  ├─ src/main/java/xiaozhi/modules/knowledge/   知识库
│  │  ├─ src/main/java/xiaozhi/modules/agent/       角色、声纹、MCP
│  │  └─ src/main/resources/                        Spring Boot 配置
│  └─ xiaozhi-server/
│     ├─ app.py                     服务主入口
│     ├─ core/                      WebSocket、HTTP、认证与处理链路
│     ├─ config/                    配置加载与日志
│     ├─ plugins_func/              工具调用插件
│     ├─ performance_tester.py      模型性能测试
│     └─ test/test_page.html        音频交互测试页
└─ hardware/
   ├─ CMakeLists.txt                ESP-IDF 工程入口
   ├─ main/application.*            终端主调度
   ├─ main/audio/                   音频处理
   ├─ main/protocols/               终端通信协议
   ├─ main/display/                 界面显示
   ├─ main/boards/                  板级适配
   └─ partitions/                   分区表
```

## 功能模块

| 模块 | 代码位置 | 当前实现 |
| --- | --- | --- |
| 语音采集与上传 | `hardware/main/audio/` | I2S 采样、前导缓冲、VAD 触发、音频分帧上传 |
| 终端通信 | `hardware/main/protocols/` | WebSocket / MQTT 协议封装、状态回传 |
| 终端状态管理 | `hardware/main/application.*`, `device_state_machine.*` | 待机、监听、上传、等待反馈、播放反馈等状态切换 |
| 实时语音服务 | `backend/xiaozhi-server/core/` | WebSocket 会话、HTTP 接口、模型调度、音频返回 |
| 管理后端 | `backend/manager-api/src/main/java/xiaozhi/modules/` | 用户、设备、参数、知识库、OTA、角色与声纹接口 |
| Web 控制台 | `frontend/src/views/` | 参数配置、设备管理、模型管理、运行状态查看 |
| 测试工具 | `backend/xiaozhi-server/performance_tester.py`, `backend/xiaozhi-server/test/test_page.html` | 音频交互测试与模型性能测试 |

## 默认端口与服务关系

| 服务 | 默认地址 | 用途 |
| --- | --- | --- |
| Web 控制台 | `http://127.0.0.1:8001` | 前端页面 |
| 管理后端 `manager-api` | `http://127.0.0.1:8002/xiaozhi` | 管理接口、设备配置、参数管理 |
| 实时语音服务 `xiaozhi-server` | `ws://127.0.0.1:8000/xiaozhi/v1/` | ESP32 语音会话链路 |
| HTTP / OTA / Vision | `http://127.0.0.1:8003` | OTA、视觉分析、辅助 HTTP 接口 |

前端开发模式下通过 `frontend/vue.config.js` 将 `/xiaozhi` 代理到 `http://127.0.0.1:8002`。ESP32 终端默认连接 `xiaozhi-server` 的 WebSocket 接口；如需从管理后端拉取配置，可使用 `backend/xiaozhi-server/config_from_api.yaml`。

## 实验性能

以下数据取自论文联调与测试章节，统计对象为本系统的局域网部署版本。

### 功能与性能指标

| 指标 | 测试结果 |
| --- | --- |
| 语音识别准确率 | `57 / 60`，准确率 `95.0%` |
| 语义理解准确率 | `58 / 60`，准确率 `96.7%` |
| 本地链路端到端平均时延 | `1.18 s` |
| 外部模型链路端到端平均时延 | `1.44 s` |
| GUI 刷新频率 | `27.8 fps` |
| GUI 识别结果显示延迟 | `94 ms` |
| GUI 状态刷新周期 | `1 s / 次` |

### 时延对比

| 测试对象 | 模型/链路 | 样本数 | 平均响应时延 | P95 时延 | 稳定性记录 |
| --- | --- | ---: | ---: | ---: | --- |
| 本系统 | Ollama 本地模型 | 30 | `1186 ms` | `1438 ms` | `30 min` 无掉线 |
| 本系统 | WSL `llama.cpp` 本地模型 | 30 | `1048 ms` | `1295 ms` | `30 min` 无掉线 |
| 星智 CUBE | Qwen 3.5 4G 物联网 | 30 | `1425 ms` | `1760 ms` | `30 min` 无掉线 |
| 星智 CUBE | DeepSeek V3 4G 物联网 | 30 | `2318 ms` | `2860 ms` | `30 min`，1 次重连 |

### 稳定性记录

| 测试时长 | 交互轮次 | 掉线次数 | 重连次数 | 异常日志 | 结果 |
| ---: | ---: | ---: | ---: | ---: | --- |
| `30 min` | 28 | 0 | 0 | 0 | 运行稳定 |
| `60 min` | 53 | 0 | 0 | 1 | 1 次模型超时告警，自动恢复 |
| `120 min` | 102 | 1 | 1 | 1 | 1 次无线连接断开，自动重连恢复 |

### GUI 性能记录

| 指标 | 目标值 | 当前记录值 |
| --- | --- | --- |
| 界面刷新频率 | `>= 5 fps` | `27.8 fps` |
| 识别结果显示延迟 | `<= 200 ms` | `94 ms` |
| 状态刷新周期 | `1 s / 次` | `1 s / 次` |
| 长时日志显示稳定性 | 连续运行无明显卡顿 | `30 min` 无明显卡顿 |

## 运行环境

### 前端

- Node.js `18+`
- npm

### 管理后端

- JDK `21`
- Maven `3.8+`
- MySQL `8.0`
- Redis `5.0+`

### 实时语音服务

- Python `3.10`
- 关键依赖见 [requirements.txt](C:/Users/Wslave/Documents/New%20project/Code/ESP32-AI-Voice-Edge-System/backend/xiaozhi-server/requirements.txt)
- 默认包含 `torch 2.2.2`、`torchaudio 2.2.2`、`funasr 1.2.7`、`silero_vad 6.1.0`

### 硬件固件

- ESP-IDF `5.x`
- 支持 `esp32s3`、`esp32c3` 等目标芯片

## 快速启动

建议启动顺序为：`manager-api -> xiaozhi-server -> frontend -> hardware`

### 1. 启动管理后端

配置文件：

- [application.yml](C:/Users/Wslave/Documents/New%20project/Code/ESP32-AI-Voice-Edge-System/backend/manager-api/src/main/resources/application.yml)
- [application-dev.yml](C:/Users/Wslave/Documents/New%20project/Code/ESP32-AI-Voice-Edge-System/backend/manager-api/src/main/resources/application-dev.yml)

启动命令：

```bash
cd backend/manager-api
mvn spring-boot:run
```

接口文档：

```text
http://127.0.0.1:8002/xiaozhi/doc.html
```

### 2. 启动实时语音服务

核心文件：

- [app.py](C:/Users/Wslave/Documents/New%20project/Code/ESP32-AI-Voice-Edge-System/backend/xiaozhi-server/app.py)
- [config.yaml](C:/Users/Wslave/Documents/New%20project/Code/ESP32-AI-Voice-Edge-System/backend/xiaozhi-server/config.yaml)
- [config_from_api.yaml](C:/Users/Wslave/Documents/New%20project/Code/ESP32-AI-Voice-Edge-System/backend/xiaozhi-server/config_from_api.yaml)

启动命令：

```bash
cd backend/xiaozhi-server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

默认 WebSocket 地址：

```text
ws://127.0.0.1:8000/xiaozhi/v1/
```

### 3. 启动 Web 控制台

启动命令：

```bash
cd frontend
npm ci
npm run serve
```

访问地址：

```text
http://127.0.0.1:8001
```

生产构建：

```bash
cd frontend
npm run build
```

### 4. 编译与烧录 ESP32 固件

启动命令：

```bash
cd hardware
idf.py set-target <chip>
idf.py build
idf.py -p <port> flash monitor
```

## 配置文件

### `backend/manager-api`

默认开发配置：

- 端口：`8002`
- Context Path：`/xiaozhi`
- MySQL：`127.0.0.1:3306/xiaozhi_esp32_server`
- Redis：`127.0.0.1:6379`

### `backend/xiaozhi-server`

默认配置：

- `server.port: 8000`
- `server.http_port: 8003`
- `server.websocket: ws://你的ip或者域名:端口号/xiaozhi/v1/`
- 支持 `config.yaml` 本地配置
- 支持 `data/.config.yaml` 覆盖配置
- 支持 `config_from_api.yaml` 从 `manager-api` 拉取参数

### `frontend`

`frontend/vue.config.js` 默认配置：

- 开发端口：`8001`
- `/xiaozhi` 代理目标：`http://127.0.0.1:8002`

## 测试工具

| 工具 | 位置 | 用途 |
| --- | --- | --- |
| 音频交互测试页 | `backend/xiaozhi-server/test/test_page.html` | 验证 WebSocket 音频收发与播放 |
| 模型性能测试 | `backend/xiaozhi-server/performance_tester.py` | 测试 ASR、LLM、VLLM、TTS 响应速度 |
| 接口文档 | `http://127.0.0.1:8002/xiaozhi/doc.html` | 查看管理后端接口 |

## 代码行变更占比

下图统计 README 中列出的两位贡献者在当前仓库历史中的代码行变更量占比，统计方式基于 `git log --numstat` 汇总代码类文件的新增行与删除行之和，并自动合并以下作者别名：

- `Wslave / Xu DeJia / 许德佳`
- `Charles / Charles-0509`

该图会在每次推送到 `main` 后由 GitHub Actions 自动重新生成，并发布到仓库的 `gh-pages` 分支，不再通过 bot 提交去改 README 本身。

统计口径：`main` 分支全部历史提交，代码类文件新增行与删除行之和。

![代码行变更占比](https://github.com/wslave/ESP32-AI-Voice-Edge-System/blob/gh-pages/contribution-line-share.svg?raw=1)

静态备份图：[`contribution-line-share.svg`](./.github/pages/contribution-line-share.svg)

## 贡献者

<!-- readme: collaborators,contributors -start -->
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/wslave">
        <img src="https://avatars.githubusercontent.com/wslave?s=100" width="100px;" alt="Wslave"/>
        <br />
        <sub><b>Wslave</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Charles-0509">
        <img src="https://avatars.githubusercontent.com/Charles-0509?s=100" width="100px;" alt="Charles-0509"/>
        <br />
        <sub><b>Charles-0509</b></sub>
      </a>
    </td>
  </tr>
</table>
<!-- readme: collaborators,contributors -end -->
