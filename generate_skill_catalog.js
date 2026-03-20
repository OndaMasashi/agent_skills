const fs = require("fs");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  Header,
  Footer,
  AlignmentType,
  HeadingLevel,
  BorderStyle,
  WidthType,
  ShadingType,
  PageNumber,
  PageBreak,
  NumberFormat,
  LevelFormat,
} = require("docx");

// ===== Configuration =====
const VERSION = 6;
const OUTPUT_PATH = `${__dirname}/skill_catalog_v${VERSION}.docx`;
const CREATED_DATE = "2026-03-20";

// Color palette (same as project catalog)
const COLORS = {
  primary: "1F4E79",
  accent: "2E75B6",
  lightBg: "D6E4F0",
  headerBg: "1F4E79",
  headerText: "FFFFFF",
  border: "B4C6E7",
  text: "333333",
  subtext: "666666",
};

const border = { style: BorderStyle.SINGLE, size: 1, color: COLORS.border };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

// A4 with 1" margins => content width = 11906 - 2880 = 9026
const CONTENT_WIDTH = 9026;

// Table column widths: No.(500) + Name(1600) + Keywords(2126) + UseCase(2400) + Features(2400) = 9026
const COL_WIDTHS = [500, 1600, 2126, 2400, 2400];

// ===== Helper Functions =====
function headerCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: COLORS.headerBg, type: ShadingType.CLEAR },
    margins: cellMargins,
    verticalAlign: "center",
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text,
            bold: true,
            color: COLORS.headerText,
            font: "Arial",
            size: 20,
          }),
        ],
      }),
    ],
  });
}

function dataCell(text, width, opts = {}) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: opts.shading
      ? { fill: opts.shading, type: ShadingType.CLEAR }
      : undefined,
    margins: cellMargins,
    children: [
      new Paragraph({
        alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
        children: [
          new TextRun({
            text,
            font: "Arial",
            size: 18,
            color: COLORS.text,
            ...(opts.bold ? { bold: true } : {}),
          }),
        ],
      }),
    ],
  });
}

function categorySection(cat) {
  const elements = [];

  // Category heading
  elements.push(
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      children: [new TextRun({ text: cat.title })],
    }),
  );

  // Category description
  elements.push(
    new Paragraph({
      spacing: { after: 120 },
      children: [
        new TextRun({
          text: cat.description,
          font: "Arial",
          size: 20,
          color: COLORS.subtext,
          italics: true,
        }),
      ],
    }),
  );

  // Table header row
  const headerRow = new TableRow({
    children: [
      headerCell("No.", COL_WIDTHS[0]),
      headerCell("\u30B9\u30AD\u30EB\u540D", COL_WIDTHS[1]),
      headerCell(
        "\u547C\u3073\u51FA\u3057\u30AD\u30FC\u30EF\u30FC\u30C9",
        COL_WIDTHS[2],
      ),
      headerCell("\u30E6\u30FC\u30B9\u30B1\u30FC\u30B9", COL_WIDTHS[3]),
      headerCell("\u6A5F\u80FD\u30FB\u7279\u5FB4", COL_WIDTHS[4]),
    ],
  });

  // Data rows
  const dataRows = cat.skills.map((s, i) => {
    const bg = i % 2 === 1 ? COLORS.lightBg : undefined;
    return new TableRow({
      children: [
        dataCell(String(i + 1), COL_WIDTHS[0], { center: true, shading: bg }),
        dataCell(s.name, COL_WIDTHS[1], { bold: true, shading: bg }),
        dataCell(s.keywords, COL_WIDTHS[2], { shading: bg }),
        dataCell(s.useCase, COL_WIDTHS[3], { shading: bg }),
        dataCell(s.features, COL_WIDTHS[4], { shading: bg }),
      ],
    });
  });

  elements.push(
    new Table({
      width: { size: CONTENT_WIDTH, type: WidthType.DXA },
      columnWidths: COL_WIDTHS,
      rows: [headerRow, ...dataRows],
    }),
  );

  elements.push(new Paragraph({ spacing: { after: 300 }, children: [] }));
  return elements;
}

