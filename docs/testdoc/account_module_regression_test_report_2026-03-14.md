# 账户模块回归测试报告（修复后复测）

## 1. 背景与目标
根据上一版测试报告中提出的缺陷（`PATCH /accounts/{account_id}` 可写入空白 `api_key/api_secret`），对已修复版本进行复测，确认：
1. 修复代码已落地；
2. 不会再允许空白凭据通过更新入口写入；
3. 输出最新测试结论与后续建议。

## 2. 本次测试环境
- 仓库路径：`/workspace/auto_trader`
- 执行时间：2026-03-14
- Python：`3.10.19`

## 3. 测试执行记录

### 3.1 依赖安装尝试（端到端前置）
- 命令：`python -m pip install -r backend/requirements.txt`
- 结果：失败。
- 失败信息（摘要）：`ProxyError ... 403 Forbidden`，最终 `No matching distribution found for fastapi`。
- 结论：当前容器仍无法拉取 `fastapi` 等依赖，导致无法启动 FastAPI 服务，无法完成真实 HTTP 端到端联调。

### 3.2 运行依赖可用性检查
- 命令：
  ```bash
  cd backend && python - <<'PY'
  try:
      import fastapi
      print('fastapi installed')
  except Exception as e:
      print(type(e).__name__, e)
  PY
  ```
- 结果：`ModuleNotFoundError No module named 'fastapi'`。

### 3.3 语法与编译检查
- 命令：
  ```bash
  python -m py_compile \
    backend/app/api/accounts.py \
    backend/app/api/deps.py \
    backend/app/schemas/__init__.py \
    backend/app/api/trade.py
  ```
- 结果：通过。

### 3.4 修复点存在性检查（静态）
- 命令：读取 `backend/app/api/accounts.py` 并断言以下逻辑存在：
  - 遍历 `("api_key", "api_secret")`
  - 对 `None/空白` 做拒绝
  - 对有效值做 `strip()` 后再写入
- 结果：通过（输出：`validation guards present`）。

## 4. 缺陷复测结论

### BUG-01：更新接口允许空白 API 凭据
- 状态：**代码层面已修复（通过静态复核）**。
- 修复要点：
  - 更新接口在 `api_key/api_secret` 出现在请求体时，拒绝 `None`、空串、纯空白串（422）；
  - 对合法值执行 `strip()` 后再入库；
  - `passphrase` 也新增了字符串清洗。
- 备注：受环境依赖限制，本次仍无法执行真实 HTTP 请求验证状态码与响应体。

## 5. 风险与建议
1. **当前剩余风险**：未完成真实 API 联调（注册/登录/创建账户/更新账户/交易前置校验）前，仍存在“运行时行为与静态分析不一致”的低概率风险。
2. **建议的提测前动作**：
   - 在可联网环境或可用私有镜像环境安装依赖后，执行一次人工 API 全链路回归：
     - 用户 A 注册/登录
     - 创建账户（合法凭据）
     - 更新账户为纯空格 `api_key`（预期 422）
     - 更新账户为纯空格 `api_secret`（预期 422）
     - 更新账户为带前后空格凭据（预期成功并被裁剪）
     - 跨用户访问（预期 404）

## 6. 本次交付物
- 本报告：`docs/testdoc/account_module_regression_test_report_2026-03-14.md`
