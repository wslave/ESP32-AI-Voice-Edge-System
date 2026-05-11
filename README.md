# ESP32 本地 AI 语音 Web 控制台

本仓库面向毕业论文《基于ESP32与本地AI上位机的语音交互控制系统的设计与实现》整理，核心目标是提供一个以后端控制和状态联调为主的 Web 管理端，并保留 ESP32 终端固件作为语音采集、播放和设备控制的硬件侧实现。

系统采用“ESP32 语音终端 + 本地 AI 上位机 + Web 控制台”的结构。ESP32 负责麦克风采样、VAD 触发、音频封装、无线传输、语音播放和外设控制；本地上位机负责语音识别、语义解析、命令推理、状态管理和日志记录；Web 控制台用于查看识别文本、设备状态、交互日志、性能指标，并辅助完成局域网环境下的调试和控制。

## 项目结构

- `src/`、`public/`：Web 控制台源码，已放在仓库根目录，便于直接安装、启动和打包。
- `main/`：ESP32 固件核心代码，保留音频、显示、网络、协议、OTA、设置和板级适配等模块。
- `partitions/`、`sdkconfig.defaults*`、`CMakeLists.txt`：ESP-IDF 固件构建配置。
- `scripts/`：固件构建和资源生成相关脚本。

已经移除原硬件项目中与本课题无关的展示文档、CI 模板、多语言首页说明和图片资料。板级驱动目录暂时保留，因为论文没有限定唯一开发板，后续确定具体硬件后可以继续裁剪。

## Web 控制台

在仓库根目录执行：

```bash
npm ci
npm run serve
```

默认开发端口为 `8001`。开发环境会把 `/xiaozhi` 请求代理到 `http://127.0.0.1:8002`，用于连接本地 AI 上位机后端。

生产构建：

```bash
npm run build
```

构建结果输出到 `dist/`，该目录不会提交到 Git。

## ESP32 固件

固件侧代码保留在 `main/`，用于完成语音终端功能：

- 采集麦克风音频并按协议封装传输。
- 接收上位机返回的语音和控制指令。
- 展示连接、唤醒、播放、错误等设备状态。
- 通过 GPIO、LED、显示屏、音频编解码器等模块完成硬件交互。

如需继续精简硬件代码，建议先确定最终开发板型号、屏幕/音频芯片和联网方式，再删除未使用的 `main/boards/*` 适配目录。

## 贡献者

<!-- readme: collaborators,contributors -start -->
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/wslave">
        <img src="https://avatars.githubusercontent.com/wslave?s=100" width="100px;" alt="wslave"/>
        <br />
        <sub><b>wslave</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Charles-0509">
        <img src="https://avatars.githubusercontent.com/Charles-0509?s=100" width="100px;" alt="wslave"/>
        <br />
        <sub><b>wslave</b></sub>
      </a>
    </td>
  </tr>
</table>
<!-- readme: collaborators,contributors -end -->