// ===== Skill Data =====
const categories = [
  {
    title: "\u30C9\u30AD\u30E5\u30E1\u30F3\u30C8\u95A2\u9023 (Document Skills)",
    description:
      "\u6587\u66F8\u306E\u4F5C\u6210\u3001\u7DE8\u96C6\u3001\u5206\u6790\u3001\u5909\u63DB\u306A\u3069\u3092\u884C\u3046\u30B9\u30AD\u30EB\u3067\u3059\u3002",
    skills: [
      {
        name: "Word (DOCX)",
        keywords:
          "\u300CWord\u3092\u4F5C\u6210\u300D\u300C\u30EC\u30DD\u30FC\u30C8\u3092docx\u3067\u300D",
        useCase:
          "\u30EC\u30DD\u30FC\u30C8\u30FB\u4F01\u753B\u66F8\u30FB\u8B70\u4E8B\u9332\u306A\u3069\u306EWord\u6587\u66F8\u4F5C\u6210\u30FB\u7DE8\u96C6",
        features:
          "\u30B9\u30BF\u30A4\u30EB\u8A2D\u5B9A\u3001\u753B\u50CF\u306E\u633F\u5165\u3001\u69CB\u6210\u6848\u304B\u3089\u306E\u81EA\u52D5\u751F\u6210\u3001\u65E2\u5B58\u6587\u66F8\u306E\u6821\u6B63\u3068\u30EA\u30E9\u30A4\u30C8\u3002",
      },
      {
        name: "Excel (XLSX)",
        keywords:
          "\u300CExcel\u3092\u4F5C\u3063\u3066\u300D\u300C\u8868\u8A08\u7B97\u30D5\u30A1\u30A4\u30EB\u3092\u300D",
        useCase:
          "\u8907\u96D1\u306A\u8A08\u7B97\u5F0F\u3084\u96C6\u8A08\u30C6\u30FC\u30D6\u30EB\u3092\u542B\u3080Excel\u30D5\u30A1\u30A4\u30EB\u306E\u4F5C\u6210",
        features:
          "\u8907\u96D1\u306A\u8A08\u7B97\u5F0F\u306E\u57CB\u3081\u8FBC\u307F\u3001\u96C6\u8A08\u30C6\u30FC\u30D6\u30EB\u306E\u4F5C\u6210\u3001CSV\u30C7\u30FC\u30BF\u304B\u3089\u306E\u8868\u5909\u63DB\u3002",
      },
      {
        name: "PowerPoint (PPTX)",
        keywords:
          "\u300C\u30B9\u30E9\u30A4\u30C9\u3092\u4F5C\u3063\u3066\u300D\u300Cpptx\u3067\u30D7\u30EC\u30BC\u30F3\u6848\u300D",
        useCase:
          "\u30D7\u30EC\u30BC\u30F3\u30C6\u30FC\u30B7\u30E7\u30F3\u8CC7\u6599\u306E\u4F5C\u6210\u30FB\u7DE8\u96C6",
        features:
          "\u69CB\u6210\u6848\u306B\u57FA\u3065\u304F\u30B9\u30E9\u30A4\u30C9\u306E\u81EA\u52D5\u751F\u6210\u3001\u30EC\u30A4\u30A2\u30A6\u30C8\u8A2D\u8A08\u3001\u767A\u8868\u7528\u30CE\u30FC\u30C8\u306E\u4F5C\u6210\u3002",
      },
      {
        name: "PDF",
        keywords:
          "\u300CPDF\u3092\u7D50\u5408\u300D\u300CPDF\u304B\u3089\u30C6\u30AD\u30B9\u30C8\u62BD\u51FA\u300D",
        useCase:
          "PDF\u30D5\u30A1\u30A4\u30EB\u306E\u7D50\u5408\u30FB\u5206\u5272\u30FB\u30C6\u30AD\u30B9\u30C8\u62BD\u51FA\u30FB\u52A0\u5DE5",
        features:
          "\u8907\u6570\u30D5\u30A1\u30A4\u30EB\u306E\u7D50\u5408\u30FB\u5206\u5272\u3001\u30B9\u30AD\u30E3\u30F3\u6E08\u307FPDF\u306E\u30C6\u30AD\u30B9\u30C8\u5316\u3001\u7279\u5B9A\u30DA\u30FC\u30B8\u306E\u62BD\u51FA\u3002",
      },
      {
        name: "Word\u6587\u5B57\u6570\u30AB\u30A6\u30F3\u30C8",
        keywords:
          "\u300Cdocx\u3068\u3057\u3066\u306E\u6587\u5B57\u6570\u3092\u30AB\u30A6\u30F3\u30C8\u300D",
        useCase:
          "Markdown\u304B\u3089Word(A4/40\u5B57\u00D740\u884C)\u3067\u306E\u60F3\u5B9A\u6587\u5B57\u6570\u30FB\u679A\u6570\u3092\u63A8\u5B9A",
        features:
          "Markdown\u5F62\u5F0F\u304B\u3089Word\u306B\u66F8\u304D\u51FA\u3057\u305F\u969B\u306E\u60F3\u5B9A\u6587\u5B57\u6570\u30FB\u679A\u6570\u3092\u7CBE\u5BC6\u306B\u63A8\u5B9A\u3002",
      },
      {
        name: "Google Docs",
        keywords:
          "\u300CGoogle\u30C9\u30AD\u30E5\u30E1\u30F3\u30C8\u3092\u300D\u300C\u30C6\u30AD\u30B9\u30C8\u53D6\u5F97\u300D",
        useCase:
          "Google\u30C9\u30AD\u30E5\u30E1\u30F3\u30C8\u306E\u4F5C\u6210\u30FB\u691C\u7D22\u30FB\u30C6\u30AD\u30B9\u30C8\u53D6\u5F97\u30FB\u8FFD\u8A18\u30FB\u7F6E\u63DB",
        features:
          "\u30C9\u30AD\u30E5\u30E1\u30F3\u30C8\u306E\u4F5C\u6210\u30FB\u691C\u7D22\u30FB\u30C6\u30AD\u30B9\u30C8\u53D6\u5F97\u30FB\u8FFD\u8A18\u30FB\u633F\u5165\u30FB\u7F6E\u63DB\u3002OAuth\u8A8D\u8A3C\u3001MCP\u4E0D\u8981\u3002",
      },
      {
        name: "Google Drive",
        keywords:
          "\u300CDrive\u304B\u3089\u300D\u300C\u30D5\u30A1\u30A4\u30EB\u3092\u691C\u7D22\u300D",
        useCase:
          "Google Drive\u4E0A\u306E\u30D5\u30A1\u30A4\u30EB\u691C\u7D22\u30FB\u30A2\u30C3\u30D7\u30ED\u30FC\u30C9\u30FB\u30C0\u30A6\u30F3\u30ED\u30FC\u30C9",
        features:
          "Drive\u30D5\u30A1\u30A4\u30EB\u306E\u691C\u7D22\u30FB\u4E00\u89A7\u30FB\u30C0\u30A6\u30F3\u30ED\u30FC\u30C9\u3002URL/ID\u306E\u81EA\u52D5\u5224\u5225\u3002",
      },
      {
        name: "Google Sheets",
        keywords:
          "\u300C\u30B9\u30D7\u30EC\u30C3\u30C9\u30B7\u30FC\u30C8\u3092\u300D\u300C\u30B7\u30FC\u30C8\u306E\u5185\u5BB9\u300D",
        useCase:
          "Google\u30B9\u30D7\u30EC\u30C3\u30C9\u30B7\u30FC\u30C8\u306E\u30C7\u30FC\u30BF\u53D6\u5F97\u30FB\u95B2\u89A7",
        features:
          "\u30B9\u30D7\u30EC\u30C3\u30C9\u30B7\u30FC\u30C8\u306E\u8AAD\u307F\u53D6\u308A(text/csv/json)\u30FB\u7BC4\u56F2\u6307\u5B9A\u30FB\u30E1\u30BF\u30C7\u30FC\u30BF\u53D6\u5F97\u3002",
      },
      {
        name: "Google Slides",
        keywords:
          "\u300C\u30D7\u30EC\u30BC\u30F3\u306E\u5185\u5BB9\u3092\u300D\u300C\u30B9\u30E9\u30A4\u30C9\u3092\u691C\u7D22\u300D",
        useCase:
          "Google\u30B9\u30E9\u30A4\u30C9\u306E\u30C6\u30AD\u30B9\u30C8\u62BD\u51FA\u30FB\u691C\u7D22",
        features:
          "\u30D7\u30EC\u30BC\u30F3\u30C6\u30FC\u30B7\u30E7\u30F3\u306E\u30C6\u30AD\u30B9\u30C8\u62BD\u51FA\u30FB\u691C\u7D22\u30FB\u30E1\u30BF\u30C7\u30FC\u30BF\u53D6\u5F97\u3002\u8AAD\u307F\u53D6\u308A\u5C02\u7528\u3002",
      },
      {
        name: "\u30C9\u30AD\u30E5\u30E1\u30F3\u30C8\u81EA\u52D5\u4FDD\u5B58",
        keywords:
          "\u300C\u8A08\u753B\u3092\u30D0\u30C3\u30AF\u30A2\u30C3\u30D7\u300D\u300Cwalkthrough\u4FDD\u5B58\u300D",
        useCase:
          "\u91CD\u8981\u306A\u8A08\u753B\u3084\u6210\u679C\u5831\u544A\u3092\u81EA\u52D5\u3067\u6307\u5B9A\u30D5\u30A9\u30EB\u30C0\u306B\u30D0\u30C3\u30AF\u30A2\u30C3\u30D7",
        features:
          "\u91CD\u8981\u306A\u8A08\u753B(implementation_plan)\u3084\u6210\u679C\u5831\u544A(walkthrough)\u3092\u81EA\u52D5\u3067\u6307\u5B9A\u30D5\u30A9\u30EB\u30C0\u306B\u30D0\u30C3\u30AF\u30A2\u30C3\u30D7\u3002",
      },
      {
        name: "Outline Wiki",
        keywords:
          "\u300C\u8981\u7D04\u3057\u3066\u300D\u300C\u30A2\u30A6\u30C8\u30E9\u30A4\u30F3\u3092\u4F5C\u6210\u300D",
        useCase:
          "Outline Wiki\u306E\u30C9\u30AD\u30E5\u30E1\u30F3\u30C8\u691C\u7D22\u30FB\u8AAD\u307F\u66F8\u304D",
        features:
          "\u9577\u6587\u306E\u8AD6\u7406\u69CB\u9020\u3092\u62BD\u51FA\u3057\u3001\u898B\u51FA\u3057\u30EC\u30D9\u30EB\u306B\u5FDC\u3058\u305F\u968E\u5C64\u7684\u306A\u69CB\u6210\u6848\u3092\u751F\u6210\u3002",
      },
      {
        name: "Excel\u2192PDF\u5909\u63DB",
        keywords:
          "\u300CExcel\u3092PDF\u306B\u5909\u63DB\u300D\u300Cxlsx\u3092PDF\u5316\u300D",
        useCase:
          "Excel\u30D5\u30A1\u30A4\u30EB\u3092PDF\u306B\u5909\u63DB\u3057\u305F\u3044\u5834\u5408",
        features:
          "LibreOffice\u306B\u3088\u308B\u9AD8\u5FE0\u5B9F\u5EA6\u5909\u63DB\u3001Python\u7D14\u6B63\u306E\u8EFD\u91CF\u5909\u63DB\u306B\u5BFE\u5FDC\u3002\u66F8\u5F0F\u30FB\u7F6B\u7DDA\u30FB\u30B0\u30E9\u30D5\u3092\u4FDD\u6301\u3002",
      },
      {
        name: "CSV\u30C7\u30FC\u30BF\u5206\u6790",
        keywords:
          "\u300CCSV\u3092\u5206\u6790\u3057\u3066\u300D\u300C\u30C7\u30FC\u30BF\u3092\u8981\u7D04\u300D",
        useCase:
          "CSV\u30D5\u30A1\u30A4\u30EB\u306E\u7D71\u8A08\u30B5\u30DE\u30EA\u30FC\u3084\u76F8\u95A2\u5206\u6790\u3092\u5373\u5EA7\u306B\u5B9F\u884C",
        features:
          "CSV\u30D5\u30A1\u30A4\u30EB\u306E\u81EA\u52D5\u5206\u6790\u3002\u7D71\u8A08\u30B5\u30DE\u30EA\u30FC\u3001\u76F8\u95A2\u5206\u6790\u3001\u53EF\u8996\u5316\u3092\u8CEA\u554F\u306A\u3057\u3067\u5373\u6642\u5B9F\u884C\u3002",
      },
      {
        name: "\u30C7\u30FC\u30BF\u5206\u6790",
        keywords:
          "\u300CEDA\u3092\u5B9F\u884C\u300D\u300C\u5206\u6790\u30EC\u30DD\u30FC\u30C8\u4F5C\u6210\u300D",
        useCase:
          "\u63A2\u7D22\u7684\u30C7\u30FC\u30BF\u5206\u6790(EDA)\u3084\u54C1\u8CEA\u691C\u8A3C\u3001\u53EF\u8996\u5316\u3092\u5305\u62EC\u7684\u306B\u5B9F\u65BD",
        features:
          "\u63A2\u7D22\u7684\u30C7\u30FC\u30BF\u5206\u6790(EDA)\u3001\u54C1\u8CEA\u691C\u8A3C\u3001\u53EF\u8996\u5316\u3001\u30EC\u30DD\u30FC\u30C8\u751F\u6210\u3092\u5305\u62EC\u7684\u306B\u5B9F\u884C\u3002",
      },
      {
        name: "\u30D7\u30ED\u30B8\u30A7\u30AF\u30C8\u5831\u544A\u66F8",
        keywords:
          "\u300C\u7DCF\u62EC\u5831\u544A\u66F8\u3092\u4F5C\u6210\u300D\u300C\u30D7\u30ED\u30B8\u30A7\u30AF\u30C8\u30EC\u30DD\u30FC\u30C8\u300D",
        useCase:
          "\u793E\u5185\u5411\u3051\u30FB\u9867\u5BA2\u5411\u3051\u306E\u7DCF\u62EC\u5831\u544A\u66F8\u3092DOCX\u3068\u3057\u3066\u751F\u6210",
        features:
          "\u30A4\u30F3\u30BF\u30D3\u30E5\u30FC\u5F62\u5F0F\u3067\u5185\u5BB9\u53CE\u96C6\u3001DOCX\u3068\u3057\u3066\u751F\u6210\u3002\u30BB\u30AF\u30B7\u30E7\u30F3\u9078\u629E\u30FB\u30B9\u30BF\u30A4\u30EB\u9078\u629E\u5BFE\u5FDC\u3002",
      },
      {
        name: "Mermaid Diagram",
        keywords:
          "\u300C\u30A2\u30FC\u30AD\u30C6\u30AF\u30C1\u30E3\u56F3\u3092\u4F5C\u3063\u3066\u300D\u300CMermaid\u56F3\u300D\u300C\u69CB\u6210\u56F3\u300D",
        useCase:
          "\u30B7\u30B9\u30C6\u30E0\u69CB\u6210\u56F3\u30FBER\u56F3\u30FB\u30D5\u30ED\u30FC\u56F3\u306A\u3069\u306E\u6280\u8853\u56F3\u3092\u4F5C\u6210",
        features:
          "Mermaid\u8A18\u6CD5\u30678\u30BF\u30A4\u30D7\u306E\u56F3\u3092\u4F5C\u6210\u3002\u30D6\u30E9\u30F3\u30C9\u30AB\u30E9\u30FC\u30D1\u30EC\u30C3\u30C8\u3001PNG/SVG\u51FA\u529B\u5BFE\u5FDC\u3002",
      },
    ],
  },
  {
    title: "\u958B\u767A\u30FB\u6280\u8853\u95A2\u9023 (Development Skills)",
    description:
      "\u30D7\u30ED\u30B0\u30E9\u30DF\u30F3\u30B0\u3001\u30C7\u30D7\u30ED\u30A4\u3001\u30C6\u30B9\u30C8\u3001\u8A2D\u8A08\u306A\u3069\u3092\u652F\u63F4\u3059\u308B\u30B9\u30AD\u30EB\u3067\u3059\u3002",
    skills: [
      {
        name: "Vercel Deploy",
        keywords:
          "\u300C\u30C7\u30D7\u30ED\u30A4\u3057\u3066\u300D\u300CURL\u3092\u5171\u6709\u3057\u3066\u300D",
        useCase:
          "\u30ED\u30FC\u30AB\u30EB\u30D7\u30ED\u30B8\u30A7\u30AF\u30C8\u3092\u77AC\u6642\u306B\u516C\u958B\u30FB\u30D7\u30EC\u30D3\u30E5\u30FC",
        features:
          "\u30ED\u30FC\u30AB\u30EB\u30D7\u30ED\u30B8\u30A7\u30AF\u30C8\u3092\u77AC\u6642\u306B\u516C\u958B\u3002\u30D7\u30EC\u30D3\u30E5\u30FCURL+Claim\u30EA\u30F3\u30AF\u3092\u767A\u884C\u3002",
      },
      {
        name: "React/Expo\u958B\u767A",
        keywords:
          "\u300CReact Native\u3067\u4F5C\u3063\u3066\u300D\u300CExpo\u3067\u300D",
        useCase:
          "iOS/Android\u4E21\u5BFE\u5FDC\u306E\u30E2\u30D0\u30A4\u30EB\u30A2\u30D7\u30EA\u958B\u767A",
        features:
          "iOS/Android\u4E21\u5BFE\u5FDC\u306E\u30E2\u30D0\u30A4\u30EB\u30A2\u30D7\u30EA\u304A\u3088\u3073Web\u30A2\u30D7\u30EA\u306E\u30B3\u30FC\u30C9\u751F\u6210\u3001\u753B\u9762\u9077\u79FB\u3001\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u5B9F\u88C5\u3002",
      },
      {
        name: "React\u30D9\u30B9\u30C8\u30D7\u30E9\u30AF\u30C6\u30A3\u30B9",
        keywords:
          "\u300CReact\u306E\u8A2D\u8A08\u65B9\u91DD\u306F\uFF1F\u300D\u300C\u30D5\u30C3\u30AF\u306E\u4F7F\u3044\u65B9\u300D",
        useCase:
          "React/Next.js\u306E\u30D1\u30D5\u30A9\u30FC\u30DE\u30F3\u30B9\u6700\u9069\u5316\u3084\u30B3\u30FC\u30C7\u30A3\u30F3\u30B0\u6A19\u6E96\u306E\u78BA\u8A8D",
        features:
          "\u4F9D\u5B58\u914D\u5217\u306E\u6700\u9069\u5316\u3001\u72B6\u614B\u7BA1\u7406\u306E\u9078\u5B9A\u3001\u30D1\u30D5\u30A9\u30FC\u30DE\u30F3\u30B9\u3092\u8003\u616E\u3057\u305F\u30B3\u30FC\u30C7\u30A3\u30F3\u30B0\u6A19\u6E96\u3002",
      },
      {
        name: "\u8A2D\u8A08\u30D1\u30BF\u30FC\u30F3",
        keywords:
          "\u300C\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u69CB\u6210\u6848\u300D\u300CRender Props\u300D",
        useCase:
          "DRY\u3067\u30E1\u30F3\u30C6\u30CA\u30F3\u30B9\u6027\u306E\u9AD8\u3044React\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u8A2D\u8A08",
        features:
          "\u9AD8\u968E\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8(HOC)\u3084Composition\u3092\u7528\u3044\u305F\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u30C4\u30EA\u30FC\u306E\u8A2D\u8A08\u3002",
      },
      {
        name: "Find Skills",
        keywords:
          "\u300C\u30B9\u30AD\u30EB\u3092\u691C\u7D22\u300D\u300C\u3069\u3093\u306A\u30B9\u30AD\u30EB\u304C\u3042\u308B\uFF1F\u300D",
        useCase:
          "\u30E6\u30FC\u30B6\u30FC\u306E\u8981\u671B\u304B\u3089\u6700\u9069\u306A\u30B9\u30AD\u30EB\u3092\u7279\u5B9A\u30FB\u63D0\u6848",
        features:
          "\u30E6\u30FC\u30B6\u30FC\u306E\u6F20\u7136\u3068\u3057\u305F\u8981\u671B\u304B\u3089\u6700\u9069\u306A\u30B9\u30AD\u30EB\u3092\u7279\u5B9A\u3057\u3001\u4F7F\u3044\u65B9\u3084\u30E1\u30EA\u30C3\u30C8\u3092\u30AC\u30A4\u30C9\u3002",
      },
      {
        name: "Skill Creator",
        keywords:
          "\u300C\u65B0\u3057\u3044\u30B9\u30AD\u30EB\u3092\u4F5C\u6210\u3057\u3066\u300D\u300C\u30AB\u30B9\u30BF\u30E0\u30B9\u30AD\u30EB\u300D",
        useCase:
          "\u72EC\u81EA\u306E\u5B9A\u578B\u696D\u52D9\u3092\u81EA\u52D5\u5316\u3059\u308B\u30B9\u30AD\u30EB\u306E\u4F5C\u6210",
        features:
          "\u72EC\u81EA\u306E\u5B9A\u578B\u696D\u52D9\u3092\u81EA\u52D5\u5316\u3059\u308B\u30B9\u30AD\u30EB\uFF08\u6307\u793A\u66F8\u3001\u30B9\u30AF\u30EA\u30D7\u30C8\u3001\u30C6\u30F3\u30D7\u30EC\u30FC\u30C8\uFF09\u3092\u8A2D\u8A08\u30FB\u30D1\u30C3\u30B1\u30FC\u30B8\u5316\u3002",
      },
      {
        name: "MCP Builder",
        keywords:
          "\u300CMCP\u30B5\u30FC\u30D0\u30FC\u3092\u4F5C\u6210\u300D\u300CMCP\u30C4\u30FC\u30EB\u3092\u300D",
        useCase:
          "\u5916\u90E8API\u3084\u72EC\u81EADB\u3092\u30A8\u30FC\u30B8\u30A7\u30F3\u30C8\u306B\u63A5\u7D9A\u3059\u308BMCP\u30B5\u30FC\u30D0\u30FC\u5B9F\u88C5",
        features:
          "Model Context Protocol\u306E\u5B9F\u88C5\u652F\u63F4\u3002TypeScript/Python\u5BFE\u5FDC\u3002",
      },
      {
        name: "Web\u30A2\u30D7\u30EA\u30C6\u30B9\u30C8",
        keywords:
          "\u300CUI\u30C6\u30B9\u30C8\u3092\u5B9F\u884C\u300D\u300CE2E\u30C6\u30B9\u30C8\u3092\u3057\u3066\u300D",
        useCase:
          "\u30D6\u30E9\u30A6\u30B6\u81EA\u52D5\u64CD\u4F5C\u306B\u3088\u308BUI\u30C6\u30B9\u30C8\u3084E2E\u30C6\u30B9\u30C8",
        features:
          "\u30D6\u30E9\u30A6\u30B6\u3092\u81EA\u52D5\u64CD\u4F5C\u3057\u3001\u30DC\u30BF\u30F3\u30AF\u30EA\u30C3\u30AF\u3084\u30D5\u30A9\u30FC\u30E0\u5165\u529B\u306A\u3069\u306E\u30E6\u30FC\u30B6\u30FC\u30D5\u30ED\u30FC\u3092\u691C\u8A3C\u3002",
      },
      {
        name: "Deep Research",
        keywords:
          "\u300C\u8A73\u7D30\u306B\u8ABF\u67FB\u3057\u3066\u300D\u300C\u591A\u89D2\u7684\u306B\u8ABF\u3079\u3066\u300D",
        useCase:
          "\u8907\u6570\u306E\u60C5\u5831\u6E90\u3092\u6A2A\u65AD\u3057\u305F\u6DF1\u6398\u308A\u8ABF\u67FB\u30FB\u7AF6\u5408\u5206\u6790",
        features:
          "Gemini API\u3067\u81EA\u5F8B\u7684\u306BWeb\u8ABF\u67FB\u3002\u8907\u6570\u60C5\u5831\u6E90\u6A2A\u65AD\u3067\u7AF6\u5408\u5206\u6790\u3084\u6280\u8853\u30C8\u30EC\u30F3\u30C9\u306E\u6DF1\u6398\u308A\u8ABF\u67FB\u3002",
      },
      {
        name: "\u30C7\u30FC\u30BF\u30D9\u30FC\u30B9 (Postgres)",
        keywords:
          "\u300CSQL\u3092\u5B9F\u884C\u300D\u300CDB\u3092\u64CD\u4F5C\u300D",
        useCase:
          "PostgreSQL\u30C7\u30FC\u30BF\u30D9\u30FC\u30B9\u306E\u30AF\u30A8\u30EA\u5B9F\u884C\u3084\u30B9\u30AD\u30FC\u30DE\u63A2\u7D22",
        features:
          "\u30B9\u30AD\u30FC\u30DE\u8A2D\u8A08\u304B\u3089\u8907\u96D1\u306ASELECT\u53E5\u3001\u30B8\u30E7\u30A4\u30F3\u3092\u542B\u3080\u30AF\u30A8\u30EA\u306E\u4F5C\u6210\u3068\u5B9F\u884C\u3001\u30C7\u30D0\u30C3\u30B0\u3002",
      },
      {
        name: "GitHub Pusher",
        keywords:
          "\u300CGitHub\u3078\u30D7\u30C3\u30B7\u30E5\u3057\u3066\u300D\u300C\u30B3\u30DF\u30C3\u30C8\u3057\u3066GitHub\u3078\u300D",
        useCase:
          "\u5909\u66F4\u306E\u81EA\u52D5\u8981\u7D04\u3068GitHub\u3078\u306E\u4E00\u62EC\u53CD\u6620",
        features:
          "\u5909\u66F4\u7B87\u6240\u306E\u81EA\u52D5\u8981\u7D04\u3001\u6700\u9069\u306A\u30B3\u30DF\u30C3\u30C8\u30E1\u30C3\u30BB\u30FC\u30B8\u306E\u751F\u6210\u3001GitHub\u3078\u306E\u4E00\u62EC\u53CD\u6620\u3002",
      },
      {
        name: "Stripe Integration",
        keywords:
          "\u300CStripe\u6C7A\u6E08\u3092\u5B9F\u88C5\u300D\u300C\u30B5\u30D6\u30B9\u30AF\u30EA\u30D7\u30B7\u30E7\u30F3\u6A5F\u80FD\u300D",
        useCase:
          "Stripe\u3092\u4F7F\u3063\u305F\u6C7A\u6E08\u30FB\u30B5\u30D6\u30B9\u30AF\u30EA\u30D7\u30B7\u30E7\u30F3\u6A5F\u80FD\u306E\u7D44\u307F\u8FBC\u307F",
        features:
          "PaymentElement\u3001Webhook\u51E6\u7406\u3001\u30B5\u30D6\u30B9\u30AF\u30EA\u30D7\u30B7\u30E7\u30F3\u7BA1\u7406\u306A\u3069\u3001Stripe\u6C7A\u6E08\u306E\u7D71\u5408\u5B9F\u88C5\u3002",
      },
      {
        name: "MoAI Domain Frontend",
        keywords:
          "\u300CNext.js\u30A2\u30D7\u30EA\u3092\u958B\u767A\u300D\u300C\u30D5\u30ED\u30F3\u30C8\u30A8\u30F3\u30C9\u958B\u767A\u300D",
        useCase:
          "React/Next.js/Vue.js\u3092\u7528\u3044\u305F\u30E2\u30C0\u30F3\u30D5\u30ED\u30F3\u30C8\u30A8\u30F3\u30C9\u958B\u767A",
        features:
          "React 19/Next.js 16/Vue 3.5\u5BFE\u5FDC\u3002Server Components\u3001Zustand\u72B6\u614B\u7BA1\u7406\u3002",
      },
      {
        name: "Ship-Learn-Next",
        keywords:
          "\u300C\u5B66\u7FD2\u5185\u5BB9\u3092\u8A08\u753B\u306B\u300D\u300C\u30A2\u30A6\u30C8\u30D7\u30C3\u30C8\u8A08\u753B\u3092\u300D",
        useCase:
          "\u5B66\u7FD2\u6210\u679C\u3092\u6B21\u306E\u30A2\u30A6\u30C8\u30D7\u30C3\u30C8\u306B\u3064\u306A\u3052\u308B\u8A08\u753B\u7B56\u5B9A",
        features:
          "\u5B66\u7FD2\u30B3\u30F3\u30C6\u30F3\u30C4\u3092\u5B9F\u8DF5\u7684\u306AShip\u8A08\u753B\u306B\u5909\u63DB\u3002",
      },
      {
        name: "Brainstorming",
        keywords:
          "\u300C\u8A2D\u8A08\u306E\u30D6\u30EC\u30B9\u30C8\u300D\u300C\u69CB\u6210\u6848\u3092\u51FA\u3057\u3066\u300D",
        useCase:
          "\u5B9F\u88C5\u524D\u306E\u8A2D\u8A08\u691C\u8A0E\u3084\u30A2\u30A4\u30C7\u30A2\u51FA\u3057",
        features:
          "\u5B9F\u88C5\u524D\u306E\u8A2D\u8A08\u691C\u8A0E\u3084\u30A2\u30A4\u30C7\u30A2\u51FA\u3057\u3092\u69CB\u9020\u5316\u3057\u3066\u884C\u3046\u30D6\u30EC\u30A4\u30F3\u30B9\u30C8\u30FC\u30DF\u30F3\u30B0\u652F\u63F4\u3002",
      },
      {
        name: "Jules",
        keywords:
          "\u300CJules\u306B\u805E\u3044\u3066\u300D\u300C\u30A8\u30FC\u30B8\u30A7\u30F3\u30C8\u9023\u643A\u3092\u300D",
        useCase:
          "GitHub\u4E0A\u306E\u30B3\u30FC\u30C7\u30A3\u30F3\u30B0\u4F5C\u696D\u3092Jules AI\u306B\u59D4\u4EFB",
        features:
          "\u5916\u90E8\u30A8\u30FC\u30B8\u30A7\u30F3\u30C8\uFF08Jules\uFF09\u3068\u306E\u9023\u643A\u306B\u3088\u308B\u30BF\u30B9\u30AF\u59D4\u4EFB\u30FB\u5354\u8ABF\u4F5C\u696D\u3002",
      },
      {
        name: "D3.js\u53EF\u8996\u5316",
        keywords:
          "\u300CD3\u3067\u30B0\u30E9\u30D5\u4F5C\u6210\u300D\u300C\u30A4\u30F3\u30BF\u30E9\u30AF\u30C6\u30A3\u30D6\u30C1\u30E3\u30FC\u30C8\u300D",
        useCase:
          "\u30AB\u30B9\u30BF\u30E0\u30C1\u30E3\u30FC\u30C8\u3084\u30A4\u30F3\u30BF\u30E9\u30AF\u30C6\u30A3\u30D6\u53EF\u8996\u5316\u306E\u4F5C\u6210",
        features:
          "D3.js\u306B\u3088\u308B\u30AB\u30B9\u30BF\u30E0\u30C1\u30E3\u30FC\u30C8\u3001\u30CD\u30C3\u30C8\u30EF\u30FC\u30AF\u56F3\u3001\u30D2\u30FC\u30C8\u30DE\u30C3\u30D7\u7B49\u306E\u30A4\u30F3\u30BF\u30E9\u30AF\u30C6\u30A3\u30D6\u53EF\u8996\u5316\u3002",
      },
      {
        name: "Kaizen",
        keywords:
          "\u300C\u30AB\u30A4\u30BC\u30F3\u306E\u8996\u70B9\u3067\u300D\u300C\u7D99\u7D9A\u7684\u6539\u5584\u300D",
        useCase:
          "\u6539\u5584\u30FB\u30DD\u30AB\u30E8\u30B1\u30FB\u6A19\u6E96\u5316\u30FBJIT\u306E\u539F\u5247\u306B\u57FA\u3065\u304F\u54C1\u8CEA\u5411\u4E0A",
        features:
          "4\u3064\u306E\u67F1\uFF08\u6539\u5584\u30FB\u30DD\u30AB\u30E8\u30B1\u30FB\u6A19\u6E96\u5316\u30FBJIT\uFF09\u306B\u57FA\u3065\u304F\u6F38\u9032\u7684\u306A\u54C1\u8CEA\u5411\u4E0A\u624B\u6CD5\u3002",
      },
      {
        name: "Tapestry",
        keywords:
          "\u300Ctapestry URL\u300D\u300C\u52D5\u753B\u304B\u3089\u8A08\u753B\u3092\u300D",
        useCase:
          "URL\uFF08YouTube/\u8A18\u4E8B/PDF\uFF09\u304B\u3089\u30B3\u30F3\u30C6\u30F3\u30C4\u62BD\u51FA\u2192\u30A2\u30AF\u30B7\u30E7\u30F3\u30D7\u30E9\u30F3\u751F\u6210",
        features:
          "URL\u304B\u3089\u30B3\u30F3\u30C6\u30F3\u30C4\u3092\u62BD\u51FA\u3057\u3001\u30A2\u30AF\u30B7\u30E7\u30F3\u30D7\u30E9\u30F3\u3092\u81EA\u52D5\u751F\u6210\u3002",
      },
      {
        name: "\u8CA1\u52D9\u30E2\u30C7\u30EA\u30F3\u30B0",
        keywords:
          "\u300CDCF\u5206\u6790\u300D\u300CWACC\u8A08\u7B97\u300D\u300C\u30E2\u30F3\u30C6\u30AB\u30EB\u30ED\u300D",
        useCase:
          "DCF\u6CD5\u3084\u611F\u5FDC\u5EA6\u5206\u6790\u3001\u30E2\u30F3\u30C6\u30AB\u30EB\u30ED\u30B7\u30DF\u30E5\u30EC\u30FC\u30B7\u30E7\u30F3\u306B\u3088\u308B\u4F01\u696D\u4FA1\u5024\u8A55\u4FA1",
        features:
          "DCF\u6CD5\u3001\u611F\u5FDC\u5EA6\u5206\u6790\u3001\u30E2\u30F3\u30C6\u30AB\u30EB\u30ED\u30B7\u30DF\u30E5\u30EC\u30FC\u30B7\u30E7\u30F3\u7B49\u306B\u3088\u308B\u4F01\u696D\u4FA1\u5024\u8A55\u4FA1\u30FB\u8CA1\u52D9\u5206\u6790\u3002",
      },
      {
        name: "UI\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u30AC\u30A4\u30C9",
        keywords:
          "\u300C\u3069\u306E\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u3092\u4F7F\u3046\u3079\u304D?\u300D\u300C\u30C0\u30C3\u30B7\u30E5\u30DC\u30FC\u30C9\u306E\u69CB\u6210\u306F?\u300D",
        useCase:
          "60\u7A2E\u306E\u6A19\u6E96UI\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u304B\u3089\u6700\u9069\u306A\u69CB\u6210\u3092\u63D0\u6848",
        features:
          "60\u7A2E\u306E\u6A19\u6E96UI\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u306E\u77E5\u8B58\u30D9\u30FC\u30B9\u3002\u30DA\u30FC\u30B8\u7A2E\u5225\u30C6\u30F3\u30D7\u30EC\u30FC\u30C8\u3068\u9078\u5B9A\u30EF\u30FC\u30AF\u30D5\u30ED\u30FC\u3002",
      },
      {
        name: "CLAUDE.md Improver",
        keywords:
          "\u300CCLAUDE.md\u3092\u76E3\u67FB\u300D\u300CCLAUDE.md\u3092\u6539\u5584\u3057\u3066\u300D\u300C\u30D7\u30ED\u30B8\u30A7\u30AF\u30C8\u30E1\u30E2\u30EA\u6700\u9069\u5316\u300D",
        useCase:
          "\u30EA\u30DD\u30B8\u30C8\u30EA\u5185\u306ECLAUDE.md\u30D5\u30A1\u30A4\u30EB\u306E\u54C1\u8CEA\u76E3\u67FB\u30FB\u6539\u5584\u63D0\u6848",
        features:
          "\u5168CLAUDE.md\u3092\u767A\u898B\u30FB6\u57FA\u6E96100\u70B9\u6E80\u70B9\u3067\u30B9\u30B3\u30A2\u30EA\u30F3\u30B0\u3002\u54C1\u8CEA\u30EC\u30DD\u30FC\u30C8\u51FA\u529B\u5F8C\u3001\u30BF\u30FC\u30B2\u30C3\u30C8\u3092\u7D5E\u3063\u305F\u6539\u5584diff\u3092\u63D0\u6848\u30FB\u9069\u7528\u3002",
      },
      {
        name: "Claude API",
        keywords:
          "\u300CClaude API\u3067\u5B9F\u88C5\u300D\u300CAnthropic SDK\u3092\u4F7F\u3063\u3066\u300D\u300CAgent SDK\u3067\u300D",
        useCase:
          "Claude API\u30FBAnthropic SDK\u30FBAgent SDK\u3092\u4F7F\u3063\u305F\u30A2\u30D7\u30EA\u30B1\u30FC\u30B7\u30E7\u30F3\u958B\u767A",
        features:
          "Python/TypeScript/Java/Go/Ruby/C#/PHP/cURL\u306E8\u8A00\u8A9E\u5BFE\u5FDC\u3002\u30B9\u30C8\u30EA\u30FC\u30DF\u30F3\u30B0\u3001Tool Use\u3001\u30D0\u30C3\u30C1\u51E6\u7406\u3001\u30D5\u30A1\u30A4\u30EBAPI\u3002",
      },
      {
        name: "ML Data Guardian",
        keywords:
          "\u300C\u7279\u5FB4\u91CF\u3092\u691C\u8A3C\u300D\u300C\u30C7\u30FC\u30BF\u6574\u5408\u6027\u30C1\u30A7\u30C3\u30AF\u300D\u300C\u63D0\u51FA\u524D\u30C1\u30A7\u30C3\u30AF\u300D",
        useCase:
          "ML\u30D1\u30A4\u30D7\u30E9\u30A4\u30F3\u306Etrain/test\u30C7\u30FC\u30BF\u6574\u5408\u6027\u30C1\u30A7\u30C3\u30AF\u3092\u80FD\u52D5\u7684\u306B\u63D0\u6848",
        features:
          "5\u3064\u306E\u30DE\u30A4\u30EB\u30B9\u30C8\u30FC\u30F3\u3067NaN\u7387\u6BD4\u8F03\u3001\u5206\u5E03\u30C9\u30EA\u30D5\u30C8\u691C\u51FA\u3001\u5E38\u8B58\u30C1\u30A7\u30C3\u30AF\u7528Python\u30B9\u30CB\u30DA\u30C3\u30C8\u4ED8\u304D\u3002",
      },
    ],
  },
  {
    title:
      "\u30AF\u30EA\u30A8\u30A4\u30C6\u30A3\u30D6\u30FB\u30C7\u30B6\u30A4\u30F3 (Creative Skills)",
    description:
      "UI/UX\u8A2D\u8A08\u3001\u753B\u50CF\u751F\u6210\u3001\u30D3\u30B8\u30E5\u30A2\u30EB\u30C7\u30B6\u30A4\u30F3\u3092\u652F\u63F4\u3057\u307E\u3059\u3002",
    skills: [
      {
        name: "UI/UX Pro Max",
        keywords:
          "\u300C\u30AB\u30E9\u30FC\u30D1\u30EC\u30C3\u30C8\u9078\u5B9A\u300D\u300C\u753B\u9762\u8A2D\u8A08\u3057\u3066\u300D",
        useCase:
          "\u30A2\u30AF\u30BB\u30B7\u30D3\u30EA\u30C6\u30A3\u5BFE\u5FDC\u3084\u30C7\u30B6\u30A4\u30F3\u30B7\u30B9\u30C6\u30E0\u69CB\u7BC9",
        features:
          "50+\u30B9\u30BF\u30A4\u30EB\u300197\u30AB\u30E9\u30FC\u30D1\u30EC\u30C3\u30C8\u300157\u30D5\u30A9\u30F3\u30C8\u30DA\u30A2\u30EA\u30F3\u30B0\u3002\u5305\u62EC\u7684\u30C7\u30B6\u30A4\u30F3\u30B7\u30B9\u30C6\u30E0\u3002",
      },
      {
        name: "Web\u30C7\u30B6\u30A4\u30F3\u6307\u91DD",
        keywords:
          "\u300C\u30C7\u30B6\u30A4\u30F3\u306E\u57FA\u790E\u300D\u300CUX\u5411\u4E0A\u306E\u30B3\u30C4\u300D",
        useCase:
          "UI\u30B3\u30FC\u30C9\u30EC\u30D3\u30E5\u30FC\u3084\u30C7\u30B6\u30A4\u30F3\u30B3\u30F3\u30D7\u30E9\u30A4\u30A2\u30F3\u30B9\u76E3\u67FB",
        features:
          "\u60C5\u5831\u8A2D\u8A08(IA)\u306E\u6700\u9069\u5316\u3001\u8996\u7DDA\u8A98\u5C0E\u3001\u30DE\u30A4\u30AF\u30ED\u30A4\u30F3\u30BF\u30E9\u30AF\u30B7\u30E7\u30F3\u306A\u3069\u306E\u30AC\u30A4\u30C9\u3002",
      },
      {
        name: "Imagen",
        keywords:
          "\u300C\u753B\u50CF\u3092\u751F\u6210\u3057\u3066\u300D\u300CAI\u3067\u753B\u50CF\u4F5C\u6210\u300D",
        useCase:
          "\u5199\u771F\u98A8\u753B\u50CF\u304B\u3089\u30A4\u30E9\u30B9\u30C8\u3001\u30ED\u30B4\u3001UI\u30A2\u30A4\u30B3\u30F3\u307E\u3067\u306EAI\u751F\u6210",
        features:
          "Gemini API\u306B\u3088\u308BAI\u753B\u50CF\u751F\u6210\u3002\u30EA\u30A2\u30EB\u306A\u5199\u771F\u304B\u3089\u30A4\u30E9\u30B9\u30C8\u307E\u3067\u591A\u69D8\u306A\u30D3\u30B8\u30E5\u30A2\u30EB\u7D20\u6750\u3002",
      },
      {
        name: "Web Artifacts",
        keywords:
          "\u300C\u30A4\u30F3\u30BF\u30E9\u30AF\u30C6\u30A3\u30D6\u306A\u30C7\u30E2\u300D\u300C\u30A6\u30A3\u30B8\u30A7\u30C3\u30C8\u300D",
        useCase:
          "\u30D6\u30E9\u30A6\u30B6\u4E0A\u3067\u52D5\u4F5C\u3059\u308B\u30A4\u30F3\u30BF\u30E9\u30AF\u30C6\u30A3\u30D6\u306A\u30C7\u30E2\u3084\u30D1\u30FC\u30C4\u4F5C\u6210",
        features:
          "React 18 + TypeScript + Vite + shadcn/ui\u3067\u30D0\u30F3\u30C9\u30EB\u3002\u52D5\u4F5C\u3059\u308B\u30B0\u30E9\u30D5\u3084\u30B7\u30DF\u30E5\u30EC\u30FC\u30BF\u30FC\u3092\u5373\u5EA7\u4F5C\u6210\u3002",
      },
      {
        name: "\u30C6\u30FC\u30DE\u30D5\u30A1\u30AF\u30C8\u30EA\u30FC",
        keywords:
          "\u300C\u30C7\u30B6\u30A4\u30F3\u30B7\u30B9\u30C6\u30E0\u3092\u4F5C\u6210\u300D\u300C\u30C6\u30FC\u30DE\u4F5C\u6210\u300D",
        useCase:
          "\u30C0\u30FC\u30AF\u30E2\u30FC\u30C9\u5BFE\u5FDC\u3084\u4E00\u8CAB\u6027\u306E\u3042\u308B\u30C6\u30FC\u30DE\u69CB\u7BC9",
        features:
          "10\u7A2E\u306E\u30D7\u30ED\u30D5\u30A7\u30C3\u30B7\u30E7\u30CA\u30EB\u30C6\u30FC\u30DE\u3002CSS\u5909\u6570\u3092\u7528\u3044\u305F\u518D\u5229\u7528\u53EF\u80FD\u306A\u30C6\u30FC\u30DE\u69CB\u7BC9\u3002",
      },
      {
        name: "\u30AD\u30E3\u30F3\u30D0\u30B9\u30C7\u30B6\u30A4\u30F3",
        keywords:
          "\u300C\u30B0\u30E9\u30D5\u30A3\u30C3\u30AF\u4F5C\u6210\u300D\u300CCanvas API\u3067\u300D",
        useCase:
          "\u30C7\u30B6\u30A4\u30F3\u54F2\u5B66\u306B\u57FA\u3065\u304F\u30A2\u30FC\u30C8\u4F5C\u54C1(PNG/PDF)\u306E\u751F\u6210",
        features:
          "\u52D5\u7684\u306A\u30B0\u30E9\u30D5\u63CF\u753B\u3001\u753B\u50CF\u52A0\u5DE5\uFF08\u30EA\u30B5\u30A4\u30BA\u3001\u30D5\u30A3\u30EB\u30BF\uFF09\u3001\u5E7E\u4F55\u5B66\u6A21\u69D8\u306E\u751F\u6210\u3002",
      },
      {
        name: "\u6570\u5B66\u7684\u30A2\u30FC\u30C8",
        keywords:
          "\u300C\u30A2\u30EB\u30B4\u30EA\u30BA\u30DF\u30C3\u30AF\u30A2\u30FC\u30C8\u300D\u300C\u30B8\u30A7\u30CD\u30A2\u30FC\u30C8\u300D",
        useCase:
          "\u6570\u5B66\u3084\u30A2\u30EB\u30B4\u30EA\u30BA\u30E0\u3092\u7528\u3044\u305F\u82B8\u8853\u4F5C\u54C1\u306E\u4F5C\u6210",
        features:
          "p5.js\u306B\u3088\u308B\u30B8\u30A7\u30CD\u30E9\u30C6\u30A3\u30D6\u30A2\u30FC\u30C8\u3002\u30B7\u30FC\u30C9\u4ED8\u304D\u30E9\u30F3\u30C0\u30E0\u3067\u518D\u73FE\u6027\u3042\u308A\u3002",
      },
      {
        name: "NLM Style Generator",
        keywords:
          "\u300CNLM\u30B9\u30BF\u30A4\u30EBJSON\u300D\u300CNotebookLM\u30B9\u30BF\u30A4\u30EB\u300D\u300C\u30B9\u30E9\u30A4\u30C9\u306E\u30B9\u30BF\u30A4\u30EB\u3092\u4F5C\u3063\u3066\u300D",
        useCase:
          "PDF\u30FB\u753B\u50CF\u304B\u3089NotebookLM\u30B9\u30BF\u30A4\u30EBJSON\u3092\u30EA\u30D0\u30FC\u30B9\u30A8\u30F3\u30B8\u30CB\u30A2\u30EA\u30F3\u30B0\u751F\u6210",
        features:
          "5000\u6587\u5B57\u5236\u9650\u5BFE\u5FDC\u3002PDF\u30EA\u30D0\u30FC\u30B9\u30AC\u30A4\u30C9\u30C1\u30A7\u30C3\u30AF\u30EA\u30B9\u30C8\u3001\u691C\u8A3C\u30B9\u30AF\u30EA\u30D7\u30C8\u4ED8\u304D\u3002",
      },
      {
        name: "Frontend Design",
        keywords:
          "\u300C\u30C7\u30B6\u30A4\u30F3UI\u300D\u300C\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u4F5C\u6210\u300D",
        useCase:
          "\u500B\u6027\u7684\u30FB\u9AD8\u54C1\u8CEA\u306A\u30D5\u30ED\u30F3\u30C8\u30A8\u30F3\u30C9UI\u5B9F\u88C5",
        features:
          "\u7523\u696D\u30B0\u30EC\u30FC\u30C9\u306E\u30D5\u30ED\u30F3\u30C8\u30A8\u30F3\u30C9UI\u3002\u72EC\u81EA\u306E\u7F8E\u5B66\u306B\u57FA\u3065\u304F\u30C7\u30B6\u30A4\u30F3\u3002",
      },
      {
        name: "\u30D6\u30E9\u30F3\u30C9\u30AC\u30A4\u30C9\u30E9\u30A4\u30F3",
        keywords:
          "\u300C\u30B9\u30BF\u30A4\u30EB\u30AC\u30A4\u30C9\u4F5C\u6210\u300D\u300C\u30D6\u30E9\u30F3\u30C7\u30A3\u30F3\u30B0\u300D",
        useCase:
          "Anthropic\u516C\u5F0F\u30D6\u30E9\u30F3\u30C9\u30AB\u30E9\u30FC\u30FB\u30BF\u30A4\u30DD\u30B0\u30E9\u30D5\u30A3\u306E\u9069\u7528",
        features:
          "\u30ED\u30B4\u306E\u4F7F\u7528\u898F\u5B9A\u3001\u30C8\u30FC\u30F3\uFF06\u30DE\u30CA\u30FC\u306E\u8A2D\u5B9A\u3001\u30D6\u30E9\u30F3\u30C9\u306E\u4E16\u754C\u89B3\u3092\u7D71\u4E00\u3059\u308B\u6587\u66F8\u4F5C\u6210\u3002",
      },
    ],
  },
  {
    title:
      "\u30B3\u30DF\u30E5\u30CB\u30B1\u30FC\u30B7\u30E7\u30F3\u30FB\u65E5\u5E38 (Communication Skills)",
    description:
      "\u5916\u90E8\u30C4\u30FC\u30EB\u3068\u306E\u9023\u643A\u3084\u3001\u7279\u5B9A\u306E\u6587\u4F53\u3067\u306E\u57F7\u7B46\u3092\u884C\u3044\u307E\u3059\u3002",
    skills: [
      {
        name: "\u30D6\u30ED\u30B0\u57F7\u7B46 (\u6069\u7530\u98A8)",
        keywords:
          "\u300C\u6069\u7530\u3055\u3093\u98A8\u306B\u66F8\u3044\u3066\u300D\u300C\u30D6\u30ED\u30B0\u8A18\u4E8B\u3092\u300D",
        useCase:
          "\u89AA\u3057\u307F\u3084\u3059\u304F\u5C02\u9580\u6027\u306E\u9AD8\u3044\u6587\u4F53\u3067\u306E\u30D6\u30ED\u30B0\u8A18\u4E8B\u4F5C\u6210",
        features:
          "\u89AA\u3057\u307F\u3084\u3059\u304F\u5C02\u9580\u6027\u306E\u9AD8\u3044\u72EC\u7279\u306E\u8A9E\u308A\u53E3\u3092\u518D\u73FE\u3002\u69CB\u6210\u6848\u304B\u3089\u672C\u6587\u307E\u3067\u5BFE\u5FDC\u3002",
      },
      {
        name: "Gmail",
        keywords:
          "\u300C\u30E1\u30FC\u30EB\u3092\u9001\u4FE1\u300D\u300C\u4E0B\u66F8\u304D\u3092\u4F5C\u6210\u300D",
        useCase:
          "\u30E1\u30FC\u30EB\u691C\u7D22\u30FB\u95B2\u89A7\u30FB\u9001\u4FE1\u30FB\u4E0B\u66F8\u304D\u30FB\u30E9\u30D9\u30EB\u7BA1\u7406",
        features:
          "\u30E1\u30FC\u30EB\u691C\u7D22\u30FB\u95B2\u89A7\u30FB\u9001\u4FE1\u30FB\u4E0B\u66F8\u304D\u30FB\u30E9\u30D9\u30EB\u7BA1\u7406\u3002HTML\u30E1\u30FC\u30EB\u5BFE\u5FDC\u3002OAuth\u8A8D\u8A3C\u3002",
      },
      {
        name: "Google\u30AB\u30EC\u30F3\u30C0\u30FC",
        keywords:
          "\u300C\u4E88\u5B9A\u3092\u5165\u308C\u3066\u300D\u300C\u30AB\u30EC\u30F3\u30C0\u30FC\u3067\u78BA\u8A8D\u300D",
        useCase:
          "\u30A4\u30D9\u30F3\u30C8\u306ECRUD\u30FB\u7A7A\u304D\u6642\u9593\u691C\u7D22\u30FB\u62DB\u5F85\u5FDC\u7B54",
        features:
          "\u30A4\u30D9\u30F3\u30C8\u306ECRUD\u30FB\u7A7A\u304D\u6642\u9593\u691C\u7D22\u30FB\u62DB\u5F85\u5FDC\u7B54\u3002\u8907\u6570\u30AB\u30EC\u30F3\u30C0\u30FC\u5BFE\u5FDC\u3002OAuth\u8A8D\u8A3C\u3002",
      },
      {
        name: "Google Chat",
        keywords:
          "\u300C\u30C1\u30E3\u30C3\u30C8\u3067\u9001\u4FE1\u300D\u300C\u30B9\u30DA\u30FC\u30B9\u3092\u691C\u7D22\u300D",
        useCase:
          "Google Chat\u3067\u306E\u30E1\u30C3\u30BB\u30FC\u30B8\u9001\u53D7\u4FE1\u30FB\u30B9\u30DA\u30FC\u30B9\u7BA1\u7406",
        features:
          "\u30B9\u30DA\u30FC\u30B9\u4E00\u89A7\u30FB\u30E1\u30C3\u30BB\u30FC\u30B8\u9001\u53D7\u4FE1\u30FBDM\u30FB\u30B9\u30EC\u30C3\u30C9\u30FB\u30B9\u30DA\u30FC\u30B9\u4F5C\u6210\u3002OAuth\u8A8D\u8A3C\u3002",
      },
      {
        name: "Slack GIF Creator",
        keywords: "\u300CGIF\u3092\u751F\u6210\u300D\u300CSlack\u7528GIF\u300D",
        useCase:
          "Slack\u7528\u306E\u30EA\u30A2\u30AF\u30B7\u30E7\u30F3GIF\u3084\u30AB\u30B9\u30BF\u30E0\u7D75\u6587\u5B57\u306E\u751F\u6210",
        features:
          "\u30EA\u30A2\u30AF\u30B7\u30E7\u30F3\u7528GIF\u3084\u30AB\u30B9\u30BF\u30E0\u7D75\u6587\u5B57\u306E\u751F\u6210\u3002128x128\u3001480x480\u5BFE\u5FDC\u3002",
      },
      {
        name: "Doc Co-authoring",
        keywords:
          "\u300C\u6587\u66F8\u3092\u5171\u540C\u7DE8\u96C6\u300D\u300C\u30EC\u30D3\u30E5\u30FC\u3057\u3066\u300D",
        useCase:
          "\u30C9\u30AD\u30E5\u30E1\u30F3\u30C8\u306E\u5171\u540C\u7DE8\u96C6\u30FB\u30EC\u30D3\u30E5\u30FC\u30EF\u30FC\u30AF\u30D5\u30ED\u30FC",
        features:
          "\u30C9\u30AD\u30E5\u30E1\u30F3\u30C8\u306E\u5171\u540C\u7DE8\u96C6\u30FB\u30EC\u30D3\u30E5\u30FC\u30EF\u30FC\u30AF\u30D5\u30ED\u30FC\u3092\u652F\u63F4\u3002\u30D5\u30A3\u30FC\u30C9\u30D0\u30C3\u30AF\u306E\u69CB\u9020\u5316\u3068\u53CD\u6620\u3002",
      },
      {
        name: "Internal Comms",
        keywords:
          "\u300C\u793E\u5185\u5411\u3051\u544A\u77E5\u3092\u300D\u300C\u793E\u5185\u6587\u66F8\u3092\u4F5C\u6210\u300D",
        useCase:
          "\u793E\u5185\u30B3\u30DF\u30E5\u30CB\u30B1\u30FC\u30B7\u30E7\u30F3\u6587\u66F8\uFF08\u544A\u77E5\u3001\u5831\u544A\u66F8\u3001\u30CB\u30E5\u30FC\u30B9\u30EC\u30BF\u30FC\u7B49\uFF09\u306E\u4F5C\u6210",
        features:
          "\u793E\u5185\u30B3\u30DF\u30E5\u30CB\u30B1\u30FC\u30B7\u30E7\u30F3\u6587\u66F8\uFF08\u544A\u77E5\u3001\u5831\u544A\u66F8\u3001\u30CB\u30E5\u30FC\u30B9\u30EC\u30BF\u30FC\u7B49\uFF09\u306E\u4F5C\u6210\u652F\u63F4\u3002",
      },
    ],
  },
  {
    title: "\u5C02\u9580\u77E5\u8B58 (Domain Knowledge)",
    description:
      "\u7279\u5B9A\u306E\u5C02\u9580\u9818\u57DF\u306B\u95A2\u3059\u308B\u6DF1\u3044\u6D1E\u5BDF\u3092\u63D0\u4F9B\u3057\u307E\u3059\u3002",
    skills: [
      {
        name: "\u4E2D\u5C0F\u4F01\u696D\u8A3A\u65AD\u58EB (SME)",
        keywords:
          "\u300C\u7D4C\u55B6\u5206\u6790\u3057\u3066\u300D\u300C\u4E8B\u696D\u6226\u7565\u3092\u76F8\u8AC7\u300D",
        useCase:
          "\u8CA1\u52D9\u8A3A\u65AD\u3001SWOT\u5206\u6790\u3001\u4E8B\u696D\u627F\u7D99\u3084M&A\u306B\u95A2\u3059\u308B\u5C02\u9580\u7684\u30A2\u30C9\u30D0\u30A4\u30B9",
        features:
          "\u6C7A\u7B97\u66F8\u304B\u3089\u306E\u8CA1\u52D9\u8A3A\u65AD\u3001SWOT\u5206\u6790\u3001PPM\u3001\u4E8B\u696D\u627F\u7D99\u3084M&A\u3001PMI\u306B\u95A2\u3059\u308B\u5C02\u9580\u7684\u306A\u30A2\u30C9\u30D0\u30A4\u30B9\u3002",
      },
      {
        name: "\u8FB2\u696D\u30CA\u30EC\u30C3\u30B8",
        keywords:
          "\u300C\u30B9\u30DE\u30FC\u30C8\u8FB2\u696D\u306B\u3064\u3044\u3066\u300D\u300C\u8FB2\u5730\u96C6\u7D04\u300D",
        useCase:
          "\u8FB2\u696D\u7D4C\u55B6\u306E\u8AB2\u984C\u89E3\u6C7A\u3001\u62C5\u3044\u624B\u4E0D\u8DB3\u5BFE\u7B56\u3001\u30A2\u30B0\u30EA\u30C6\u30C3\u30AF\u5C0E\u5165",
        features:
          "\u8FB2\u696D\u7D4C\u55B6\u306E\u8AB2\u984C\u89E3\u6C7A\u3001\u62C5\u3044\u624B\u4E0D\u8DB3\u5BFE\u7B56\u3001\u6700\u65B0\u306E\u30A2\u30B0\u30EA\u30C6\u30C3\u30AF\u5C0E\u5165\u306B\u95A2\u3059\u308B\u4E8B\u4F8B\u306B\u57FA\u3065\u3044\u305F\u77E5\u8B58\u63D0\u4F9B\u3002",
      },
    ],
  },
];

