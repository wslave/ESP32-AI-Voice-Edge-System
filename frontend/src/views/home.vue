<template>
  <div class="welcome">
    <!-- 公共头部 -->
    <HeaderBar :devices="devices" @search="handleSearch" @search-reset="handleSearchReset" />
    <el-main style="padding: 20px;display: flex;flex-direction: column;">
      <div>
        <!-- 首页内容 -->
        <div class="add-device">
          <div class="add-device-bg">
            <div class="hellow-text" style="margin-top: 30px;">
              {{ $t('home.greeting') }}
            </div>
            <div class="hellow-text">
              {{ $t('home.wish') }}
            </div>
            <div class="hi-hint">
              let's have a wonderful day!
            </div>
            <div class="add-device-btn">
              <div class="left-add" @click="showAddDialog">
                {{ $t('home.addAgent') }}
              </div>
              <div class="add-device-btn-bridge" />
              <div class="right-add">
                <i class="el-icon-right" @click="showAddDialog" style="font-size: 20px;color: #163300;" />
              </div>
            </div>
          </div>
        </div>
        <section class="ops-overview" aria-label="系统运行概览">
          <div class="overview-card overview-card--dark">
            <div class="metric-label">智能体总数</div>
            <div class="metric-value">{{ dashboardStats.agentCount }}</div>
            <div class="metric-note">{{ isSearching ? '当前为搜索结果' : '已加载工作台列表' }}</div>
          </div>
          <div class="overview-card">
            <div class="metric-label">已绑定设备</div>
            <div class="metric-value">{{ dashboardStats.deviceCount }}</div>
            <div class="metric-note">跨全部智能体统计</div>
          </div>
          <div class="overview-card">
            <div class="metric-label">启用能力</div>
            <div class="metric-value">{{ dashboardStats.enabledFeatureCount }}/3</div>
            <div class="metric-note">{{ dashboardStats.enabledFeatureNames }}</div>
          </div>
          <div class="overview-card">
            <div class="metric-label">待唤醒会话</div>
            <div class="metric-value">{{ dashboardStats.idleAgentCount }}</div>
            <div class="metric-note">暂无最近对话的智能体</div>
          </div>
        </section>
        <section class="ops-strip" aria-label="快捷运维入口">
          <div class="ops-strip__left">
            <span class="ops-dot"></span>
            <span>本地服务</span>
            <strong>Web 8001</strong>
            <strong>API 8002</strong>
            <strong>Device 8000</strong>
          </div>
          <div class="ops-strip__actions">
            <button type="button" @click="fetchAgentList">
              <i class="el-icon-refresh"></i>
              <span>刷新</span>
            </button>
            <button type="button" @click="handleDeviceManage">
              <i class="el-icon-cpu"></i>
              <span>设备</span>
            </button>
            <button type="button" @click="showAddDialog">
              <i class="el-icon-plus"></i>
              <span>智能体</span>
            </button>
          </div>
        </section>
        <div class="device-list-container">
          <template v-if="isLoading">
            <div v-for="i in skeletonCount" :key="'skeleton-' + i" class="skeleton-item">
              <div class="skeleton-image"></div>
              <div class="skeleton-content">
                <div class="skeleton-line"></div>
                <div class="skeleton-line-short"></div>
              </div>
            </div>
          </template>

          <template v-else>
            <DeviceItem v-for="(item, index) in devices" :key="index" :device="item" :feature-status="featureStatus" 
              @configure="goToRoleConfig" @deviceManage="handleDeviceManage" @delete="handleDeleteAgent" 
              @chat-history="handleShowChatHistory" />
          </template>
        </div>
      </div>
      <AddWisdomBodyDialog :visible.sync="addDeviceDialogVisible" @confirm="handleWisdomBodyAdded" />
    </el-main>
    <el-footer>
      <version-footer />
    </el-footer>
    <chat-history-dialog :visible.sync="showChatHistory" :agent-id="currentAgentId" :agent-name="currentAgentName" />
  </div>

</template>

<script>
import Api from '@/apis/api';
import AddWisdomBodyDialog from '@/components/AddWisdomBodyDialog.vue';
import ChatHistoryDialog from '@/components/ChatHistoryDialog.vue';
import DeviceItem from '@/components/DeviceItem.vue';
import HeaderBar from '@/components/HeaderBar.vue';
import VersionFooter from '@/components/VersionFooter.vue';
import featureManager from '@/utils/featureManager';

