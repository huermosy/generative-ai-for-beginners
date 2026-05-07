const fs = require("fs");
const path = require("path");

const outDir = path.join(__dirname, "diagrams");

function id(prefix) {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`;
}

function base(el) {
  return {
    id: el.id || id(el.type),
    type: el.type,
    x: el.x,
    y: el.y,
    width: el.width || 0,
    height: el.height || 0,
    angle: 0,
    strokeColor: el.strokeColor || "#1e1e1e",
    backgroundColor: el.backgroundColor || "transparent",
    fillStyle: "hachure",
    strokeWidth: el.strokeWidth || 2,
    strokeStyle: "solid",
    roughness: 1,
    opacity: 100,
    groupIds: [],
    frameId: null,
    roundness: el.roundness || { type: 3 },
    seed: Math.floor(Math.random() * 1000000),
    version: 1,
    versionNonce: Math.floor(Math.random() * 1000000),
    isDeleted: false,
    boundElements: null,
    updated: 1,
    link: null,
    locked: false,
    customData: {},
  };
}

function rect(x, y, width, height, label, bg = "#fff9db") {
  const r = base({ type: "rectangle", x, y, width, height, backgroundColor: bg });
  return [r, text(x + width / 2, y + height / 2, label, 24, "center", "middle")];
}

function diamond(x, y, width, height, label, bg = "#e7f5ff") {
  const d = base({ type: "diamond", x, y, width, height, backgroundColor: bg });
  return [d, text(x + width / 2, y + height / 2, label, 22, "center", "middle")];
}

function text(x, y, value, fontSize = 24, textAlign = "left", verticalAlign = "top") {
  return {
    ...base({ type: "text", x, y, width: 10, height: 10, roundness: null }),
    text: value,
    fontSize,
    fontFamily: 1,
    textAlign,
    verticalAlign,
    containerId: null,
    originalText: value,
    lineHeight: 1.25,
    autoResize: true,
  };
}

function arrow(x1, y1, x2, y2, label) {
  const a = {
    ...base({
      type: "arrow",
      x: x1,
      y: y1,
      width: x2 - x1,
      height: y2 - y1,
      roundness: { type: 2 },
    }),
    points: [
      [0, 0],
      [x2 - x1, y2 - y1],
    ],
    lastCommittedPoint: null,
    startBinding: null,
    endBinding: null,
    startArrowhead: null,
    endArrowhead: "arrow",
    elbowed: false,
  };
  return label ? [a, text((x1 + x2) / 2, (y1 + y2) / 2 - 26, label, 18, "center")] : [a];
}

function file(name, elements) {
  const scene = {
    type: "excalidraw",
    version: 2,
    source: "https://excalidraw.com",
    elements,
    appState: {
      gridSize: null,
      viewBackgroundColor: "#fffdf8",
      currentItemFontFamily: 1,
    },
    files: {},
  };
  fs.writeFileSync(path.join(outDir, name), JSON.stringify(scene, null, 2), "utf8");
}

function contextMap() {
  const els = [
    text(340, 34, "W2D2：上下文是什么", 38, "center"),
    ...rect(360, 260, 300, 130, "上下文\n模型回答前的背景信息", "#e7f5ff"),
    ...rect(70, 130, 260, 110, "任务上下文\n这次要做什么", "#fff3bf"),
    ...rect(760, 130, 260, 110, "用户上下文\n答案给谁看", "#d3f9d8"),
    ...rect(70, 460, 260, 110, "资料上下文\n依据哪些材料", "#ffe3e3"),
    ...rect(760, 460, 260, 110, "对话上下文\n前面聊过什么", "#e5dbff"),
    ...arrow(330, 190, 430, 278),
    ...arrow(760, 190, 650, 278),
    ...arrow(330, 515, 430, 380),
    ...arrow(760, 515, 650, 380),
    text(160, 650, "记忆点：不是信息越多越好，而是越相关越好。", 28),
  ];
  file("w2d2-context-map.excalidraw", els);
}

function promptTemplate() {
  const els = [
    text(315, 34, "W2D2：Prompt 模板结构", 38, "center"),
    ...rect(90, 125, 240, 92, "Role\n你是谁", "#fff3bf"),
    ...rect(90, 250, 240, 92, "Task\n要做什么", "#d3f9d8"),
    ...rect(90, 375, 240, 92, "User Profile\n给谁看", "#e7f5ff"),
    ...rect(90, 500, 240, 92, "Context\n依据什么", "#ffe3e3"),
    ...rect(90, 625, 240, 92, "Output + Constraints\n输出格式与限制", "#e5dbff"),
    ...rect(530, 280, 360, 180, "可复用 Prompt 模板\n\n固定稳定部分\n替换变量部分\n重复任务更稳定", "#fff9db"),
    ...arrow(330, 170, 530, 315),
    ...arrow(330, 295, 530, 345),
    ...arrow(330, 420, 530, 375),
    ...arrow(330, 545, 530, 405),
    ...arrow(330, 670, 530, 435),
    text(470, 560, "{{role}} + {{task}} + {{context}} + {{output_format}}", 26),
  ];
  file("w2d2-prompt-template.excalidraw", els);
}

function askVsTemplate() {
  const els = [
    text(315, 34, "W2D2：普通提问 vs 模板化提问", 36, "center"),
    ...rect(90, 160, 330, 340, "普通提问\n\n请解释 Prompt 模板\n\n优点：快\n问题：容易泛\n问题：格式不稳\n问题：不方便复用", "#ffe3e3"),
    ...rect(650, 160, 330, 340, "模板化提问\n\n角色 + 任务\n用户背景 + 上下文\n输出格式 + 约束\n\n结果：更稳定\n结果：更贴题\n结果：可复用", "#d3f9d8"),
    ...arrow(440, 330, 630, 330, "加结构"),
    text(280, 585, "普通提问适合探索；模板化提问适合做工具和产品。", 28),
  ];
  file("w2d2-ask-vs-template.excalidraw", els);
}

function chatContext() {
  const els = [
    text(320, 34, "W2D2：聊天应用里的上下文管理", 36, "center"),
    ...rect(80, 145, 320, 100, "历史消息 1\n自我介绍", "#f1f3f5"),
    ...rect(80, 280, 320, 100, "历史消息 2\n无关闲聊", "#f1f3f5"),
    ...rect(80, 415, 320, 100, "历史消息 3\n当前任务约束", "#fff3bf"),
    ...diamond(510, 285, 220, 160, "筛选\n相关吗？", "#e7f5ff"),
    ...rect(830, 145, 300, 120, "保留\n任务目标\n用户水平\n关键约束", "#d3f9d8"),
    ...rect(830, 395, 300, 120, "丢弃或压缩\n无关闲聊\n过旧信息\n敏感信息", "#ffe3e3"),
    ...arrow(400, 195, 525, 310),
    ...arrow(400, 330, 510, 340),
    ...arrow(400, 465, 525, 375),
    ...arrow(730, 315, 830, 205, "相关"),
    ...arrow(730, 360, 830, 455, "无关"),
    text(190, 635, "上下文管理不是全保留，而是保留当前任务真正需要的。", 28),
  ];
  file("w2d2-chat-context.excalidraw", els);
}

contextMap();
promptTemplate();
askVsTemplate();
chatContext();