// ===== Document Builder =====
async function main() {
  const totalSkills = categories.reduce(
    (sum, cat) => sum + cat.skills.length,
    0,
  );

  // Summary table data
  const summaryColWidths = [4513, 4513];
  const summaryRows = [
    new TableRow({
      children: [
        headerCell("\u9805\u76EE", summaryColWidths[0]),
        headerCell("\u5024", summaryColWidths[1]),
      ],
    }),
    new TableRow({
      children: [
        dataCell("\u7DCF\u30B9\u30AD\u30EB\u6570", summaryColWidths[0], {
          bold: true,
        }),
        dataCell(String(totalSkills), summaryColWidths[1], { center: true }),
      ],
    }),
    new TableRow({
      children: [
        dataCell("\u30AB\u30C6\u30B4\u30EA\u6570", summaryColWidths[0], {
          bold: true,
          shading: COLORS.lightBg,
        }),
        dataCell(String(categories.length), summaryColWidths[1], {
          center: true,
          shading: COLORS.lightBg,
        }),
      ],
    }),
    ...categories.map(
      (cat, i) =>
        new TableRow({
          children: [
            dataCell(`  ${cat.title}`, summaryColWidths[0], {
              shading: i % 2 === 0 ? undefined : COLORS.lightBg,
            }),
            dataCell(String(cat.skills.length), summaryColWidths[1], {
              center: true,
              shading: i % 2 === 0 ? undefined : COLORS.lightBg,
            }),
          ],
        }),
    ),
  ];

  // Tips section
  const tips = [
    "\u8907\u6570\u3092\u7D44\u307F\u5408\u308F\u305B\u308B: \u300C\u8ABF\u67FB\u30B9\u30AD\u30EB\u3067\u8ABF\u3079\u3066\u3001Word\u30B9\u30AD\u30EB\u3067\u30EC\u30DD\u30FC\u30C8\u306B\u3057\u3066\u300D\u3068\u3044\u3063\u305F\u8907\u5408\u7684\u306A\u6307\u793A\u3082\u53EF\u80FD\u3067\u3059\u3002",
    "\u5177\u4F53\u7684\u306B\u6307\u793A\u3059\u308B: \u6307\u793A\u5185\u5BB9\u306B\u5177\u4F53\u7684\u306A\u76EE\u7684\u3092\u5165\u308C\u308B\u3068\u3001\u30A8\u30FC\u30B8\u30A7\u30F3\u30C8\u304C\u3088\u308A\u6700\u9069\u306A\u30B9\u30AD\u30EB\u3092\u9078\u629E\u3057\u307E\u3059\u3002",
    "\u308F\u304B\u3089\u306A\u3044\u6642\u306F\u805E\u304F: \u300C\u25CB\u25CB\u304C\u3067\u304D\u308B\u30B9\u30AD\u30EB\u306F\u3042\u308B\uFF1F\u300D\u3068\u805E\u3051\u3070\u3001\u30A8\u30FC\u30B8\u30A7\u30F3\u30C8\u304C\u6700\u9069\u306A\u3082\u306E\u3092\u63D0\u6848\u3057\u307E\u3059\u3002",
  ];

  const doc = new Document({
    styles: {
      default: { document: { run: { font: "Arial", size: 22 } } },
      paragraphStyles: [
        {
          id: "Heading1",
          name: "Heading 1",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { size: 36, bold: true, font: "Arial", color: COLORS.primary },
          paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 },
        },
        {
          id: "Heading2",
          name: "Heading 2",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { size: 28, bold: true, font: "Arial", color: COLORS.accent },
          paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 },
        },
      ],
    },
    numbering: {
      config: [
        {
          reference: "bullet-list",
          levels: [
            {
              level: 0,
              format: LevelFormat.BULLET,
              text: "\u2022",
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 720, hanging: 360 } } },
            },
          ],
        },
      ],
    },
    sections: [
      {
        properties: {
          page: {
            size: { width: 11906, height: 16838 },
            margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
          },
        },
        headers: {
          default: new Header({
            children: [
              new Paragraph({
                alignment: AlignmentType.RIGHT,
                border: {
                  bottom: {
                    style: BorderStyle.SINGLE,
                    size: 4,
                    color: COLORS.accent,
                    space: 4,
                  },
                },
                children: [
                  new TextRun({
                    text: "\u30B9\u30AD\u30EB\u30AB\u30BF\u30ED\u30B0",
                    font: "Arial",
                    size: 16,
                    color: COLORS.subtext,
                    italics: true,
                  }),
                ],
              }),
            ],
          }),
        },
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                alignment: AlignmentType.CENTER,
                border: {
                  top: {
                    style: BorderStyle.SINGLE,
                    size: 2,
                    color: COLORS.border,
                    space: 4,
                  },
                },
                children: [
                  new TextRun({
                    text: "Page ",
                    font: "Arial",
                    size: 16,
                    color: COLORS.subtext,
                  }),
                  new TextRun({
                    children: [PageNumber.CURRENT],
                    font: "Arial",
                    size: 16,
                    color: COLORS.subtext,
                  }),
                ],
              }),
            ],
          }),
        },
        children: [
          // Title
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 80 },
            children: [
              new TextRun({
                text: "\u30B9\u30AD\u30EB\u30AB\u30BF\u30ED\u30B0",
                font: "Arial",
                size: 52,
                bold: true,
                color: COLORS.primary,
              }),
            ],
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 40 },
            children: [
              new TextRun({
                text: `Agent Skills \u4E00\u89A7 v${VERSION}`,
                font: "Arial",
                size: 24,
                color: COLORS.subtext,
              }),
            ],
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 600 },
            border: {
              bottom: {
                style: BorderStyle.SINGLE,
                size: 6,
                color: COLORS.accent,
                space: 8,
              },
            },
            children: [
              new TextRun({
                text: `\u4F5C\u6210\u65E5: ${CREATED_DATE}`,
                font: "Arial",
                size: 20,
                color: COLORS.subtext,
              }),
            ],
          }),

          // Overview
          new Paragraph({
            heading: HeadingLevel.HEADING_1,
            children: [new TextRun({ text: "\u6982\u8981" })],
          }),
          new Paragraph({
            spacing: { after: 200 },
            children: [
              new TextRun({
                text: "\u672C\u30C9\u30AD\u30E5\u30E1\u30F3\u30C8\u306F\u3001\u73FE\u5728\u5229\u7528\u53EF\u80FD\u306A\u5168\u30B9\u30AD\u30EB\u306E\u30AB\u30BF\u30ED\u30B0\u3067\u3059\u3002\u5404\u30B9\u30AD\u30EB\u306E\u547C\u3073\u51FA\u3057\u30AD\u30FC\u30EF\u30FC\u30C9\u3001\u30E6\u30FC\u30B9\u30B1\u30FC\u30B9\u3001\u6A5F\u80FD\u6982\u8981\u3092\u30AB\u30C6\u30B4\u30EA\u5225\u306B\u6574\u7406\u3057\u3066\u3044\u307E\u3059\u3002",
                font: "Arial",
                size: 22,
                color: COLORS.text,
              }),
            ],
          }),

          // Summary table
          new Table({
            width: { size: CONTENT_WIDTH, type: WidthType.DXA },
            columnWidths: summaryColWidths,
            rows: summaryRows,
          }),

          // Page break
          new Paragraph({ children: [new PageBreak()] }),

          // Category sections
          ...categories.flatMap((cat) => categorySection(cat)),

          // Tips section
          new Paragraph({
            heading: HeadingLevel.HEADING_1,
            children: [
              new TextRun({ text: "\u4F7F\u3044\u65B9\u306E\u30B3\u30C4" }),
            ],
          }),
          ...tips.map(
            (tip) =>
              new Paragraph({
                spacing: { after: 120 },
                numbering: { reference: "bullet-list", level: 0 },
                children: [
                  new TextRun({
                    text: tip,
                    font: "Arial",
                    size: 22,
                    color: COLORS.text,
                  }),
                ],
              }),
          ),
        ],
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(OUTPUT_PATH, buffer);
  console.log(`Created: ${OUTPUT_PATH}`);
  console.log(
    `Total: ${totalSkills} skills across ${categories.length} categories`,
  );
}

main().catch(console.error);