export default {
  name: 'HomePage',
  components: { DeviceItem, AddWisdomBodyDialog, HeaderBar, VersionFooter, ChatHistoryDialog },
  data() {
    return {
      addDeviceDialogVisible: false,
      devices: [],
      originalDevices: [],
      isSearching: false,
      searchRegex: null,
      isLoading: true,
      skeletonCount: localStorage.getItem('skeletonCount') || 8,
      showChatHistory: false,
      currentAgentId: '',
      currentAgentName: '',
      // 功能状态
      featureStatus: {
        voiceprintRecognition: false,
        voiceClone: false,
        knowledgeBase: false
      }
    }
  },

  async mounted() {
    this.fetchAgentList();
    await this.loadFeatureStatus();
  },

  computed: {
    dashboardStats() {
      const enabledFeatures = [
        { enabled: this.featureStatus.voiceprintRecognition, label: '声纹' },
        { enabled: this.featureStatus.voiceClone, label: '复刻' },
        { enabled: this.featureStatus.knowledgeBase, label: '知识库' }
      ].filter(item => item.enabled);

      return {
        agentCount: this.devices.length,
        deviceCount: this.devices.reduce((total, item) => total + Number(item.deviceCount || 0), 0),
        enabledFeatureCount: enabledFeatures.length,
        enabledFeatureNames: enabledFeatures.length ? enabledFeatures.map(item => item.label).join(' / ') : '基础模式',
        idleAgentCount: this.devices.filter(item => !item.lastConnectedAt).length
      };
    }
  },

  methods: {
    // 加载功能状态
    async loadFeatureStatus() {
      await featureManager.waitForInitialization();
      const config = featureManager.getConfig();
      this.featureStatus = {
        voiceprintRecognition: config.voiceprintRecognition,
        voiceClone: config.voiceClone,
        knowledgeBase: config.knowledgeBase
      };
    },
    
    showAddDialog() {
      this.addDeviceDialogVisible = true
    },
    goToRoleConfig() {
      // 点击配置角色后跳转到角色配置页
      this.$router.push('/role-config')
    },
    handleWisdomBodyAdded(res) {
      this.fetchAgentList();
      this.addDeviceDialogVisible = false;
    },
    handleDeviceManage() {
      this.$router.push('/device-management');
    },
    handleSearch(keyword) {
      this.isSearching = true;
      this.isLoading = true;
      // 检测MAC地址格式：包含4个冒号
      const isMac = /^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$/.test(keyword)
      const searchType = isMac ? 'mac' : 'name';
      Api.agent.searchAgent(keyword, searchType, ({ data }) => {
        if (data?.data) {
          this.devices = data.data.map(item => ({
            ...item,
            agentId: item.id
          }));
        }
        this.isLoading = false;
      }, (error) => {
        console.error('搜索智能体失败:', error);
        this.isLoading = false;
        this.$message.error(this.$t('message.searchFailed'));
      });
    },
    handleSearchReset() {
      this.isSearching = false;
      // 直接将原始设备列表赋值给显示设备列表，避免重新加载数据
      this.devices = [...this.originalDevices];
    },

    // 搜索更新智能体列表
    handleSearchResult(filteredList) {
      this.devices = filteredList; // 更新设备列表
    },
    // 获取智能体列表
    fetchAgentList() {
      this.isLoading = true;
      Api.agent.getAgentList(({ data }) => {
        if (data?.data) {
          this.originalDevices = data.data.map(item => ({
            ...item,
            agentId: item.id
          }));

          // 动态设置骨架屏数量（可选）
          this.skeletonCount = Math.min(
            Math.max(this.originalDevices.length, 3), // 最少3个
            10 // 最多10个
          );

          this.handleSearchReset();
        }
        this.isLoading = false;
      }, (error) => {
        console.error('Failed to fetch agent list:', error);
        this.isLoading = false;
      });
    },
    // 删除智能体
    handleDeleteAgent(agentId) {
      this.$confirm(this.$t('home.confirmDeleteAgent'), '提示', {
        confirmButtonText: this.$t('button.ok'),
        cancelButtonText: this.$t('button.cancel'),
        type: 'warning'
      }).then(() => {
        Api.agent.deleteAgent(agentId, (res) => {
          if (res.data.code === 0) {
            this.$message.success({
              message: this.$t('home.deleteSuccess'),
              showClose: true
            });
            this.fetchAgentList(); // 刷新列表
          } else {
            this.$message.error({
              message: res.data.msg || this.$t('home.deleteFailed'),
              showClose: true
            });
          }
        });
      }).catch(() => { });
    },
    handleShowChatHistory({ agentId, agentName }) {
      this.currentAgentId = agentId;
      this.currentAgentName = agentName;
      this.showChatHistory = true;
    }
  }
}
</script>

<style scoped>
.welcome {
  min-width: 900px;
  min-height: 506px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 12% 10%, rgba(159, 232, 112, 0.2), transparent 30%),
    linear-gradient(180deg, #ffffff 0%, #fbfcf8 52%, #f2f5ef 100%);
  background-size: cover;
  /* 确保背景图像覆盖整个元素 */
  background-position: center;
  /* 从顶部中心对齐 */
  -webkit-background-size: cover;
  /* 兼容老版本WebKit浏览器 */
  -o-background-size: cover;
  /* 兼容老版本Opera浏览器 */
}

.add-device {
  min-height: 230px;
  border-radius: 40px;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 82% 18%, rgba(255, 192, 145, 0.32), transparent 24%),
    linear-gradient(135deg, #e2f6d5 0%, #fbfcf8 48%, #ffffff 100%);
  border: 1px solid rgba(14, 15, 12, 0.12);
  box-shadow: rgba(14, 15, 12, 0.12) 0 0 0 1px;
}

