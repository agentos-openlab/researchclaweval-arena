#!/usr/bin/env bash
# ============================================================================
# setup_datasets.sh — Download and prepare the public benchmark inputs
#
# This script downloads inputs from their published upstream sources and
# prepares them for local evaluation.
#
# Usage:
#   bash scripts/setup_datasets.sh                                    # Download all datasets
#   bash scripts/setup_datasets.sh --dataset arc_wbe_2026             # Download specific dataset
#   bash scripts/setup_datasets.sh --dir /path/to/datasets            # Custom output directory
# ============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()      { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }
header()  { echo -e "\n${CYAN}════════════════════════════════════════════${NC}"; echo -e "${CYAN}  $*${NC}"; echo -e "${CYAN}════════════════════════════════════════════${NC}"; }

# ---- Parse arguments ----
DATASET=""
DATA_DIR="$ROOT/data"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dataset) DATASET="$2"; shift 2 ;;
    --dir) DATA_DIR="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: bash scripts/setup_datasets.sh [--dataset ID] [--dir PATH]"
      echo "Topics: babylm mountaincar_continuous arc_wbe_2026 psydefdetect tdc_admet_tox"
      exit 0 ;;
    *) error "Unknown option: $1"; exit 1 ;;
  esac
done

mkdir -p "$DATA_DIR"
DATA_DIR="$(cd "$DATA_DIR" && pwd)"

# ============================================================================
# ARC-WBE-2026 (public, from AIcrowd via HuggingFace)
# ============================================================================
download_arc_wbe_2026() (
  header "ARC-WBE-2026 Dataset"
  local target="$DATA_DIR/arc_white_box_estimation_2026"
  if [[ -f "$target/split_manifest.json" ]]; then
    python3 "$ROOT/scoring/prepare_public_topic_data.py" --check-cache arc_wbe_2026 --root "$target"
  else
    command -v uv >/dev/null || { error "ARC dataset preparation requires uv"; return 1; }
    python3 "$ROOT/scoring/prepare_public_topic_data.py" --topic arc_wbe_2026 --root "$target"
    local staging
    staging="$(mktemp -d "$target/.split-build.XXXXXXXX")"
    trap 'rm -rf -- "$staging"' EXIT
    uv run --no-project --with pyarrow==20.0.0 python "$ROOT/scoring/make_arc_wbe_2026_visible_validation.py" \
      --source-root "$target" --output-root "$staging"
    for part in visible-validation scoring split_manifest.json; do
      [[ ! -e "$target/$part" ]] || { error "Partial ARC split already exists: $target/$part"; return 1; }
    done
    for part in visible-validation scoring split_manifest.json; do
      mv -- "$staging/$part" "$target/$part"
    done
    python3 "$ROOT/scoring/prepare_public_topic_data.py" --check-cache arc_wbe_2026 --root "$target"
  fi
  ok "ARC-WBE-2026 visible validation and scoring splits are ready"
  echo "  export ARC_WBE_2026_DATASET_ROOT=$target"
)

# ============================================================================
# BabyLM-10M and MountainCar-Continuous
# ============================================================================
download_babylm() {
  header "BabyLM-10M Dataset"
  local target="$DATA_DIR/babylm"
  python3 "$ROOT/scoring/prepare_public_topic_data.py" --topic babylm --root "$target"
  echo "  export BABYLM_DATASET_ROOT=$target"
}

download_mountaincar_continuous() {
  header "MountainCar-Continuous Starter and Evaluator"
  local target="$DATA_DIR/mountaincar_continuous"
  python3 "$ROOT/scoring/prepare_public_topic_data.py" --topic mountaincar_continuous --root "$target"
  echo "  export MOUNTAINCAR_CONTINUOUS_DATASET_ROOT=$target"
}

