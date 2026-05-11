# ESP32-AI-Voice-Edge-System

基于 ESP32 与本地 AI 上位机的语音交互控制系统。项目面向局域网环境中的低成本语音终端应用，关注语音采集、网络传输、本地模型调用、状态反馈和 GUI 调试能否稳定衔接。

系统采用端边协同结构：ESP32 语音终端负责麦克风采样、VAD 触发、音频分帧、无线传输和语音播报；本地上位机负责音频流接收、语音识别、语义解析、指令推理和运行状态管理；管理界面用于显示设备状态、识别文本、交互日志、模型配置和性能信息。通过这种分工，系统可以在不长期依赖外部云端保存或转发主要语音数据的情况下，完成一次完整的语音交互闭环。

## 主要功能

- ESP32 语音终端接入：支持 WebSocket/OTA 接入、设备状态维护和语音链路调试。
- 本地 AI 处理链路：支持 ASR、LLM、TTS、VAD、记忆和工具调用等模块化配置。
- GUI 管理与观测：提供设备管理、角色配置、模型配置、知识库、日志和会话记录等页面。
- 联调与性能分析：保留测试页面和性能测试脚本，便于观察端到端延迟、识别准确率、通信稳定性和界面刷新表现。
- 局域网部署：适合毕业设计、教学演示、智慧实验室和轻量级控制终端原型。

## 目录结构

```text
main/
  xiaozhi-server/   Python 语音交互服务端，负责 WebSocket、ASR/LLM/TTS、VAD 和工具调用
  manager-api/      Java 管理后端，负责用户、设备、模型、配置和日志数据
  manager-web/      Vue 管理前端，用于浏览器端配置与状态监控
  manager-mobile/   移动端管理界面
docs/               部署、模型和功能扩展文档
```

> 说明：上游项目中部分目录名和 API 路径仍保留 `xiaozhi`，这是为了减少重命名对部署脚本、数据库迁移和设备协议的影响。用户可见的项目说明、默认角色描述和管理端显示文本已按本课题“ESP32 与本地 AI 上位机语音交互控制系统”的定位调整。

## 快速运行

### Python 语音服务

```bash
cd main/xiaozhi-server
pip install -r requirements.txt
python app.py
```

默认 WebSocket 服务端口为 `8000`，OTA/HTTP 端口为 `8003`。实际部署时建议在 `main/xiaozhi-server/data/.config.yaml` 中覆盖本机 IP、模型供应商、密钥和语音参数。

### 管理后端

```bash
cd main/manager-api
mvn spring-boot:run
```

默认管理 API 路径为 `/xiaozhi`，端口配置见 `main/manager-api/src/main/resources/application.yml`。

### 管理前端

```bash
cd main/manager-web
npm install
npm run serve
```

生产构建可执行：

```bash
npm run build
```

## 课题定位

本项目对应的研究主题为“基于 ESP32 与本地 AI 上位机的语音交互控制系统的设计与实现”。实现重点不是单独证明某个算法最优，而是把采音、传输、识别、推理、反馈和显示组织成可调试、可观察、可复现的工程链路。
