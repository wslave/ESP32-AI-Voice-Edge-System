<template>
  <div class="device-item">
    <div style="display: flex;justify-content: space-between;">
    <el-tooltip :content="device.agentName" placement="top" effect="light">
      <div class="device-item-title">
        {{ device.agentName }}
      </div>
    </el-tooltip>
      <div>
        <img src="@/assets/home/delete.png" alt="" style="width: 18px;height: 18px;margin-right: 10px;"
          @click.stop="handleDelete" />
        <el-tooltip class="item" effect="light" :content="device.systemPrompt" placement="top"
          popper-class="device-item-tooltip"> 
          <img src="@/assets/home/info.png" alt="" style="width: 18px;height: 18px;" />
        </el-tooltip>
      </div>
    </div>
    <div class="device-name">
      {{ $t('home.languageModel') }}：{{ device.llmModelName }}
    </div>
    <div class="device-name">
      {{ $t('home.voiceModel') }}：{{ device.ttsModelName }} ({{ device.ttsVoiceName }})
    </div>
    <div style="display: flex;gap: 10px;align-items: center;">
      <div class="settings-btn" @click="handleConfigure">
        {{ $t('home.configureRole') }}
      </div>
      <div v-if="featureStatus.voiceprintRecognition" class="settings-btn" @click="handleVoicePrint">
        {{ $t('home.voiceprintRecognition') }}
      </div>
      <div class="settings-btn" @click="handleDeviceManage">
        {{ $t('home.deviceManagement') }}({{ device.deviceCount }})
      </div>
      <div :class="['settings-btn', { 'disabled-btn': device.memModelId === 'Memory_nomem' }]"
        @click="handleChatHistory">
        <el-tooltip effect="light" v-if="device.memModelId === 'Memory_nomem'" :content="$t('home.enableMemory')" placement="top">
          <span>{{ $t('home.chatHistory') }}</span>
        </el-tooltip>
        <span v-else>{{ $t('home.chatHistory') }}</span>
      </div>
    </div>
    <div class="version-info">
      <div>{{ $t('home.lastConversation') }}：{{ formattedLastConnectedTime }}</div>
      <el-tooltip :content="tags.join()" placement="top" effect="light">
        <div class="version-info-scroll">
          {{ tags.join() }}
        </div>
      </el-tooltip>
    </div>
  </div>
</template>

<script>
import i18n from '@/i18n';

export default {
  name: 'DeviceItem',
  props: {
    device: { type: Object, required: true },
    featureStatus: { 
      type: Object, 
      default: () => ({
        voiceprintRecognition: false,
        voiceClone: false,
        knowledgeBase: false
      })
    }
  },
  data() {
    return { switchValue: false }
  },
  computed: {
    formattedLastConnectedTime() {
      if (!this.device.lastConnectedAt) return this.$t('home.noConversation');

      const lastTime = new Date(this.device.lastConnectedAt);
      const now = new Date();
      const diffMinutes = Math.floor((now - lastTime) / (1000 * 60));

      if (diffMinutes <= 1) {
        return this.$t('home.justNow');
      } else if (diffMinutes < 60) {
        return this.$t('home.minutesAgo', { minutes: diffMinutes });
      } else if (diffMinutes < 24 * 60) {
        const hours = Math.floor(diffMinutes / 60);
        const minutes = diffMinutes % 60;
        return this.$t('home.hoursAgo', { hours, minutes });
      } else {
        return this.device.lastConnectedAt;
      }
    },
    tags() {
      if (!this.device.tags) return [];
      return this.device.tags.map((tag) => tag.tagName);
    }
  },
  methods: {
    handleDelete() {
      this.$emit('delete', this.device.agentId)
    },
    handleConfigure() {
      this.$router.push({ path: '/role-config', query: { agentId: this.device.agentId } });
    },
    handleVoicePrint() {
      this.$router.push({ path: '/voice-print', query: { agentId: this.device.agentId } });
    },
    handleDeviceManage() {
      this.$router.push({ path: '/device-management', query: { agentId: this.device.agentId } });
    },
    handleChatHistory() {
      if (this.device.memModelId === 'Memory_nomem') {
        return
      }
      this.$emit('chat-history', { agentId: this.device.agentId, agentName: this.device.agentName })
    }
  },
}
</script>
<style lang="scss" scoped>
.device-item {
  width: 342px;
  min-height: 178px;
  border: 1px solid rgba(14, 15, 12, 0.12);
  border-radius: 30px;
  background: #ffffff;
  padding: 24px 24px 18px;
  box-sizing: border-box;
  box-shadow: rgba(14, 15, 12, 0.12) 0 0 0 1px;
  transition: transform 180ms ease, background-color 180ms ease, border-color 180ms ease;

  &:hover {
    transform: translateY(-2px);
    background: #fbfcf8;
    border-color: rgba(22, 51, 0, 0.24);
  }

  &-title {
    flex: 1;
    font-family: "Wise Sans", Inter, "Helvetica Neue", Arial, sans-serif;
    font-weight: 900;
    font-size: 24px;
    line-height: 0.95;
    color: #0e0f0c;
    text-align: left;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    letter-spacing: 0;
  }
}

.device-name {
  margin: 10px 0;
  font-weight: 700;
  font-size: 13px;
  line-height: 1.35;
  color: #454745;
  text-align: left;
}

.settings-btn {
  font-weight: 800;
  font-size: 12px;
  color: #163300;
  background: rgba(22, 51, 0, 0.08);
  width: auto;
  padding: 0 12px;
  min-height: 26px;
  line-height: 26px;
  cursor: pointer;
  border-radius: 9999px;
  white-space: nowrap;
}

.settings-btn:hover {
  background: #9fe870;
}

.version-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  font-size: 12px;
  color: #868685;
  font-weight: 600;
  &-scroll {
    margin-left: 20px;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    text-wrap: nowrap;
    text-align: right;
  }
}

.more-tag {
  cursor: pointer;
  flex-shrink: 0;
}

.all-tags-popover {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.disabled-btn {
  background: #e8ebe6;
  color: #868685;
  cursor: not-allowed;
}
</style>

<style>
.device-item-tooltip {
  max-height: 60vh !important;
  max-width: 400px !important;
  overflow-y: auto !important;
  scrollbar-width: thin;
  word-break: break-word;
}

.device-item-tooltip .popper__arrow {
  display: none !important;
}

.device-item-tooltip[x-placement^="top"] .popper__arrow {
  border-top-color: transparent !important;
}

.device-item-tooltip[x-placement^="bottom"] .popper__arrow {
  border-bottom-color: transparent !important;
}
</style>
