# Advisor-Aware Research Meeting Coach

**把杂乱的研究进展，整理成导师能够做出决定的 meeting。**

[English](README.md) | [繁體中文](README.zh-TW.md)

![状态：early alpha](https://img.shields.io/badge/status-early%20alpha-f59e0b)
![版本：0.3.4-alpha](https://img.shields.io/badge/version-0.3.4--alpha-2563eb)
![许可：MIT](https://img.shields.io/badge/license-MIT-16a34a)
[![CI](https://github.com/niansia/research-meeting-coach/actions/workflows/ci.yml/badge.svg)](https://github.com/niansia/research-meeting-coach/actions/workflows/ci.yml)

你做了一周研究，但 meeting 前真正困难的通常不是“做幻灯片”，而是：

- 哪个结果真的值得讲？
- 哪个结论的证据还不够？
- 上周导师交代的事情是否被遗漏？
- 导师最可能从哪个推理缺口追问？
- 今天到底要请导师决定什么？

这个 Agent Skill 会在现有周报、原始笔记或 meeting 草稿之上增加一层 advisor-facing critique；它不会把证据不足的故事包装得更漂亮。

> Early alpha：deterministic integrity checks 已通过，但尚未证明导师偏好、学生学习成效、精确问题预测，或优于 strong generic prompt。

![从研究笔记到导师可回答的决策](research-meeting-coach/assets/readme-before-after.svg)

## 30 秒看懂差异

输入：

```text
baseline：72.3
compression setup：65.1
32-frame follow-up：约 70
上周导师要求的 early-frame control：只完成一半
草稿结论：“compression 会损害 accuracy”
```

输出不会直接接受这个因果结论，而会指出：

```text
观察：三个设置的数值不同。
证据边界：frame count 与 token budget 尚未控制，不能归因于 compression。
延续性：上周要求的 control 仍为 partial。
Critical gap：目前的 causal claim 不成立。
今天要问导师：equal-frame 与 equal-token-budget control 应先做哪一个？
```

## 立即试用

当前 checkout 可以直接把 `research-meeting-coach/` 目录交给支持 Agent Skills 的客户端，并使用：

```text
Use $research-meeting-coach on these notes and my previous-meeting record.
Prepare a 15-minute advisor meeting. Do not invent facts or completion.
Separate observations from interpretations, rank the reasoning gaps,
and end with one decision my advisor can answer.
```

一行安装：

```text
npx skills add niansia/research-meeting-coach --skill research-meeting-coach
```

这条命令已于 2026-08-28 从全新的临时 Git 项目连接公开 repository 实测成功。

完整可复现入口：[60-second demo](research-meeting-coach/examples/60-second-demo/README.md)。

## 为什么不直接使用通用 ChatGPT／Claude prompt？

Strong generic prompt 本身就很有用，本项目也明确承认它已经能够发现示例中的核心 confound。这个 Skill 的价值在于把较难稳定维持的行为变成可检查的契约：

| 通用 meeting prompt | Advisor-Aware |
|---|---|
| 整理内容与语气 | 找出影响导师决策的内容 |
| 容易把结果串成故事 | 拆分 observation／interpretation／hypothesis／proposal |
| 每周重新开始 | 保留上次 advisor action 及真实状态 |
| 生成可能的问题 | 按决策风险排列 reasoning gaps，不捏造概率 |
| 数字依赖模型自行维持 | 验证 output↔RMS；对 text-exact evidence 再把数值、单位、metric、condition、qualifier 与 citation 绑定回 quoted source |
| 容易猜测导师个性 | 只接受有记录行为支持的 personalization |

## 它会生成什么？

- meeting mission 与 30 秒 opener；
- evidence boundary 与未完成的 prior action；
- `Critical / High / Medium / Low` attack surface；
- 一个导师能够回答的 decision／ask；
- main／backup／omit 对话路径；
- `Changed / Why / Try next time` 新手 coaching；
- optional RMS JSON 与 deterministic validators。

## 实证状态

目前有 15 个 behavioral/adversarial case definitions、8 个 routing cases、1 个 longitudinal holdout definition，以及 15 条仅用于 taxonomy discovery 的公开回溯 seed。

正式 model-generated behavioral runs：0。Cross-model runs：0。具有知情同意、会前材料、冻结预测与会后问题记录的 paired cases：0。

因此目前可以声称的是“auditable advisor-facing critique layer”，不能声称“优于 generic prompt”或“能够预测导师”。下一个真正重要的里程碑是五个 permissioned、prospective paired meetings。

## 安全发布

不要直接压缩工作目录；`.gitignore` 无法保护 ZIP／RAR。只能使用：

```text
python -m pip install -r research-meeting-coach/requirements.txt
python research-meeting-coach/scripts/build_release.py --json
```

`validate_schema_contracts.py` 只验证 bundle 中的已知 fixtures。用户实际运行的 `validate_rms.py` 与 `validate_advisor_profile.py` 会先运行 published Draft 2020-12 schema，再运行额外语义规则；缺少 required field、加入 unexpected property 或缺少 `jsonschema` dependency 都会明确失败，不会只执行部分检查后显示 PASS。

`run_static_evals.py` 只要求 portable ZIP 内本来就应存在的文件。Git repository checkout 会另外运行 `python validate_repository.py --json`，检查 `.github` workflow、issue／PR 模板与 release checklist；这些 repository infrastructure 有意不放进 portable Skill ZIP，CI 会同时执行两层检查。

Builder 对 repository 与 Skill package 中未列出的顶层路径采用默认拒绝，并排除 local register、`.env`、private/confidential pilot 文件名、symbolic link、cache、bytecode 与嵌套压缩文件；完成 ZIP 后还会扫描 Dcard、Reddit、PTT、Threads、Facebook 的单篇帖子网址，以及常见 credential/private-key pattern。

但它不是通用 PII 检测器。通过 builder 不代表内容已经匿名、已取得同意或可以合法发布；仍须人工检查 staged files 与 manifest，而且只能使用合成案例或明确获得许可的案例。

完整技术验证、限制、prior art、贡献方式与安全政策请参阅 [English README](README.md)、[AUDIT_REPORT.md](AUDIT_REPORT.md)、[CONTRIBUTING.md](CONTRIBUTING.md) 与 [SECURITY.md](SECURITY.md)。

MIT License。
