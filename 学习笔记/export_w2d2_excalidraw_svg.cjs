const fs = require("fs");
const path = require("path");

const diagramsDir = path.join(__dirname, "diagrams");

function escapeXml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function bounds(elements) {
  const visible = elements.filter((el) => !el.isDeleted);
  const minX = Math.min(...visible.map((el) => el.x));
  const minY = Math.min(...visible.map((el) => el.y));
  const maxX = Math.max(...visible.map((el) => el.x + (el.width || 0)));
  const maxY = Math.max(...visible.map((el) => el.y + (el.height || 0)));
  return { minX, minY, maxX, maxY, width: maxX - minX, height: maxY - minY };
}

function color(el) {
  return el.backgroundColor && el.backgroundColor !== "transparent" ? el.backgroundColor : "none";
}

function renderText(el, offsetX, offsetY) {
  const lines = String(el.text || "").split("\n");
  const fontSize = el.fontSize || 24;
  const lineHeight = fontSize * (el.lineHeight || 1.25);
  const anchor = el.textAlign === "center" ? "middle" : el.textAlign === "right" ? "end" : "start";
  const x = el.x - offsetX;
  const y = el.y - offsetY;
  const startX = anchor === "middle" ? x : x;
  const baselineOffset = el.verticalAlign === "middle" ? -((lines.length - 1) * lineHeight) / 2 : 0;
  return `<text x="${startX}" y="${y + baselineOffset}" text-anchor="${anchor}" dominant-baseline="${el.verticalAlign === "middle" ? "middle" : "hanging"}" font-family="Segoe Print, Comic Sans MS, cursive" font-size="${fontSize}" fill="${el.strokeColor || "#1e1e1e"}">${lines
    .map((line, index) => `<tspan x="${startX}" dy="${index === 0 ? 0 : lineHeight}">${escapeXml(line)}</tspan>`)
    .join("")}</text>`;
}

function renderElement(el, offsetX, offsetY) {
  const x = el.x - offsetX;
  const y = el.y - offsetY;
  const stroke = el.strokeColor || "#1e1e1e";
  const fill = color(el);
  const sw = el.strokeWidth || 2;

  if (el.type === "rectangle") {
    return `<rect x="${x}" y="${y}" width="${el.width}" height="${el.height}" rx="12" ry="12" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  }
  if (el.type === "diamond") {
    const points = [
      [x + el.width / 2, y],
      [x + el.width, y + el.height / 2],
      [x + el.width / 2, y + el.height],
      [x, y + el.height / 2],
    ]
      .map((p) => p.join(","))
      .join(" ");
    return `<polygon points="${points}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  }
  if (el.type === "text") {
    return renderText(el, offsetX, offsetY);
  }
  if (el.type === "arrow") {
    const points = el.points || [
      [0, 0],
      [el.width, el.height],
    ];
    const d = points.map(([px, py], i) => `${i === 0 ? "M" : "L"} ${x + px} ${y + py}`).join(" ");
    return `<path d="${d}" fill="none" stroke="${stroke}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arrowhead)"/>`;
  }
  return "";
}

function exportScene(fileName) {
  const input = path.join(diagramsDir, fileName);
  const scene = JSON.parse(fs.readFileSync(input, "utf8"));
  const b = bounds(scene.elements);
  const margin = 48;
  const width = Math.ceil(b.width + margin * 2);
  const height = Math.ceil(b.height + margin * 2);
  const offsetX = b.minX - margin;
  const offsetY = b.minY - margin;
  const body = scene.elements
    .filter((el) => !el.isDeleted)
    .map((el) => renderElement(el, offsetX, offsetY))
    .filter(Boolean)
    .join("\n  ");
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
      <path d="M 0 0 L 10 4 L 0 8 z" fill="#1e1e1e"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="#fffdf8"/>
  ${body}
</svg>
`;
  const output = path.join(diagramsDir, fileName.replace(".excalidraw", "-excalidraw-export.svg"));
  fs.writeFileSync(output, svg, "utf8");
}

[
  "w2d2-context-map.excalidraw",
  "w2d2-prompt-template.excalidraw",
  "w2d2-ask-vs-template.excalidraw",
  "w2d2-chat-context.excalidraw",
].forEach(exportScene);