# ============================================================================
# PsyDefDetect (public — HuggingFace AIMH/PsyDefConv, cc-by-nc-4.0)
# ============================================================================
# 单一公开文件。校验 sha256 后才接受，因为整套评测都建在这份数据上。
PSYDEF_FILE_SHA256="88d55e1ae6f4653661baa795166ef103f5439f4d6720b1767c3be7bbc3904ad7"
PSYDEF_FILE_SIZE=5376380
download_psydefdetect() {
  header "PsyDefDetect Dataset"
  local dest="$DATA_DIR/psydefdetect"
  local out="$dest/PsyDefConv.json"
  mkdir -p "$dest"
  if [[ -f "$out" ]] && [[ "$(sha256sum "$out" | cut -d' ' -f1)" == "$PSYDEF_FILE_SHA256" ]]; then
    ok "Using the verified PsyDefDetect cache"
    echo "  export PSYDEFDETECT_DATASET_ROOT=$dest"
    return 0
  fi

  # 直连 huggingface.co 在部分网络下不可达（或被 DNS 污染），
  # 因此依次尝试：显式 HF_ENDPOINT → 官方 → 镜像。
  local endpoints=()
  [[ -n "${HF_ENDPOINT:-}" ]] && endpoints+=("${HF_ENDPOINT%/}")
  endpoints+=("https://huggingface.co" "https://hf-mirror.com")

  local got=0
  for ep in "${endpoints[@]}"; do
    info "尝试 $ep"
    if curl -fsSL --retry 2 --connect-timeout 15 --max-time 300 \
         -o "$out.part" \
         "$ep/datasets/AIMH/PsyDefConv/resolve/main/PsyDefConv.json" 2>/dev/null; then
      if [[ "$(sha256sum "$out.part" | cut -d' ' -f1)" == "$PSYDEF_FILE_SHA256" ]]; then
        mv "$out.part" "$out"; got=1; break
      fi
      warn "sha256 不符，换个源重试"
      rm -f "$out.part"
    fi
  done

  if [[ "$got" != "1" ]]; then
    rm -f "$out.part"
    error "PsyDefDetect 下载失败。请手动获取后放置："
    echo "  $out"
    echo "  期望 sha256: $PSYDEF_FILE_SHA256"
    echo "  期望大小  : $PSYDEF_FILE_SIZE 字节"
    echo "  许可      : cc-by-nc-4.0（非商业）—— 使用前确认用途合规"
    echo "  然后：export PSYDEFDETECT_DATASET_ROOT=$dest"
    return 1
  fi

  ok "PsyDefConv.json  sha256 校验通过  ($(stat -c%s "$out") 字节)"
  echo "  export PSYDEFDETECT_DATASET_ROOT=$dest"
  echo ""
  echo "  注：该数据集的官方切分为记录级，同一对话的话语会跨 train/test。"
  echo "      评测采用的对话级无泄漏切分已冻结，其 canonical sha256 见"
  echo "      docs/rules.md（Split Freeze 一节）。"
  echo ""
}