.add-device-bg {
  width: 100%;
  height: 100%;
  text-align: left;
  background-image: url("@/assets/home/main-top-bg.png");
  overflow: hidden;
  background-size: cover;
  /* 确保背景图像覆盖整个元素 */
  background-position: center;
  /* 从顶部中心对齐 */
  -webkit-background-size: cover;
  /* 兼容老版本WebKit浏览器 */
  -o-background-size: cover;
  box-sizing: border-box;

  /* 兼容老版本Opera浏览器 */
  .hellow-text {
    margin-left: 75px;
    color: #0e0f0c;
    font-family: "Wise Sans", Inter, "Helvetica Neue", Arial, sans-serif;
    font-size: 54px;
    font-weight: 900;
    line-height: 0.88;
    letter-spacing: 0;
  }

  .hi-hint {
    font-weight: 700;
    font-size: 15px;
    text-align: left;
    color: #454745;
    margin-left: 75px;
    margin-top: 12px;
  }
}

.add-device-btn {
  display: flex;
  align-items: center;
  margin-left: 75px;
  margin-top: 22px;
  cursor: pointer;
  width: fit-content;
  transition: transform 180ms ease;

  &:hover {
    transform: scale(1.05);
  }

  &:active {
    transform: scale(0.95);
  }

  .left-add {
    padding: 0 18px;
    height: 40px;
    border-radius: 9999px;
    background: #9fe870;
    color: #163300;
    font-size: 15px;
    font-weight: 800;
    text-align: center;
    line-height: 40px;
  }

  .add-device-btn-bridge {
    width: 20px;
    height: 14px;
    background: #9fe870;
    margin-left: -10px;
  }

  .right-add {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #9fe870;
    margin-left: -6px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}

.device-list-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  padding: 28px 0;
}

.ops-overview {
  display: grid;
  grid-template-columns: 1.35fr repeat(3, minmax(160px, 1fr));
  gap: 14px;
  margin: 18px 0 12px;
}

.overview-card {
  min-height: 116px;
  padding: 18px 20px;
  border: 1px solid rgba(14, 15, 12, 0.12);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: rgba(14, 15, 12, 0.08) 0 1px 0;
}

.overview-card--dark {
  background: #163300;
  color: #ffffff;

  .metric-label,
  .metric-note {
    color: rgba(255, 255, 255, 0.72);
  }
}

.metric-label {
  color: #454745;
  font-size: 13px;
  font-weight: 800;
}

.metric-value {
  margin-top: 10px;
  color: inherit;
  font-family: "Wise Sans", Inter, "Helvetica Neue", Arial, sans-serif;
  font-size: 38px;
  font-weight: 900;
  line-height: 0.95;
  letter-spacing: 0;
}

.metric-note {
  min-height: 18px;
  margin-top: 10px;
  color: #868685;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ops-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 58px;
  padding: 10px 12px 10px 18px;
  border: 1px solid rgba(14, 15, 12, 0.12);
  border-radius: 20px;
  background: #ffffff;
}

.ops-strip__left,
.ops-strip__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.ops-strip__left {
  color: #454745;
  font-size: 13px;
  font-weight: 800;

  strong {
    padding: 7px 10px;
    border-radius: 9999px;
    background: rgba(22, 51, 0, 0.08);
    color: #163300;
    font-size: 12px;
    white-space: nowrap;
  }
}

.ops-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #9fe870;
  box-shadow: 0 0 0 5px rgba(159, 232, 112, 0.25);
}

.ops-strip__actions button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 36px;
  padding: 0 13px;
  border: 0;
  border-radius: 9999px;
  background: #9fe870;
  color: #163300;
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
}

/* 在 DeviceItem.vue 的样式中 */
.device-item {
  margin: 0 !important;
  /* 避免冲突 */
  width: auto !important;
}

.footer {
  font-size: 12px;
  font-weight: 400;
  margin-top: auto;
  padding-top: 30px;
  color: #979db1;
  text-align: center;
  /* 居中显示 */
}

/* 骨架屏动画 */
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

.skeleton-item {
  background: #fff;
  border: 1px solid rgba(14, 15, 12, 0.12);
  border-radius: 30px;
  padding: 20px;
  height: 120px;
  position: relative;
  overflow: hidden;
  margin-bottom: 20px;
}

.skeleton-image {
  width: 80px;
  height: 80px;
  background: #e8ebe6;
  border-radius: 20px;
  float: left;
  position: relative;
  overflow: hidden;
}

.skeleton-content {
  margin-left: 100px;
}

.skeleton-line {
  height: 16px;
  background: #e8ebe6;
  border-radius: 9999px;
  margin-bottom: 12px;
  width: 70%;
  position: relative;
  overflow: hidden;
}

.skeleton-line-short {
  height: 12px;
  background: #e8ebe6;
  border-radius: 9999px;
  width: 50%;
}

.skeleton-item::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg,
      rgba(255, 255, 255, 0),
      rgba(255, 255, 255, 0.3),
      rgba(255, 255, 255, 0));
  animation: shimmer 1.5s infinite;
}
</style>
