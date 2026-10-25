# Witcut

**有目的地剪輯，忠於真實。**

將真實 UI 操作製作成清楚、有設計感、可驗證的產品展示影片。

[English](README.md) · [Skill 入口](skills/witcut/SKILL.md)

## 現在能做什麼？

此分支包含三種不同能力：

| 元件 | 已有能力 | 邊界 |
| --- | --- | --- |
| Agent skill | 規劃、錄製、剪輯決策、候選檔檢查與交接指引 | 使用 agent 原有且已授權的工具，不提供電腦存取權限 |
| Python planner | 共用產品展示／Podcast 轉影片 schema v2、來源到輸出時間、驗證與三項規劃產物 | 不讀取媒體、不判斷語意，也不認證製作就緒 |
| 可選 FFmpeg fixture adapter | 生成及重現一支明確標示的原創合成測試短片，含語音 | 不是真實 UI 錄影、通用剪輯器或 Podcast 改編；正常速度觀看與實際聆聽仍未驗收 |

自主編劇、媒體理解及通用剪輯仍是未來工作。[協作策略](skills/witcut/references/collaboration.md) 涵蓋可用模型／推理選擇及有限角色交接；最終仍須驗收觀眾理解。

## 五分鐘快速上手：純 Python

此流程使用 [Draft PR #1](https://github.com/focaxisdev/witcut/pull/1) 的 `planning-loop-v1`，不表示已合併至 `main`。需要 Python 3.9+ 與 POSIX shell；checkout 後不需要 pip 套件、FFmpeg、帳號憑證或媒體檔。

```sh
git clone --branch planning-loop-v1 --single-branch https://github.com/focaxisdev/witcut.git
cd witcut
python3 scripts/validate.py
work_dir=$(mktemp -d)
python3 skills/witcut/scripts/plan.py skills/witcut/examples/plans/product-demo.json --out "$work_dir/product-demo"
python3 skills/witcut/scripts/plan.py skills/witcut/examples/plans/podcast-to-video.json --out "$work_dir/podcast-to-video"
python3 - "$work_dir" <<'PYTHON'
import json
from pathlib import Path
import sys
for profile in ('product-demo', 'podcast-to-video'):
    folder = Path(sys.argv[1]) / profile
    assert {p.name for p in folder.iterdir()} == {'script.md', 'shot-plan.json', 'missing-materials.json'}
    shots = json.loads((folder / 'shot-plan.json').read_text())
    missing = json.loads((folder / 'missing-materials.json').read_text())
    assert shots['planning_only'] is True
    assert missing['production_ready'] is False and len(missing['items']) == 4
    print(profile, 'planning_only=True; production_ready=False; missing=4', folder)
PYTHON
```

輸入是兩份原創合成 JSON 計畫，不是真實錄影或私人電台內容。兩次 CLI 各會顯示 `PASS` 與 **4 項缺料**，並產生：

- `script.md`：供人閱讀的影音分鏡劇本。
- `shot-plan.json`：場景時間及證據映射，`planning_only: true`。
- `missing-materials.json`：尚缺錄音、畫面或來源檢查，`production_ready: false`。

缺料是範例的預期結果，不是快速上手失敗。`PASS` 僅代表規劃不變條件通過，不表示已產生影片或驗證語意、權利與品質。輸出目錄必須不存在；重跑時先重新執行 `mktemp`。格式見[規劃契約](skills/witcut/references/planning.md)。

## 核心原則

- 先理解真實功能：獨立模式不能被說成連續流程；手動操作不能被剪成自動完成。
- 每段 zoom 都要有目的，並檢查放大前、移動中、放大後的構圖。
- 解析度不等於 UI 大小；browser zoom、DPR、錄製與輸出解析度要分開處理。
- 時長服從理解，不為了湊一分鐘刪掉必要結果。
- 技術檢查、藝術判斷、音訊信號、實際聆聽、播放裝置與使用者驗收分開記錄。
- 尊重「只檢視，不改檔」和已凍結版本，不陷入無限打磨。
- 備份回讀成功不等於已在乾淨環境完整重建。

150%、4K、16:9、片長與配樂都是個案設定，不是強制規範。

## 使用

將完整 `skills/witcut` 資料夾放入 agent 支援的 skill 目錄；不支援自動發現的環境，可直接指定 `SKILL.md` 作為入口，並允許讀取相關 references。

範例：

> 使用 Witcut 檢視這支產品影片，特別檢查 zoom 是否幫助理解。只回報時間碼與問題，先不要改檔。

> 使用 Witcut 為這個產品規劃展示影片。先驗證各模式的關係，再做短版錄製測試。

## 開發與驗證

純 Python CI 只執行以下明確的套件／planner 範圍（Python 3.9+，標準函式庫）：

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -p 'test_validate.py' -v
python3 -m unittest discover -s tests -p 'test_plan.py' -v
```

Renderer 整合測試是獨立且可選的檢查：

```sh
python3 -m unittest discover -s tests -p 'test_render_fixture.py' -v
```

需具備[合成測試短片](skills/witcut/references/render-fixture.md)所列的 FFmpeg/libflite、FFprobe 與字型。請讀取實際 unittest 結果：缺依賴時顯示 `skipped`，不等於 renderer 驗收成功。純 Python CI 不執行也不認證 renderer；技術整合測試或抽樣 PNG 都不能證明已實際觀看、聆聽或通過觀眾驗收。

這些檢查涵蓋 frontmatter、本地 Markdown 檔案連結、必要結構及規劃 schema 不變條件（含反例與 CLI 輸出保護），無法確立藝術品質、隱私完整性、授權或 agent 行為。[情境檢查](tests/scenarios.md)提供行為驗收任務與證據要求。

## 發展方向：尚未完成的能力

1. 實際觀看與聆聽原創合成短片，再依已觀察失敗擴充。
2. 僅為已證實的製作需求擴充單一 fixture adapter；通用剪輯自動化仍未提供。
3. 超出固定 fixture 範圍、對應精確輸出產物的製作 QA。
4. 具可審查決策與明確批准邊界的 agent 輔助粗剪。
5. 以真實素材與人類驗收評估更廣泛的剪輯自動化。

自動化應保留觀眾理解與產品真實性，不以可播放檔案替代。

## 貢獻與授權

修改應指出具體製作失敗、可重用的決策及有限範圍的情境或測試；避免累積僵硬規則。勿提交私人帳號資料、錄影、憑證、未授權素材或機器專屬路徑。

目前尚未選定授權條款，也未宣告開源授權。第三方影片、音樂、字型或品牌素材未附帶；未來納入須另行確認來源與適用權利。