# ============================================================================
# TDC-ADMET-Tox (public — Harvard Dataverse, doi:10.7910/DVN/21LKWG)
# ============================================================================
# 归档含 22 个 ADMET endpoint；本评测使用 AMES / hERG / DILI。
# 归档里每个 endpoint 有两份带标签文件：
#   train_val.csv  → 按冻结划分拆成 train / validation
#   test.csv       → 写入 public/ 时移除标签；归档原始标签留在主机缓存
TDC_ARCHIVE_MD5="e3e4dda2f7f62268448fc813ceefccd5"
TDC_ARCHIVE_SHA256="bd0005246cb6f1672333c28ad202112a8bf071ab65d847848715030308faf1f1"
TDC_ARCHIVE_BYTES=1472501
TDC_DATAVERSE_FILE_ID=4426004
download_tdc_admet_tox() {
  header "TDC-ADMET-Tox Dataset"
  local dest="$DATA_DIR/tdc_admet_tox"
  local cache="$dest/.cache"
  local zip="$cache/admet_group.zip"
  if [[ -d "$dest/public" ]]; then
    python3 "$ROOT/scoring/prepare_public_topic_data.py" --check-cache tdc_admet_tox --root "$dest/public"
    ok "Using the verified TDC-ADMET-Tox public dataset"
    echo "  export TDC_ADMET_TOX_DATASET_ROOT=$dest/public"
    return 0
  fi
  mkdir -p "$cache"

  if [[ ! -f "$zip" ]] || [[ "$(sha256sum "$zip" 2>/dev/null | cut -d' ' -f1)" != "$TDC_ARCHIVE_SHA256" ]]; then
    info "从 Harvard Dataverse 下载 admet_group.zip"
    if ! curl -fsSL --retry 2 --connect-timeout 20 --max-time 600 -o "$zip.part" \
         "https://dataverse.harvard.edu/api/access/datafile/$TDC_DATAVERSE_FILE_ID"; then
      error "下载失败。手动获取："
      echo "  https://doi.org/10.7910/DVN/21LKWG  (V105, admet_group.zip)"
      echo "  MD5    : $TDC_ARCHIVE_MD5"
      echo "  SHA256 : $TDC_ARCHIVE_SHA256"
      echo "  放到  : $zip"
      return 1
    fi
    mv "$zip.part" "$zip"
  fi

  local actual_sha actual_size
  actual_sha="$(sha256sum "$zip" | cut -d' ' -f1)"
  actual_size="$(stat -c%s "$zip")"
  if [[ "$actual_sha" != "$TDC_ARCHIVE_SHA256" ]] || [[ "$actual_size" != "$TDC_ARCHIVE_BYTES" ]]; then
    error "归档校验失败：期望 $TDC_ARCHIVE_SHA256 ($TDC_ARCHIVE_BYTES B)，实际 $actual_sha ($actual_size B)"
    return 1
  fi
  ok "admet_group.zip  sha256 + 大小校验通过"

  # 解出三个 endpoint 的原始文件。转换与划分由 python 脚本负责，
  # 这里只保证拿到的是逐字节正确的归档。
  info "解压 AMES / hERG / DILI"
  local raw="$cache/raw"
  rm -rf "$raw"; mkdir -p "$raw"
  unzip -q -o "$zip" "admet_group/ames/*" "admet_group/herg/*" "admet_group/dili/*" -d "$raw"

  python3 "$ROOT/scoring/prepare_tdc_admet_tox_from_archive.py" \
    --raw-root "$raw/admet_group" \
    --output-root "$dest"

  ok "已生成 $dest/public/{train,validation,test}.csv"
  echo "  export TDC_ADMET_TOX_DATASET_ROOT=$dest/public"
  echo ""
  echo "  注：public/test.csv 不含标签；原始测试标签保留在主机缓存，不会挂载到框架容器。"
  echo ""
}

# ============================================================================
# Main
# ============================================================================
header "Dataset Setup"

if [[ -n "$DATASET" ]]; then
  case "$DATASET" in
    babylm) download_babylm ;;
    mountaincar_continuous) download_mountaincar_continuous ;;
    arc_wbe_2026) download_arc_wbe_2026 ;;
    psydefdetect) download_psydefdetect ;;
    tdc_admet_tox) download_tdc_admet_tox ;;
    *) error "Unknown dataset: $DATASET"; exit 1 ;;
  esac
else
  download_babylm
  download_mountaincar_continuous
  download_arc_wbe_2026
  download_psydefdetect
  download_tdc_admet_tox
fi

echo ""
ok "Dataset setup complete"
echo ""
echo "Don't forget to set the corresponding environment variables:"
echo "  export ARC_WBE_2026_DATASET_ROOT=$DATA_DIR/arc_white_box_estimation_2026"
echo "  export PSYDEFDETECT_DATASET_ROOT=$DATA_DIR/psydefdetect"
echo "  export TDC_ADMET_TOX_DATASET_ROOT=$DATA_DIR/tdc_admet_tox/public"
echo "  export BABYLM_DATASET_ROOT=$DATA_DIR/babylm"
echo "  export MOUNTAINCAR_CONTINUOUS_DATASET_ROOT=$DATA_DIR/mountaincar_continuous"
